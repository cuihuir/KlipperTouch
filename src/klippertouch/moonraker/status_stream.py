import json
from typing import Any

from PySide6.QtCore import QObject, QTimer, QUrl, Slot
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtWebSockets import QWebSocket

from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.qt_models.status_model import StatusModel

SUBSCRIPTION_ID = 1
TEMPERATURE_FIELDS = ["temperature", "target"]
PRINT_STATUS_FIELDS = {
    "print_stats": [
        "state",
        "filename",
        "print_duration",
        "total_duration",
        "filament_used",
        "info",
    ],
    "display_status": ["progress", "message"],
    "virtual_sdcard": ["progress", "is_active", "file_path"],
}
TOOLHEAD_STATUS_FIELDS = {
    "toolhead": ["position", "homed_axes", "max_accel", "max_velocity"],
    "gcode_move": [
        "gcode_position",
        "homing_origin",
        "speed",
        "speed_factor",
        "extrude_factor",
    ],
}
EXCLUDE_OBJECT_STATUS_FIELDS = {
    "exclude_object": ["objects", "excluded_objects", "current_object"],
}


def build_websocket_request(client: MoonrakerClient) -> QNetworkRequest:
    request = QNetworkRequest(QUrl(client.websocket_endpoint))
    if client.config.moonraker_api_key:
        request.setRawHeader(b"x-api-key", client.config.moonraker_api_key.encode())
    return request


def build_temperature_subscription_message(
    client: MoonrakerClient,
    status: PrinterStatus,
) -> str:
    client.policy.validate_jsonrpc("printer.objects.subscribe")
    return json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "printer.objects.subscribe",
            "params": {"objects": _subscription_objects(status)},
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
    return current_status.with_status_update(update)


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
        reconnect_interval_ms: int = 2000,
    ) -> None:
        super().__init__()
        self._client = client
        self._status_model = status_model
        self._status = initial_status
        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.setSingleShot(True)
        self._reconnect_timer.setInterval(reconnect_interval_ms)
        self._reconnect_timer.timeout.connect(self.start)
        self._socket = QWebSocket()
        self._socket.connected.connect(self._send_subscription)
        self._socket.connected.connect(self._reconnect_timer.stop)
        self._socket.disconnected.connect(self._schedule_reconnect)
        self._socket.errorOccurred.connect(self._schedule_reconnect)
        self._socket.textMessageReceived.connect(self._handle_text_message)

    def start(self) -> None:
        if not _subscription_objects(self._status):
            return
        self._socket.open(build_websocket_request(self._client))

    def _schedule_reconnect(self, *_args: object) -> None:
        if not _subscription_objects(self._status) or self._reconnect_timer.isActive():
            return
        self._reconnect_timer.start()

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


def _subscription_objects(status: PrinterStatus) -> dict[str, list[str]]:
    objects = {device.name: TEMPERATURE_FIELDS for device in status.temperature_devices}
    objects.update(
        {
            name: fields
            for name, fields in (
                PRINT_STATUS_FIELDS | TOOLHEAD_STATUS_FIELDS | EXCLUDE_OBJECT_STATUS_FIELDS
            ).items()
            if name in status.objects
        }
    )
    return objects
