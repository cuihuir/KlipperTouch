from klippertouch.domain.printer import PrinterStatus, TemperatureDeviceStatus


def test_printer_status_from_probe_payloads() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["extruder", "heater_bed", "controller_fan 驱动"]},
    )

    assert status.hostname == "orangepi3b"
    assert status.klippy_state == "ready"
    assert status.object_count == 3
    assert "controller_fan 驱动" in status.objects


def test_printer_status_copies_mutable_objects() -> None:
    object_names = ["extruder"]
    status = PrinterStatus(objects=object_names)  # type: ignore[arg-type]

    object_names.append("heater_bed")

    assert status.objects == ("extruder",)
    assert status.object_count == 1


def test_temperature_device_status_normalizes_values() -> None:
    device = TemperatureDeviceStatus(
        name="heater_bed",
        display_name="Heater Bed",
        icon="bed",
        temperature=24.6,
        target=60.2,
    )

    assert device.display_name == "Heater Bed"
    assert device.temperature == 24.6
    assert device.target == 60.2


def test_printer_status_derives_read_only_temperature_devices_from_objects() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={
            "objects": [
                "extruder",
                "heater_bed",
                "temperature_sensor raspberry_pi",
                "controller_fan 驱动",
            ]
        },
    )

    assert tuple(device.name for device in status.temperature_devices) == (
        "extruder",
        "heater_bed",
        "temperature_sensor raspberry_pi",
    )
    assert tuple(device.icon for device in status.temperature_devices) == (
        "extruder",
        "bed",
        "heat-up",
    )
    assert status.temperature_device_count == 3


def test_printer_status_populates_temperature_values_from_status_query() -> None:
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

    assert tuple(device.temperature for device in status.temperature_devices) == (24.3, 26.7)
    assert tuple(device.target for device in status.temperature_devices) == (0.0, 60.0)


def test_printer_status_applies_read_only_temperature_update() -> None:
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

    updated = status.with_temperature_status_update(
        {
            "extruder": {"temperature": 25.1},
            "heater_bed": {"target": 55.0},
        }
    )

    assert updated.hostname == "orangepi3b"
    assert updated.objects == ("extruder", "heater_bed")
    assert tuple(device.temperature for device in updated.temperature_devices) == (25.1, 26.7)
    assert tuple(device.target for device in updated.temperature_devices) == (0.0, 55.0)


def test_printer_status_populates_read_only_job_state_from_status_query() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["print_stats", "display_status", "virtual_sdcard"]},
        object_status={
            "status": {
                "print_stats": {
                    "state": "printing",
                    "filename": "calibration_cube.gcode",
                    "print_duration": 42.5,
                    "total_duration": 51.0,
                },
                "display_status": {"progress": 0.375, "message": "Printing"},
                "virtual_sdcard": {"progress": 0.4, "is_active": True},
            }
        },
    )

    assert status.print_state == "printing"
    assert status.print_filename == "calibration_cube.gcode"
    assert status.print_progress == 37.5
    assert status.print_message == "Printing"
    assert status.print_duration == 42.5
    assert status.total_duration == 51.0


def test_printer_status_applies_read_only_print_update() -> None:
    status = PrinterStatus(
        objects=("print_stats", "display_status", "virtual_sdcard"),
        print_state="standby",
        print_filename="old.gcode",
        print_progress=0.0,
    )

    updated = status.with_status_update(
        {
            "print_stats": {"state": "paused", "filename": "part.gcode"},
            "virtual_sdcard": {"progress": 0.625, "is_active": True},
            "display_status": {"message": "Paused"},
        }
    )

    assert updated.print_state == "paused"
    assert updated.print_filename == "part.gcode"
    assert updated.print_progress == 62.5
    assert updated.print_message == "Paused"
