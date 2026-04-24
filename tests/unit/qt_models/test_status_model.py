from PySide6.QtCore import QSettings, Qt

from klippertouch.domain.printer import (
    McuStatus,
    PrinterStatus,
    ServiceVersionStatus,
    TemperatureDeviceStatus,
)
from klippertouch.qt_models.status_model import StatusModel, TemperatureDeviceListModel


def test_status_model_exposes_printer_status(qtbot) -> None:
    model = StatusModel()
    status = PrinterStatus(
        hostname="orangepi3b",
        klippy_state="ready",
        klipper_version="v0.13.0",
        moonraker_version="v0.10.0",
        mcu_statuses=(McuStatus(name="mcu", version="v0.13.0-main", build_versions="gcc 12.2.0"),),
        service_versions=(
            ServiceVersionStatus(name="klipper", version="v0.13.0", configured_type="git_repo"),
            ServiceVersionStatus(name="moonraker", version="v0.10.0", configured_type="git_repo"),
        ),
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
    assert model.mcuCount == 1
    assert model.mcuInfos == [
        {"name": "mcu", "version": "v0.13.0-main", "build_versions": "gcc 12.2.0"}
    ]
    assert model.serviceVersionCount == 2
    assert model.serviceVersions == [
        {"name": "klipper", "version": "v0.13.0", "configured_type": "git_repo"},
        {"name": "moonraker", "version": "v0.10.0", "configured_type": "git_repo"},
    ]
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
        "graphVisible": Qt.ItemDataRole.UserRole + 6,
    }
    assert model.data(first_index, roles["name"]) == "extruder"
    assert model.data(first_index, roles["displayName"]) == "Extruder"
    assert model.data(first_index, roles["icon"]) == "extruder"


def test_temperature_device_list_model_records_read_only_history(qtbot) -> None:
    model = TemperatureDeviceListModel()

    with qtbot.waitSignal(model.historyChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder", "heater_bed"),
                temperature_devices=(
                    TemperatureDeviceStatus(
                        name="extruder",
                        display_name="Extruder",
                        icon="extruder",
                        temperature=210.0,
                        target=215.0,
                    ),
                    TemperatureDeviceStatus(
                        name="heater_bed",
                        display_name="Heater Bed",
                        icon="bed",
                        temperature=58.0,
                        target=60.0,
                    ),
                ),
            )
        )

    model.set_status(
        PrinterStatus(
            objects=("extruder", "heater_bed"),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=60.0,
                ),
            ),
        )
    )

    assert model.extruderSeries == [210.0, 212.0]
    assert model.bedSeries == [58.0, 59.0]


def test_temperature_device_list_model_initializes_history_from_temperature_store(qtbot) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder", "heater_bed", "temperature_sensor chamber"),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=60.0,
                ),
                TemperatureDeviceStatus(
                    name="temperature_sensor chamber",
                    display_name="Temperature Sensor Chamber",
                    icon="heat-up",
                    temperature=35.0,
                    target=None,
                ),
            ),
        )
    )

    with qtbot.waitSignal(model.historyChanged, timeout=1000):
        model.initialize_history(
            {
                "extruder": {
                    "temperatures": [200.0, 205.0, 210.0],
                    "targets": [215.0, 215.0, 215.0],
                },
                "heater_bed": {"temperatures": [50.0, 55.0, 58.0]},
                "temperature_sensor chamber": {"temperatures": [29.0, 31.0, 33.0]},
            }
        )

    assert model.extruderSeries == [200.0, 205.0, 210.0]
    assert model.bedSeries == [50.0, 55.0, 58.0]
    assert [item["name"] for item in model.graphSeriesModel] == [
        "extruder",
        "extruder_target",
        "heater_bed",
        "heater_bed_target",
        "temperature_sensor chamber",
    ]
    assert model.graphSeriesModel[0]["dashed"] is False
    assert model.graphSeriesModel[1]["dashed"] is True
    assert model.graphSeriesModel[2]["series"] == [50.0, 55.0, 58.0]
    assert model.graphSeriesModel[3]["dashed"] is True
    assert model.graphSeriesModel[4]["series"] == [29.0, 31.0, 33.0]


def test_temperature_device_list_model_toggles_graph_visibility(qtbot) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder", "heater_bed"),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=60.0,
                ),
            ),
        )
    )
    model.initialize_history(
        {
            "extruder": {"temperatures": [200.0, 205.0, 210.0]},
            "heater_bed": {"temperatures": [50.0, 55.0, 58.0]},
        }
    )

    with qtbot.waitSignal(model.graphSelectionChanged, timeout=1000):
        model.toggleGraphDevice("heater_bed")

    assert [item["name"] for item in model.graphSeriesModel] == ["extruder", "extruder_target"]


def test_temperature_device_list_model_adds_target_series_for_heaters(qtbot) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder", "heater_bed", "temperature_sensor chamber"),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=220.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=0.0,
                ),
                TemperatureDeviceStatus(
                    name="temperature_sensor chamber",
                    display_name="Temperature Sensor Chamber",
                    icon="heat-up",
                    temperature=35.0,
                    target=None,
                ),
            ),
        )
    )
    model.initialize_history(
        {
            "extruder": {
                "temperatures": [200.0, 205.0, 210.0],
                "targets": [220.0, 220.0, 220.0],
            },
            "heater_bed": {
                "temperatures": [50.0, 55.0, 58.0],
                "targets": [0.0, 0.0, 0.0],
            },
            "temperature_sensor chamber": {"temperatures": [29.0, 31.0, 33.0]},
        }
    )

    assert [item["name"] for item in model.graphSeriesModel] == [
        "extruder",
        "extruder_target",
        "heater_bed",
        "temperature_sensor chamber",
    ]
    assert model.graphSeriesModel[1]["series"] == [220.0, 220.0, 220.0]
    assert model.graphSeriesModel[1]["dashed"] is True


def test_temperature_device_list_model_persists_graph_visibility_per_host(qtbot, tmp_path) -> None:
    settings = QSettings(str(tmp_path / "temperature-graph.ini"), QSettings.Format.IniFormat)
    first_model = TemperatureDeviceListModel(settings=settings)
    status = PrinterStatus(
        hostname="toper1",
        objects=("extruder", "heater_bed"),
        temperature_devices=(
            TemperatureDeviceStatus(
                name="extruder",
                display_name="Extruder",
                icon="extruder",
                temperature=212.0,
                target=215.0,
            ),
            TemperatureDeviceStatus(
                name="heater_bed",
                display_name="Heater Bed",
                icon="bed",
                temperature=59.0,
                target=60.0,
            ),
        ),
    )
    first_model.set_status(status)
    first_model.initialize_history(
        {
            "extruder": {"temperatures": [200.0, 205.0, 210.0]},
            "heater_bed": {"temperatures": [50.0, 55.0, 58.0]},
        }
    )

    with qtbot.waitSignal(first_model.graphSelectionChanged, timeout=1000):
        first_model.toggleGraphDevice("heater_bed")

    second_model = TemperatureDeviceListModel(settings=settings)
    second_model.set_status(status)
    second_model.initialize_history(
        {
            "extruder": {"temperatures": [200.0, 205.0, 210.0]},
            "heater_bed": {"temperatures": [50.0, 55.0, 58.0]},
        }
    )

    assert [item["name"] for item in second_model.graphSeriesModel] == [
        "extruder",
        "extruder_target",
    ]


def test_temperature_device_list_model_scopes_graph_visibility_by_host(qtbot, tmp_path) -> None:
    settings = QSettings(str(tmp_path / "temperature-graph.ini"), QSettings.Format.IniFormat)
    first_model = TemperatureDeviceListModel(settings=settings)
    first_model.set_status(
        PrinterStatus(
            hostname="printer-a",
            objects=("extruder", "heater_bed"),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=60.0,
                ),
            ),
        )
    )
    first_model.initialize_history(
        {
            "extruder": {"temperatures": [200.0, 205.0, 210.0]},
            "heater_bed": {"temperatures": [50.0, 55.0, 58.0]},
        }
    )
    first_model.toggleGraphDevice("heater_bed")

    second_model = TemperatureDeviceListModel(settings=settings)
    second_model.set_status(
        PrinterStatus(
            hostname="printer-b",
            objects=("extruder", "heater_bed"),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=60.0,
                ),
            ),
        )
    )
    second_model.initialize_history(
        {
            "extruder": {"temperatures": [200.0, 205.0, 210.0]},
            "heater_bed": {"temperatures": [50.0, 55.0, 58.0]},
        }
    )

    assert [item["name"] for item in second_model.graphSeriesModel] == [
        "extruder",
        "extruder_target",
        "heater_bed",
        "heater_bed_target",
    ]
