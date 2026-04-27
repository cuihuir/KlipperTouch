import json
from pathlib import Path

from klippertouch.config.models import PrinterConfig
from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.status_stream import (
    build_temperature_subscription_message,
    build_websocket_request,
    status_from_websocket_message,
    status_needs_recovery_polling,
)


def test_build_temperature_subscription_message_uses_read_only_objects_method() -> None:
    status = PrinterStatus(
        objects=(
            "extruder",
            "heater_bed",
            "fan",
            "print_stats",
            "display_status",
            "toolhead",
            "gcode_move",
            "exclude_object",
            "webhooks",
        )
    )
    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    message = json.loads(build_temperature_subscription_message(client, status))

    assert message == {
        "jsonrpc": "2.0",
        "method": "printer.objects.subscribe",
        "params": {
            "objects": {
                "extruder": ["temperature", "target"],
                "heater_bed": ["temperature", "target"],
                "print_stats": [
                    "state",
                    "filename",
                    "print_duration",
                    "total_duration",
                    "filament_used",
                    "info",
                ],
                "display_status": ["progress", "message"],
                "exclude_object": ["objects", "excluded_objects", "current_object"],
                "webhooks": ["state", "state_message"],
                "toolhead": ["position", "homed_axes", "max_accel", "max_velocity"],
                "gcode_move": [
                    "gcode_position",
                    "homing_origin",
                    "speed",
                    "speed_factor",
                    "extrude_factor",
                ],
            }
        },
        "id": 1,
    }


def test_build_websocket_request_includes_optional_api_key() -> None:
    client = MoonrakerClient(
        PrinterConfig(
            name="p",
            moonraker_host="host",
            moonraker_api_key="secret",
        )
    )

    request = build_websocket_request(client)

    assert request.url().toString() == "ws://host:7125/websocket"
    assert bytes(request.rawHeader("x-api-key")).decode() == "secret"


def test_status_stream_schedules_read_only_reconnects() -> None:
    source = Path("src/klippertouch/moonraker/status_stream.py").read_text(encoding="utf-8")

    assert "QTimer" in source
    assert "reconnect_interval_ms: int = 2000" in source
    assert "self._reconnect_timer.setSingleShot(True)" in source
    assert "self._socket.disconnected.connect(self._schedule_reconnect)" in source
    assert "self._socket.errorOccurred.connect(self._schedule_reconnect)" in source
    assert "self._socket.connected.connect(self._reconnect_timer.stop)" in source
    assert "self._socket.connected.connect(self._poll_timer.stop)" in source
    assert "self._reconnect_timer.timeout.connect(self.start)" in source
    assert "self._poll_timer.setInterval(reconnect_interval_ms)" in source
    assert "self._poll_timer.timeout.connect(self._poll_until_ready)" in source
    assert "self._poll_until_ready()" in source
    assert "if status_needs_recovery_polling(self._status)" in source
    assert "return" in source
    assert "if status_needs_recovery_polling(status)" in source
    assert "build_status_from_client(self._client)" in source
    assert "if status.klippy_state == \"ready\" and status.webhooks_state == \"ready\":" in source
    assert "self._poll_timer.stop()" in source
    assert "self.start()" in source
    assert "printer.objects.subscribe" in source
    assert "printer.gcode.script" not in source
    assert '_set_webhooks_state("disconnected", "Moonraker disconnected")' in source
    assert '_set_webhooks_state("startup", "Klipper is attempting to start")' in source


def test_status_needs_recovery_polling_for_klippy_faults() -> None:
    assert status_needs_recovery_polling(
        PrinterStatus(
            klippy_state="shutdown",
            moonraker_version="v0.10.0",
            webhooks_state="shutdown",
        )
    )
    assert status_needs_recovery_polling(
        PrinterStatus(
            klippy_state="ready",
            moonraker_version="v0.10.0",
            webhooks_state="startup",
        )
    )
    assert not status_needs_recovery_polling(
        PrinterStatus(
            klippy_state="ready",
            moonraker_version="v0.10.0",
            webhooks_state="ready",
        )
    )


def test_status_from_websocket_message_applies_notification_temperature_delta() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["extruder", "heater_bed"]},
        object_status={
            "status": {
                "extruder": {"temperature": 24.3, "target": 0.0},
                "heater_bed": {"temperature": 26.7, "target": 60.0},
            }
        },
    )
    message = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "notify_status_update",
            "params": [{"extruder": {"temperature": 25.1}}],
        }
    )

    updated = status_from_websocket_message(status, message)

    assert updated is not None
    assert tuple(device.temperature for device in updated.temperature_devices) == (25.1, 26.7)
    assert tuple(device.target for device in updated.temperature_devices) == (0.0, 60.0)


def test_status_from_websocket_message_recovers_from_webhooks_shutdown() -> None:
    status = PrinterStatus(
        klippy_state="shutdown",
        moonraker_version="v0.10.0",
        objects=("webhooks",),
        webhooks_state="shutdown",
        webhooks_message="Shutdown due to webhooks request",
    )
    message = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "notify_status_update",
            "params": [{"webhooks": {"state": "ready"}}],
        }
    )

    updated = status_from_websocket_message(status, message)

    assert updated is not None
    assert updated.klippy_state == "ready"
    assert updated.webhooks_state == "ready"
    assert updated.webhooks_message == "Printer is ready"


def test_status_from_websocket_message_applies_subscription_snapshot() -> None:
    status = PrinterStatus(
        objects=(
            "extruder",
            "heater_bed",
            "print_stats",
            "display_status",
            "gcode_move",
            "exclude_object",
        )
    )
    message = json.dumps(
        {
            "jsonrpc": "2.0",
            "result": {
                "status": {
                    "extruder": {"temperature": 24.3, "target": 0.0},
                    "heater_bed": {"temperature": 26.7, "target": 60.0},
                    "print_stats": {
                        "state": "printing",
                        "filename": "cube.gcode",
                        "filament_used": 3456.7,
                        "info": {"current_layer": 5, "total_layer": 30},
                    },
                    "display_status": {"progress": 0.25},
                    "toolhead": {"max_accel": 3000.0, "max_velocity": 250.0},
                    "gcode_move": {
                        "gcode_position": [1.1, 2.2, 3.3, 4.4],
                        "speed": 7500.0,
                        "speed_factor": 1.5,
                        "extrude_factor": 0.95,
                        "homing_origin": [0.0, 0.0, -0.04],
                    },
                    "exclude_object": {
                        "objects": [{"name": "part_a"}, {"name": "part_b"}],
                        "excluded_objects": ["part_a"],
                        "current_object": "part_b",
                    },
                }
            },
            "id": 1,
        }
    )

    updated = status_from_websocket_message(status, message)

    assert updated is not None
    assert tuple(device.temperature for device in updated.temperature_devices) == (24.3, 26.7)
    assert tuple(device.target for device in updated.temperature_devices) == (0.0, 60.0)
    assert updated.print_state == "printing"
    assert updated.print_filename == "cube.gcode"
    assert updated.print_progress == 25.0
    assert updated.filament_used == 3456.7
    assert updated.current_layer == 5
    assert updated.total_layers == 30
    assert updated.position_x == 1.1
    assert updated.position_y == 2.2
    assert updated.position_z == 3.3
    assert updated.position_e == 4.4
    assert updated.requested_speed == 125.0
    assert updated.speed_factor == 150.0
    assert updated.extrude_factor == 95.0
    assert updated.z_offset == -0.04
    assert updated.max_accel == 3000.0
    assert updated.max_velocity == 250.0
    assert updated.exclude_object_names == ("part_a", "part_b")
    assert updated.excluded_object_names == ("part_a",)
    assert updated.current_object == "part_b"


def test_status_from_websocket_message_ignores_unrelated_messages() -> None:
    status = PrinterStatus(objects=("extruder",))

    assert status_from_websocket_message(status, "{") is None
    assert (
        status_from_websocket_message(status, json.dumps({"method": "notify_proc_stat_update"}))
        is None
    )
