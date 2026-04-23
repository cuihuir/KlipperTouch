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
