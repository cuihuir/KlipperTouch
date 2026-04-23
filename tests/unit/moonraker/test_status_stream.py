import json
from pathlib import Path

from klippertouch.config.models import PrinterConfig
from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.status_stream import (
    build_temperature_subscription_message,
    build_websocket_request,
    status_from_websocket_message,
)


def test_build_temperature_subscription_message_uses_read_only_objects_method() -> None:
    status = PrinterStatus(objects=("extruder", "heater_bed", "fan"))
    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    message = json.loads(build_temperature_subscription_message(client, status))

    assert message == {
        "jsonrpc": "2.0",
        "method": "printer.objects.subscribe",
        "params": {
            "objects": {
                "extruder": ["temperature", "target"],
                "heater_bed": ["temperature", "target"],
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
    assert "self._reconnect_timer.timeout.connect(self.start)" in source
    assert "printer.objects.subscribe" in source
    assert "printer.gcode.script" not in source


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


def test_status_from_websocket_message_applies_subscription_snapshot() -> None:
    status = PrinterStatus(objects=("extruder", "heater_bed"))
    message = json.dumps(
        {
            "jsonrpc": "2.0",
            "result": {
                "status": {
                    "extruder": {"temperature": 24.3, "target": 0.0},
                    "heater_bed": {"temperature": 26.7, "target": 60.0},
                }
            },
            "id": 1,
        }
    )

    updated = status_from_websocket_message(status, message)

    assert updated is not None
    assert tuple(device.temperature for device in updated.temperature_devices) == (24.3, 26.7)
    assert tuple(device.target for device in updated.temperature_devices) == (0.0, 60.0)


def test_status_from_websocket_message_ignores_unrelated_messages() -> None:
    status = PrinterStatus(objects=("extruder",))

    assert status_from_websocket_message(status, "{") is None
    assert (
        status_from_websocket_message(status, json.dumps({"method": "notify_proc_stat_update"}))
        is None
    )
