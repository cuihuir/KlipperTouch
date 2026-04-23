from klippertouch.domain.printer import PrinterStatus
from klippertouch.probe import build_status_from_client


class FakeClient:
    def get_server_info(self):
        return {"moonraker_version": "v0.10.0", "klippy_state": "ready"}

    def get_printer_info(self):
        return {"hostname": "orangepi3b", "software_version": "v0.13.0", "state": "ready"}

    def get_objects_list(self):
        return {"objects": ["extruder", "heater_bed"]}


def test_build_status_from_client() -> None:
    status = build_status_from_client(FakeClient())
    assert isinstance(status, PrinterStatus)
    assert status.hostname == "orangepi3b"
    assert status.object_count == 2
