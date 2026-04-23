from PySide6.QtCore import Qt

from klippertouch.domain.printer import PrinterStatus, TemperatureDeviceStatus
from klippertouch.qt_models.status_model import StatusModel, TemperatureDeviceListModel


def test_status_model_exposes_printer_status(qtbot) -> None:
    model = StatusModel()
    status = PrinterStatus(
        hostname="orangepi3b",
        klippy_state="ready",
        klipper_version="v0.13.0",
        moonraker_version="v0.10.0",
        objects=("extruder", "heater_bed"),
        temperature_devices=(
            TemperatureDeviceStatus(
                name="extruder",
                display_name="Extruder",
                icon="extruder",
                temperature=212.4,
                target=215.0,
            ),
        ),
        print_state="printing",
        print_filename="cube.gcode",
        print_progress=25.0,
        print_message="Printing",
        print_duration=10.5,
        total_duration=12.0,
        filament_used=1234.5,
        current_layer=3,
        total_layers=12,
        position_x=1.1,
        position_y=2.2,
        position_z=3.3,
        position_e=4.4,
        homed_axes="xy",
        requested_speed=125.0,
        speed_factor=150.0,
        extrude_factor=95.0,
        z_offset=-0.04,
        max_accel=3000.0,
        max_velocity=250.0,
    )

    with qtbot.waitSignal(model.statusChanged, timeout=1000):
        model.set_status(status)

    assert model.hostname == "orangepi3b"
    assert model.klippyState == "ready"
    assert model.objectCount == 2
    assert model.objectNames == ["extruder", "heater_bed"]
    assert model.temperatureDeviceCount == 1
    assert model.printState == "printing"
    assert model.printFilename == "cube.gcode"
    assert model.printProgress == 25.0
    assert model.printMessage == "Printing"
    assert model.printDuration == 10.5
    assert model.totalDuration == 12.0
    assert model.filamentUsed == 1234.5
    assert model.currentLayer == 3
    assert model.totalLayers == 12
    assert model.positionX == 1.1
    assert model.positionY == 2.2
    assert model.positionZ == 3.3
    assert model.positionE == 4.4
    assert model.homedAxes == "xy"
    assert model.requestedSpeed == 125.0
    assert model.speedFactor == 150.0
    assert model.extrudeFactor == 95.0
    assert model.zOffset == -0.04
    assert model.maxAccel == 3000.0
    assert model.maxVelocity == 250.0
    assert model.extruderTemperature == 212.4
    assert model.extruderTarget == 215.0


def test_status_model_can_notify_temperature_device_model(qtbot) -> None:
    temperature_model = TemperatureDeviceListModel()
    model = StatusModel(temperature_device_model=temperature_model)
    status = PrinterStatus(objects=("extruder", "heater_bed"))

    with qtbot.waitSignal(temperature_model.modelReset, timeout=1000):
        model.set_status(status)

    assert model.temperatureDeviceCount == 2
    assert temperature_model.rowCount() == 2


def test_temperature_device_list_model_exposes_qml_roles(qtbot) -> None:
    model = TemperatureDeviceListModel()
    status = PrinterStatus(objects=("extruder", "heater_bed"))

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        model.set_status(status)

    roles = {bytes(value).decode(): key for key, value in model.roleNames().items()}
    first_index = model.index(0, 0)

    assert model.rowCount() == 2
    assert roles == {
        "name": Qt.ItemDataRole.UserRole + 1,
        "displayName": Qt.ItemDataRole.UserRole + 2,
        "icon": Qt.ItemDataRole.UserRole + 3,
        "temperature": Qt.ItemDataRole.UserRole + 4,
        "target": Qt.ItemDataRole.UserRole + 5,
    }
    assert model.data(first_index, roles["name"]) == "extruder"
    assert model.data(first_index, roles["displayName"]) == "Extruder"
    assert model.data(first_index, roles["icon"]) == "extruder"
