from klippertouch.domain.printer import PrinterStatus
from klippertouch.probe import build_status_from_client, status_to_dict


class FakeClient:
    def get_server_info(self):
        return {"moonraker_version": "v0.10.0", "klippy_state": "ready"}

    def get_printer_info(self):
        return {"hostname": "orangepi3b", "software_version": "v0.13.0", "state": "ready"}

    def get_objects_list(self):
        return {
            "objects": [
                "extruder",
                "heater_bed",
                "print_stats",
                "display_status",
                "toolhead",
                "gcode_move",
            ]
        }

    def get_printer_objects_query(self, objects=()):
        assert objects == (
            "extruder",
            "heater_bed",
            "print_stats",
            "display_status",
            "toolhead",
            "gcode_move",
        )
        return {
            "status": {
                "extruder": {"temperature": 24.3, "target": 0.0},
                "heater_bed": {"temperature": 26.7, "target": 60.0},
                "print_stats": {"state": "printing", "filename": "cube.gcode"},
                "display_status": {"progress": 0.5, "message": "Printing"},
                "toolhead": {"homed_axes": "xyz"},
                "gcode_move": {"gcode_position": [1.1, 2.2, 3.3, 4.4]},
            }
        }


def test_build_status_from_client() -> None:
    status = build_status_from_client(FakeClient())
    assert isinstance(status, PrinterStatus)
    assert status.hostname == "orangepi3b"
    assert status.object_count == 6
    assert tuple(device.temperature for device in status.temperature_devices) == (24.3, 26.7)
    assert tuple(device.target for device in status.temperature_devices) == (0.0, 60.0)
    assert status.print_state == "printing"
    assert status.print_filename == "cube.gcode"
    assert status.print_progress == 50.0
    assert status.position_x == 1.1
    assert status.homed_axes == "xyz"

    payload = status_to_dict(status)

    assert payload["temperature_devices"][0]["name"] == "extruder"
    assert payload["temperature_devices"][0]["temperature"] == 24.3
    assert payload["print_state"] == "printing"
    assert payload["position_x"] == 1.1


def test_build_status_from_client_returns_partial_status_when_optional_probe_fails() -> None:
    class PartialClient:
        def get_server_info(self):
            return {"moonraker_version": "v0.10.0", "klippy_state": "ready"}

        def get_printer_info(self):
            raise RuntimeError("printer/info unavailable")

        def get_objects_list(self):
            raise RuntimeError("objects unavailable")

        def get_printer_objects_query(self, objects=()):
            raise RuntimeError("query unavailable")

    status = build_status_from_client(PartialClient())

    assert status.hostname == "unknown"
    assert status.klippy_state == "ready"
    assert status.moonraker_version == "v0.10.0"
    assert status.objects == ()
    assert status.temperature_devices == ()
