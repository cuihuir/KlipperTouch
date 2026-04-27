from klippertouch.domain.printer import PrinterStatus
from klippertouch.probe import build_status_from_client, status_to_dict


class FakeClient:
    def get_server_info(self):
        return {
            "moonraker_version": "v0.10.0",
            "klippy_state": "ready",
            "components": ["update_manager", "history"],
        }

    def get_printer_info(self):
        return {"hostname": "orangepi3b", "software_version": "v0.13.0", "state": "ready"}

    def get_objects_list(self):
        return {
            "objects": [
                "mcu",
                "extruder",
                "heater_bed",
                "print_stats",
                "display_status",
                "toolhead",
                "gcode_move",
                "exclude_object",
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
            "exclude_object",
        )
        return {
            "status": {
                "extruder": {"temperature": 24.3, "target": 0.0},
                "heater_bed": {"temperature": 26.7, "target": 60.0},
                "print_stats": {"state": "printing", "filename": "cube.gcode"},
                "display_status": {"progress": 0.5, "message": "Printing"},
                "toolhead": {"homed_axes": "xyz"},
                "gcode_move": {"gcode_position": [1.1, 2.2, 3.3, 4.4]},
                "exclude_object": {
                    "objects": [{"name": "part_a"}, {"name": "part_b"}],
                    "excluded_objects": ["part_a"],
                    "current_object": "part_b",
                },
            }
        }

    def get_printer_objects_query_fields(self, fields_by_object):
        assert fields_by_object == {"mcu": "mcu_version,mcu_build_versions"}
        return {
            "status": {
                "mcu": {
                    "mcu_version": "v0.13.0-main",
                    "mcu_build_versions": "gcc 12.2.0",
                }
            }
        }

    def get_printer_objects_query_jsonrpc(self, objects):
        return {"status": {}}

    def get_machine_update_status(self):
        return {
            "version_info": {
                "moonraker": {"name": "moonraker", "version": "v0.10.0"},
                "klipper": {"name": "klipper", "version": "v0.13.0"},
            }
        }


def test_build_status_from_client() -> None:
    status = build_status_from_client(FakeClient())
    assert isinstance(status, PrinterStatus)
    assert status.hostname == "orangepi3b"
    assert status.object_count == 8
    assert tuple(device.temperature for device in status.temperature_devices) == (24.3, 26.7)
    assert tuple(device.target for device in status.temperature_devices) == (0.0, 60.0)
    assert status.print_state == "printing"
    assert status.print_filename == "cube.gcode"
    assert status.print_progress == 50.0
    assert status.position_x == 1.1
    assert status.homed_axes == "xyz"
    assert status.exclude_object_names == ("part_a", "part_b")
    assert status.excluded_object_names == ("part_a",)
    assert status.current_object == "part_b"
    assert status.mcu_statuses[0].version == "v0.13.0-main"
    assert tuple(item.name for item in status.service_versions) == ("klipper", "moonraker")

    payload = status_to_dict(status)

    assert payload["temperature_devices"][0]["name"] == "extruder"
    assert payload["temperature_devices"][0]["temperature"] == 24.3
    assert payload["print_state"] == "printing"
    assert payload["position_x"] == 1.1
    assert payload["mcu_statuses"][0]["name"] == "mcu"
    assert payload["service_versions"][0]["name"] == "klipper"


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

        def get_printer_objects_query_jsonrpc(self, objects):
            raise RuntimeError("jsonrpc query unavailable")

        def get_printer_objects_query_fields(self, fields_by_object):
            raise RuntimeError("mcu query unavailable")

        def get_machine_update_status(self):
            raise RuntimeError("update status unavailable")

    status = build_status_from_client(PartialClient())

    assert status.hostname == "unknown"
    assert status.klippy_state == "ready"
    assert status.moonraker_version == "v0.10.0"
    assert status.objects == ()
    assert status.temperature_devices == ()
    assert status.mcu_statuses == ()
    assert status.service_versions == ()


def test_build_status_from_client_uses_unfiltered_query_for_non_ascii_temperature_objects() -> None:
    class NonAsciiTemperatureClient(FakeClient):
        def __init__(self) -> None:
            self.queries: list[tuple[str, ...]] = []

        def get_objects_list(self):
            return {
                "objects": [
                    "extruder",
                    "temperature_host SOC散热",
                    "temperature_sensor chamber",
                ]
            }

        def get_printer_objects_query(self, objects=()):
            self.queries.append(tuple(objects))
            return {
                "status": {
                    "extruder": {"temperature": 24.3, "target": 0.0},
                    "temperature_sensor chamber": {"temperature": 35.5},
                }
            }

        def get_printer_objects_query_jsonrpc(self, objects):
            self.queries.append(tuple(objects))
            assert objects == {"temperature_host SOC散热": ["temperature", "target"]}
            return {
                "status": {
                    "temperature_host SOC散热": {"temperature": 42.5},
                }
            }

        def get_printer_objects_query_fields(self, fields_by_object):
            return {"status": {}}

    client = NonAsciiTemperatureClient()
    status = build_status_from_client(client)

    assert client.queries == [
        ("extruder", "temperature_host SOC散热", "temperature_sensor chamber"),
        ("temperature_host SOC散热",),
    ]
    assert tuple(device.name for device in status.temperature_devices) == (
        "extruder",
        "temperature_sensor chamber",
        "temperature_host SOC散热",
    )
    assert tuple(device.display_name for device in status.temperature_devices) == (
        "Extruder",
        "Chamber",
        "SOC散热 Host",
    )
    assert tuple(device.temperature for device in status.temperature_devices) == (
        24.3,
        35.5,
        42.5,
    )
