from klippertouch.domain.printer import PrinterStatus
from klippertouch.probe import build_status_from_client, status_to_dict


class FakeClient:
    def get_server_info(self):
        return {"moonraker_version": "v0.10.0", "klippy_state": "ready"}

    def get_printer_info(self):
        return {"hostname": "orangepi3b", "software_version": "v0.13.0", "state": "ready"}

    def get_objects_list(self):
        return {"objects": ["extruder", "heater_bed"]}

    def get_printer_objects_query(self, objects=()):
        assert objects == ("extruder", "heater_bed")
        return {
            "status": {
                "extruder": {"temperature": 24.3, "target": 0.0},
                "heater_bed": {"temperature": 26.7, "target": 60.0},
            }
        }


def test_build_status_from_client() -> None:
    status = build_status_from_client(FakeClient())
    assert isinstance(status, PrinterStatus)
    assert status.hostname == "orangepi3b"
    assert status.object_count == 2
    assert tuple(device.temperature for device in status.temperature_devices) == (24.3, 26.7)
    assert tuple(device.target for device in status.temperature_devices) == (0.0, 60.0)

    payload = status_to_dict(status)

    assert payload["temperature_devices"][0]["name"] == "extruder"
    assert payload["temperature_devices"][0]["temperature"] == 24.3


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
