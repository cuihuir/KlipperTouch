import json
from typing import Any

from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtWebSockets import QWebSocket

from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.qt_models.status_model import StatusModel

SUBSCRIPTION_ID = 1
TEMPERATURE_FIELDS = ["temperature", "target"]


def build_temperature_subscription_message(
    client: MoonrakerClient,
    status: PrinterStatus,
) -> str:
    client.policy.validate_jsonrpc("printer.objects.subscribe")
    objects = {
        device.name: TEMPERATURE_FIELDS
        for device in status.temperature_devices
    }
    return json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "printer.objects.subscribe",
            "params": {"objects": objects},
            "id": SUBSCRIPTION_ID,
        }
    )


def status_from_websocket_message(
    current_status: PrinterStatus,
    message: str,
) -> PrinterStatus | None:
    try:
        payload = json.loads(message)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    update = _status_update_from_payload(payload)
    if update is None:
        return None
    return current_status.with_temperature_status_update(update)


def _status_update_from_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    method = payload.get("method")
    if method == "notify_status_update":
        params = payload.get("params")
        if isinstance(params, list) and params and isinstance(params[0], dict):
            return params[0]
        return None

    result = payload.get("result")
    if isinstance(result, dict):
        status = result.get("status")
        if isinstance(status, dict):
            return status
    return None


class MoonrakerStatusStream(QObject):
    def __init__(
        self,
        client: MoonrakerClient,
        status_model: StatusModel,
        initial_status: PrinterStatus,
    ) -> None:
        super().__init__()
        self._client = client
        self._status_model = status_model
        self._status = initial_status
        self._socket = QWebSocket()
        self._socket.connected.connect(self._send_subscription)
        self._socket.textMessageReceived.connect(self._handle_text_message)

    def start(self) -> None:
        if not self._status.temperature_devices:
            return
        self._socket.open(QUrl(self._client.websocket_endpoint))

    @Slot()
    def _send_subscription(self) -> None:
        self._socket.sendTextMessage(
            build_temperature_subscription_message(self._client, self._status)
        )

    @Slot(str)
    def _handle_text_message(self, message: str) -> None:
        status = status_from_websocket_message(self._status, message)
        if status is None:
            return
        self._status = status
        self._status_model.set_status(status)
