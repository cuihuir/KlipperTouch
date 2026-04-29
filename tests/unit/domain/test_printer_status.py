from klippertouch.domain.printer import (
    FilamentSensorStatus,
    McuStatus,
    PrinterStatus,
    ServiceVersionStatus,
    TemperatureDeviceStatus,
)


def test_printer_status_from_probe_payloads() -> None:
    status = PrinterStatus.from_probe(
        server_info={
            "moonraker_version": "v0.10.0",
            "klippy_state": "ready",
            "components": ["update_manager", "history"],
            "warnings": [
                "[update_manager]: Failed to load extension fluidd",
                {"message": "MCU 'cartographer' has deprecated code"},
            ],
        },
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["extruder", "heater_bed", "controller_fan 驱动"]},
        update_status={
            "version_info": {
                "moonraker": {"name": "moonraker", "version": "v0.10.0"},
                "klipper": {"name": "klipper", "version": "v0.13.0"},
            }
        },
    )

    assert status.hostname == "orangepi3b"
    assert status.klippy_state == "ready"
    assert status.object_count == 3
    assert "controller_fan 驱动" in status.objects
    assert tuple(item.name for item in status.service_versions) == ("klipper", "moonraker")
    assert status.moonraker_warnings == (
        "[update_manager]: Failed to load extension fluidd",
        "MCU 'cartographer' has deprecated code",
    )


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
                "temperature_sensor raspberry_pi",
                "heater_bed",
                "extruder",
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


def test_temperature_device_display_names_remove_klipper_object_prefixes() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "toper1", "software_version": "v0.13.0"},
        objects={
            "objects": [
                "temperature_fan SOC散热",
                "temperature_host SOC散热",
                "temperature_sensor chamber",
                "heater_generic chamber heater",
            ]
        },
    )

    display_names = {device.name: device.display_name for device in status.temperature_devices}

    assert display_names == {
        "heater_generic chamber heater": "Chamber Heater",
        "temperature_fan SOC散热": "SOC散热 Fan",
        "temperature_host SOC散热": "SOC散热 Host",
        "temperature_sensor chamber": "Chamber",
    }


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


def test_printer_status_populates_primary_extruder_pressure_advance() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["extruder"]},
        object_status={
            "status": {
                "extruder": {
                    "temperature": 24.3,
                    "target": 0.0,
                    "can_extrude": True,
                    "pressure_advance": 0.045,
                    "smooth_time": 0.04,
                },
            }
        },
    )

    assert status.extruder_can_extrude is True
    assert status.extruder_pressure_advance == 0.045
    assert status.extruder_smooth_time == 0.04


def test_printer_status_populates_filament_sensor_values_from_status_query() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={
            "objects": [
                "extruder",
                "filament_switch_sensor runout",
                "filament_motion_sensor encoder",
            ]
        },
        object_status={
            "status": {
                "filament_switch_sensor runout": {
                    "enabled": True,
                    "filament_detected": False,
                },
                "filament_motion_sensor encoder": {
                    "enabled": False,
                    "filament_detected": True,
                },
            }
        },
    )

    assert status.filament_sensor_count == 2
    assert status.filament_sensors == (
        FilamentSensorStatus(
            name="filament_motion_sensor encoder",
            display_name="Encoder",
            sensor_type="motion",
            enabled=False,
            filament_detected=True,
        ),
        FilamentSensorStatus(
            name="filament_switch_sensor runout",
            display_name="Runout",
            sensor_type="switch",
            enabled=True,
            filament_detected=False,
        ),
    )


def test_printer_status_populates_mcu_and_service_versions() -> None:
    status = PrinterStatus.from_probe(
        server_info={
            "moonraker_version": "v0.10.0",
            "klippy_state": "ready",
            "components": ["update_manager", "history"],
        },
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["mcu", "mcu tool_head", "extruder"]},
        object_status={"status": {"extruder": {"temperature": 24.3, "target": 0.0}}},
        mcu_status={
            "status": {
                "mcu": {
                    "mcu_version": "v0.13.0-main",
                    "mcu_build_versions": "gcc 12.2.0",
                },
                "mcu tool_head": {
                    "mcu_version": "v0.13.0-tool",
                    "mcu_build_versions": "gcc 12.2.0",
                },
            }
        },
        update_status={
            "version_info": {
                "system": {"name": "system", "configured_type": "system"},
                "moonraker": {
                    "name": "moonraker",
                    "configured_type": "git_repo",
                    "version": "v0.10.0",
                },
                "klipper": {
                    "name": "klipper",
                    "configured_type": "git_repo",
                    "version": "v0.13.0",
                },
                "mainsail": {
                    "name": "mainsail",
                    "configured_type": "web",
                    "version": "v2.14.0",
                },
            }
        },
    )

    assert status.mcu_count == 2
    assert status.service_version_count == 3
    assert status.mcu_statuses == (
        McuStatus(name="mcu", version="v0.13.0-main", build_versions="gcc 12.2.0"),
        McuStatus(name="mcu tool_head", version="v0.13.0-tool", build_versions="gcc 12.2.0"),
    )
    assert status.service_versions == (
        ServiceVersionStatus(name="klipper", version="v0.13.0", configured_type="git_repo"),
        ServiceVersionStatus(name="mainsail", version="v2.14.0", configured_type="web"),
        ServiceVersionStatus(name="moonraker", version="v0.10.0", configured_type="git_repo"),
    )


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


def test_printer_status_applies_primary_extruder_pressure_advance_update() -> None:
    status = PrinterStatus(
        objects=("extruder",),
        extruder_can_extrude=False,
        extruder_pressure_advance=0.02,
        extruder_smooth_time=0.03,
    )

    updated = status.with_status_update(
        {"extruder": {"can_extrude": True, "pressure_advance": 0.055, "smooth_time": 0.04}}
    )

    assert updated.extruder_can_extrude is True
    assert updated.extruder_pressure_advance == 0.055
    assert updated.extruder_smooth_time == 0.04


def test_printer_status_applies_filament_sensor_update() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["filament_switch_sensor runout"]},
        object_status={
            "status": {
                "filament_switch_sensor runout": {
                    "enabled": True,
                    "filament_detected": True,
                }
            }
        },
    )

    updated = status.with_status_update(
        {"filament_switch_sensor runout": {"filament_detected": False}}
    )

    assert updated.filament_sensors[0].enabled is True
    assert updated.filament_sensors[0].filament_detected is False


def test_printer_status_update_preserves_static_version_metadata() -> None:
    status = PrinterStatus(
        hostname="toper1",
        klippy_state="ready",
        klipper_version="v0.13.0",
        moonraker_version="v0.10.0",
        mcu_statuses=(McuStatus(name="mcu", version="v0.13.0-main"),),
        service_versions=(
            ServiceVersionStatus(name="klipper", version="v0.13.0"),
            ServiceVersionStatus(name="moonraker", version="v0.10.0"),
        ),
        objects=("extruder",),
        temperature_devices=(
            TemperatureDeviceStatus(
                name="extruder",
                display_name="Extruder",
                icon="extruder",
                temperature=210.0,
                target=215.0,
            ),
        ),
    )

    updated = status.with_status_update({"extruder": {"temperature": 212.0}})

    assert updated.mcu_statuses == status.mcu_statuses
    assert updated.service_versions == status.service_versions
    assert updated.klipper_version == "v0.13.0"
    assert updated.moonraker_version == "v0.10.0"


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
                    "filament_used": 1234.5,
                    "info": {"current_layer": 3, "total_layer": 12},
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
    assert status.filament_used == 1234.5
    assert status.current_layer == 3
    assert status.total_layers == 12


def test_printer_status_populates_webhooks_shutdown_state() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "shutdown"},
        printer_info={"state": "shutdown", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["webhooks"]},
        object_status={
            "status": {
                "webhooks": {
                    "state": "shutdown",
                    "state_message": "Shutdown due to webhooks request",
                }
            }
        },
    )

    assert status.webhooks_state == "shutdown"
    assert status.webhooks_message == "Shutdown due to webhooks request"


def test_printer_status_applies_webhooks_state_from_websocket_update() -> None:
    status = PrinterStatus(
        klippy_state="ready",
        moonraker_version="v0.10.0",
        objects=("webhooks",),
    )

    updated = status.with_status_update(
        {"webhooks": {"state": "shutdown", "state_message": "Shutdown due to webhooks"}}
    )

    assert updated.webhooks_state == "shutdown"
    assert updated.webhooks_message == "Shutdown due to webhooks"


def test_printer_status_marks_klippy_ready_when_webhooks_recovers() -> None:
    status = PrinterStatus(
        klippy_state="shutdown",
        moonraker_version="v0.10.0",
        objects=("webhooks",),
        webhooks_state="shutdown",
        webhooks_message="Shutdown due to webhooks request",
    )

    updated = status.with_status_update({"webhooks": {"state": "ready"}})

    assert updated.klippy_state == "ready"
    assert updated.webhooks_state == "ready"
    assert updated.webhooks_message == "Printer is ready"


def test_printer_status_normalizes_probe_when_webhooks_is_ready() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "startup"},
        printer_info={"state": "startup", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["webhooks"]},
        object_status={"status": {"webhooks": {"state": "ready", "state_message": ""}}},
    )

    assert status.klippy_state == "ready"
    assert status.webhooks_state == "ready"
    assert status.webhooks_message == "Printer is ready"


def test_printer_status_tracks_webhooks_startup_and_disconnected_states() -> None:
    status = PrinterStatus(
        klippy_state="shutdown",
        moonraker_version="v0.10.0",
        objects=("webhooks",),
        webhooks_state="shutdown",
    )

    startup = status.with_status_update(
        {"webhooks": {"state": "startup", "state_message": "Klipper is attempting to start"}}
    )
    disconnected = startup.with_status_update(
        {"webhooks": {"state": "disconnected", "state_message": "Moonraker disconnected"}}
    )

    assert startup.klippy_state == "startup"
    assert startup.webhooks_state == "startup"
    assert startup.webhooks_message == "Klipper is attempting to start"
    assert disconnected.klippy_state == "disconnected"
    assert disconnected.webhooks_state == "disconnected"
    assert disconnected.webhooks_message == "Moonraker disconnected"


def test_printer_status_applies_read_only_print_update() -> None:
    status = PrinterStatus(
        objects=("print_stats", "display_status", "virtual_sdcard"),
        print_state="standby",
        print_filename="old.gcode",
        print_progress=0.0,
    )

    updated = status.with_status_update(
        {
            "print_stats": {
                "state": "paused",
                "filename": "part.gcode",
                "filament_used": 2345.6,
                "info": {"current_layer": 4, "total_layer": 20},
            },
            "virtual_sdcard": {"progress": 0.625, "is_active": True},
            "display_status": {"message": "Paused"},
        }
    )

    assert updated.print_state == "paused"
    assert updated.print_filename == "part.gcode"
    assert updated.print_progress == 62.5
    assert updated.print_message == "Paused"
    assert updated.filament_used == 2345.6
    assert updated.current_layer == 4
    assert updated.total_layers == 20


def test_printer_status_populates_read_only_exclude_object_state() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["exclude_object"]},
        object_status={
            "status": {
                "exclude_object": {
                    "objects": [{"name": "part_a"}, {"name": "part_b"}],
                    "excluded_objects": ["part_a"],
                    "current_object": "part_b",
                },
            }
        },
    )

    assert status.exclude_object_names == ("part_a", "part_b")
    assert status.excluded_object_names == ("part_a",)
    assert status.current_object == "part_b"
    assert status.exclude_object_count == 2
    assert status.excluded_object_count == 1


def test_printer_status_applies_read_only_exclude_object_update() -> None:
    status = PrinterStatus(
        objects=("exclude_object",),
        exclude_object_names=("part_a", "part_b"),
        excluded_object_names=(),
        current_object="part_a",
    )

    updated = status.with_status_update(
        {
            "exclude_object": {
                "current_object": "part_b",
                "excluded_objects": ["part_a"],
            }
        }
    )

    assert updated.exclude_object_names == ("part_a", "part_b")
    assert updated.excluded_object_names == ("part_a",)
    assert updated.current_object == "part_b"


def test_printer_status_ignores_null_display_status_message() -> None:
    status = PrinterStatus(
        objects=("print_stats", "display_status"),
        print_state="printing",
        print_message="",
    )

    updated = status.with_status_update({"display_status": {"message": None}})

    assert updated.print_message == ""


def test_printer_status_preserves_progress_when_terminal_update_reports_zero() -> None:
    status = PrinterStatus(
        objects=("print_stats", "display_status", "virtual_sdcard"),
        print_state="printing",
        print_filename="part.gcode",
        print_progress=46.3,
    )

    updated = status.with_status_update(
        {
            "print_stats": {"state": "cancelled", "filename": "part.gcode"},
            "display_status": {"progress": 0.0},
            "virtual_sdcard": {"progress": 0.0},
        }
    )

    assert updated.print_state == "cancelled"
    assert updated.print_progress == 46.3


def test_printer_status_populates_read_only_toolhead_position() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["toolhead", "gcode_move"]},
        object_status={
            "status": {
                "toolhead": {
                    "homed_axes": "xyz",
                    "position": [1.0, 2.0, 3.0, 4.0],
                    "max_accel": 3000.0,
                    "max_velocity": 250.0,
                },
                "gcode_move": {
                    "gcode_position": [10.1, 20.2, 30.3, 40.4],
                    "speed": 7500.0,
                    "speed_factor": 1.5,
                    "extrude_factor": 0.95,
                    "homing_origin": [0.0, 0.0, -0.04],
                },
            }
        },
    )

    assert status.position_x == 10.1
    assert status.position_y == 20.2
    assert status.position_z == 30.3
    assert status.position_e == 40.4
    assert status.homed_axes == "xyz"
    assert status.requested_speed == 125.0
    assert status.speed_factor == 150.0
    assert status.extrude_factor == 95.0
    assert status.z_offset == -0.04
    assert status.max_accel == 3000.0
    assert status.max_velocity == 250.0


def test_printer_status_applies_read_only_toolhead_update() -> None:
    status = PrinterStatus(objects=("toolhead", "gcode_move"), position_x=1.0)

    updated = status.with_status_update(
        {
            "toolhead": {"homed_axes": "xy", "max_accel": 2400.0, "max_velocity": 180.0},
            "gcode_move": {
                "gcode_position": [11.0, 22.0, 33.0, 44.0],
                "speed": 5400.0,
                "speed_factor": 0.8,
                "extrude_factor": 1.1,
                "homing_origin": [0.0, 0.0, 0.12],
            },
        }
    )

    assert updated.position_x == 11.0
    assert updated.position_y == 22.0
    assert updated.position_z == 33.0
    assert updated.position_e == 44.0
    assert updated.homed_axes == "xy"
    assert updated.requested_speed == 90.0
    assert updated.speed_factor == 80.0
    assert updated.extrude_factor == 110.0
    assert updated.z_offset == 0.12
    assert updated.max_accel == 2400.0
    assert updated.max_velocity == 180.0


def test_printer_status_exposes_primary_extruder_temperatures() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["heater_bed", "extruder"]},
        object_status={
            "status": {
                "heater_bed": {"temperature": 26.7, "target": 60.0},
                "extruder": {"temperature": 212.4, "target": 215.0},
            }
        },
    )

    assert status.primary_extruder_temperature == 212.4
    assert status.primary_extruder_target == 215.0
