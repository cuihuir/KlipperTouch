from klippertouch.domain.printer import PrinterStatus


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
