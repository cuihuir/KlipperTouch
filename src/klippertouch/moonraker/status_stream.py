import json
from typing import Any

from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtWebSockets import QWebSocket

from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.probe import build_status_from_client
from klippertouch.qt_models.status_model import StatusModel

SUBSCRIPTION_ID = 1
TEMPERATURE_FIELDS = ["temperature", "target"]
EXTRUDER_FIELDS = ["temperature", "target", "pressure_advance", "smooth_time"]
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
WEBHOOKS_STATUS_FIELDS = {
    "webhooks": ["state", "state_message"],
}
FILAMENT_SENSOR_FIELDS = ["enabled", "filament_detected"]


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


def gcode_response_from_websocket_message(message: str) -> str:
    try:
        payload = json.loads(message)
    except json.JSONDecodeError:
        return ""

    if not isinstance(payload, dict) or payload.get("method") != "notify_gcode_response":
        return ""
    params = payload.get("params")
    if isinstance(params, list) and params:
        return str(params[0]).strip()
    if isinstance(params, str):
        return params.strip()
    return ""


def status_needs_recovery_polling(status: PrinterStatus) -> bool:
    if status.moonraker_version in {"", "unknown"}:
        return True
    if status.webhooks_state and status.webhooks_state != "ready":
        return True
    return status.klippy_state != "ready"


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
    gcodeResponseReceived = Signal(str)

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
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(reconnect_interval_ms)
        self._poll_timer.timeout.connect(self._poll_until_ready)
        self._socket = QWebSocket()
        self._socket.connected.connect(self._send_subscription)
        self._socket.connected.connect(self._reconnect_timer.stop)
        self._socket.connected.connect(self._poll_timer.stop)
        self._socket.disconnected.connect(self._schedule_reconnect)
        self._socket.errorOccurred.connect(self._schedule_reconnect)
        self._socket.textMessageReceived.connect(self._handle_text_message)

    def start(self) -> None:
        if not _subscription_objects(self._status):
            return
        if status_needs_recovery_polling(self._status):
            if not self._poll_timer.isActive():
                self._poll_timer.start()
                self._poll_until_ready()
            return
        self._socket.open(build_websocket_request(self._client))

    def _schedule_reconnect(self, *_args: object) -> None:
        if not _subscription_objects(self._status) or self._poll_timer.isActive():
            return
        self._set_webhooks_state("disconnected", "Moonraker disconnected")
        self._poll_timer.start()
        self._poll_until_ready()

    @Slot()
    def _send_subscription(self) -> None:
        self._set_webhooks_state("startup", "Klipper is attempting to start")
        self._socket.sendTextMessage(
            build_temperature_subscription_message(self._client, self._status)
        )

    @Slot(str)
    def _handle_text_message(self, message: str) -> None:
        gcode_response = gcode_response_from_websocket_message(message)
        if gcode_response:
            self.gcodeResponseReceived.emit(gcode_response)
        status = status_from_websocket_message(self._status, message)
        if status is None:
            return
        self._status = status
        self._status_model.set_status(status)
        if status_needs_recovery_polling(status) and not self._poll_timer.isActive():
            self._poll_timer.start()
            self._poll_until_ready()

    def _set_webhooks_state(self, state: str, message: str) -> None:
        if "webhooks" not in self._status.objects:
            return
        status = self._status.with_status_update(
            {"webhooks": {"state": state, "state_message": message}}
        )
        if status == self._status:
            return
        self._status = status
        self._status_model.set_status(status)

    @Slot()
    def _poll_until_ready(self) -> None:
        try:
            status = build_status_from_client(self._client)
        except Exception:
            self._set_webhooks_state("disconnected", "Moonraker disconnected")
            return
        if not status.objects:
            self._set_webhooks_state("disconnected", "Moonraker disconnected")
            return
        self._status = status
        self._status_model.set_status(status)
        if status.klippy_state == "ready" and status.webhooks_state == "ready":
            self._poll_timer.stop()
            self.start()


def _subscription_objects(status: PrinterStatus) -> dict[str, list[str]]:
    objects = {
        device.name: _temperature_subscription_fields(device.name)
        for device in status.temperature_devices
    }
    objects.update(
        {
            name: fields
            for name, fields in (
                PRINT_STATUS_FIELDS
                | TOOLHEAD_STATUS_FIELDS
                | EXCLUDE_OBJECT_STATUS_FIELDS
                | WEBHOOKS_STATUS_FIELDS
            ).items()
            if name in status.objects
        }
    )
    objects.update(
        {
            name: FILAMENT_SENSOR_FIELDS
            for name in status.objects
            if name.startswith(("filament_switch_sensor ", "filament_motion_sensor "))
        }
    )
    return objects


def _temperature_subscription_fields(device_name: str) -> list[str]:
    if device_name == "extruder":
        return EXTRUDER_FIELDS
    return TEMPERATURE_FIELDS
