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
        exclude_object_names=("part_a", "part_b"),
        excluded_object_names=("part_a",),
        current_object="part_b",
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
    assert model.excludeObjectNames == ["part_a", "part_b"]
    assert model.excludedObjectNames == ["part_a"]
    assert model.currentObject == "part_b"
    assert model.excludeObjectCount == 2
    assert model.excludedObjectCount == 1
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


def test_status_model_exposes_webhooks_shutdown_fields(qtbot) -> None:
    model = StatusModel()
    changes: list[bool] = []
    model.hostChanged.connect(lambda: changes.append(True))

    model.set_status(
        PrinterStatus(
            klippy_state="shutdown",
            webhooks_state="shutdown",
            webhooks_message="Shutdown due to webhooks request",
        )
    )

    assert model.webhooksState == "shutdown"
    assert model.webhooksMessage == "Shutdown due to webhooks request"
    assert changes == [True]


def test_status_model_can_notify_temperature_device_model(qtbot) -> None:
    temperature_model = TemperatureDeviceListModel()
    model = StatusModel(temperature_device_model=temperature_model)
    status = PrinterStatus(objects=("extruder", "heater_bed"))

    with qtbot.waitSignal(temperature_model.modelReset, timeout=1000):
        model.set_status(status)

    assert model.temperatureDeviceCount == 2
    assert temperature_model.rowCount() == 2


def test_status_model_emits_granular_temperature_signal_without_global_property_churn(
    qtbot,
) -> None:
    model = StatusModel()
    model.set_status(
        PrinterStatus(
            hostname="orangepi3b",
            klippy_state="ready",
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
            print_state="printing",
            print_progress=10.0,
        )
    )
    host_changes: list[bool] = []
    print_changes: list[bool] = []
    object_changes: list[bool] = []
    toolhead_changes: list[bool] = []
    temperature_changes: list[bool] = []
    model.hostChanged.connect(lambda: host_changes.append(True))
    model.printChanged.connect(lambda: print_changes.append(True))
    model.objectsChanged.connect(lambda: object_changes.append(True))
    model.toolheadChanged.connect(lambda: toolhead_changes.append(True))
    model.extruderTemperatureChanged.connect(lambda: temperature_changes.append(True))

    with qtbot.waitSignal(model.extruderTemperatureChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                hostname="orangepi3b",
                klippy_state="ready",
                objects=("extruder",),
                temperature_devices=(
                    TemperatureDeviceStatus(
                        name="extruder",
                        display_name="Extruder",
                        icon="extruder",
                        temperature=212.0,
                        target=215.0,
                    ),
                ),
                print_state="printing",
                print_progress=10.0,
            )
        )

    assert temperature_changes == [True]
    assert host_changes == []
    assert print_changes == []
    assert object_changes == []
    assert toolhead_changes == []
    assert model.extruderTemperature == 212.0


def test_status_model_emits_granular_print_signal_without_host_or_temperature_churn(
    qtbot,
) -> None:
    model = StatusModel()
    model.set_status(
        PrinterStatus(
            hostname="orangepi3b",
            klippy_state="ready",
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
            print_state="printing",
            print_progress=10.0,
        )
    )
    host_changes: list[bool] = []
    print_changes: list[bool] = []
    temperature_changes: list[bool] = []
    model.hostChanged.connect(lambda: host_changes.append(True))
    model.printChanged.connect(lambda: print_changes.append(True))
    model.extruderTemperatureChanged.connect(lambda: temperature_changes.append(True))

    with qtbot.waitSignal(model.printChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                hostname="orangepi3b",
                klippy_state="ready",
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
                print_state="printing",
                print_progress=25.0,
            )
        )

    assert print_changes == [True]
    assert host_changes == []
    assert temperature_changes == []
    assert model.printProgress == 25.0


def test_status_model_suppresses_hidden_toolhead_updates_until_panel_needs_them(
    qtbot,
) -> None:
    model = StatusModel()
    model.set_status(
        PrinterStatus(
            objects=("toolhead", "gcode_move"),
            position_x=1.0,
            position_y=2.0,
            position_z=3.0,
            position_e=4.0,
        )
    )
    toolhead_changes: list[bool] = []
    model.toolheadChanged.connect(lambda: toolhead_changes.append(True))

    model.set_status(
        PrinterStatus(
            objects=("toolhead", "gcode_move"),
            position_x=5.0,
            position_y=6.0,
            position_z=7.0,
            position_e=8.0,
        )
    )

    assert toolhead_changes == []
    assert model.positionX == 5.0

    with qtbot.waitSignal(model.toolheadChanged, timeout=1000):
        model.setActivePanel("move")

    assert toolhead_changes == [True]
    assert model.activePanel == "move"

    with qtbot.waitSignal(model.toolheadChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("toolhead", "gcode_move"),
                position_x=9.0,
                position_y=10.0,
                position_z=11.0,
                position_e=12.0,
            )
        )

    assert toolhead_changes == [True, True]
    assert model.positionX == 9.0


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
        "targetPending": Qt.ItemDataRole.UserRole + 7,
        "targetState": Qt.ItemDataRole.UserRole + 8,
    }
    assert model.data(first_index, roles["name"]) == "extruder"
    assert model.data(first_index, roles["displayName"]) == "Extruder"
    assert model.data(first_index, roles["icon"]) == "extruder"
    assert model.rowData(0) == {
        "name": "extruder",
        "displayName": "Extruder",
        "icon": "extruder",
        "temperature": None,
        "target": None,
        "graphVisible": True,
        "targetPending": False,
        "targetState": "actual",
    }


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


def test_temperature_device_list_model_updates_existing_devices_without_model_reset(
    qtbot,
) -> None:
    model = TemperatureDeviceListModel()
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
    resets: list[bool] = []
    changes: list[tuple[int, int, list[int]]] = []
    model.modelReset.connect(lambda: resets.append(True))
    model.dataChanged.connect(
        lambda top_left, bottom_right, roles: changes.append(
            (top_left.row(), bottom_right.row(), list(roles))
        )
    )

    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder", "heater_bed"),
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
                        temperature=58.0,
                        target=60.0,
                    ),
                ),
            )
        )

    assert resets == []
    assert changes == [
        (
            0,
            0,
            [
                model.TEMPERATURE_ROLE,
                model.TARGET_ROLE,
            ],
        )
    ]
    assert model.rowData(0)["temperature"] == 212.0
    assert model.rowData(0)["target"] == 220.0
    assert model.extruderSeries == [210.0, 212.0]


def test_temperature_device_list_model_resets_when_device_structure_changes(qtbot) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
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
    )

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder", "heater_bed"),
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
                        temperature=58.0,
                        target=60.0,
                    ),
                ),
            )
        )

    assert model.rowCount() == 2


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


def test_temperature_device_list_model_downsamples_large_temperature_store_for_graph(
    qtbot,
) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder",),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=239.0,
                    target=240.0,
                ),
            ),
        )
    )

    model.initialize_history(
        {
            "extruder": {
                "temperatures": [float(value) for value in range(1200)],
                "targets": [240.0 for _ in range(1200)],
            },
        }
    )

    series = model.graphSeriesModel[0]["series"]
    target_series = model.graphSeriesModel[1]["series"]

    assert len(series) == 240
    assert series[0] == 0.0
    assert series[-1] == 1199.0
    assert len(target_series) == 240


def test_status_model_suppresses_graph_series_updates_when_graph_panel_is_inactive(
    qtbot,
) -> None:
    temperature_model = TemperatureDeviceListModel()
    model = StatusModel(temperature_device_model=temperature_model)
    model.set_status(
        PrinterStatus(
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
    )
    model.setActivePanel("print")
    graph_changes: list[bool] = []
    temperature_model.graphSeriesChanged.connect(lambda: graph_changes.append(True))

    model.set_status(
        PrinterStatus(
            objects=("extruder",),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
            ),
        )
    )

    assert graph_changes == []

    with qtbot.waitSignal(temperature_model.graphSeriesChanged, timeout=1000):
        model.setActivePanel("main")


def test_temperature_device_list_model_caches_graph_series_until_graph_data_changes(
    qtbot,
) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
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
    )

    first_series = model.graphSeriesModel
    second_series = model.graphSeriesModel

    assert first_series is second_series

    with qtbot.waitSignal(model.graphSeriesChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder",),
                temperature_devices=(
                    TemperatureDeviceStatus(
                        name="extruder",
                        display_name="Extruder",
                        icon="extruder",
                        temperature=212.0,
                        target=215.0,
                    ),
                ),
            )
        )

    updated_series = model.graphSeriesModel

    assert updated_series is not first_series
    assert updated_series is model.graphSeriesModel
    assert updated_series[0]["series"] == [210.0, 212.0]


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


def test_temperature_device_list_model_uses_latest_stored_target_when_status_target_is_missing(
    qtbot,
) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder",),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=None,
                ),
            ),
        )
    )
    model.initialize_history(
        {
            "extruder": {
                "temperatures": [200.0, 205.0, 210.0],
                "targets": [0.0, 220.0, 220.0],
            },
        }
    )

    assert model.rowData(0)["target"] == 220.0
    assert [item["name"] for item in model.graphSeriesModel] == [
        "extruder",
        "extruder_target",
    ]
    assert model.graphSeriesModel[1]["series"] == [None, 220.0, 220.0]


def test_temperature_device_list_model_tracks_pending_target_locally(qtbot) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder",),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
            ),
        )
    )

    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        model.setPendingTarget("extruder", 230.0)

    assert model.rowData(0)["target"] == 230.0
    assert model.rowData(0)["targetPending"] is True
    assert model.rowData(0)["targetState"] == "pending"
    assert [item["name"] for item in model.graphSeriesModel] == ["extruder", "extruder_target"]
    assert model.graphSeriesModel[1]["series"] == [215.0]

    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder",),
                temperature_devices=(
                    TemperatureDeviceStatus(
                        name="extruder",
                        display_name="Extruder",
                        icon="extruder",
                        temperature=212.0,
                        target=230.0,
                    ),
                ),
            )
        )

    assert model.rowData(0)["target"] == 230.0
    assert model.rowData(0)["targetPending"] is False
    assert model.rowData(0)["targetState"] == "actual"


def test_temperature_device_list_model_real_target_overrides_pending_target(qtbot) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder",),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
            ),
        )
    )
    model.setPendingTarget("extruder", 230.0)

    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder",),
                temperature_devices=(
                    TemperatureDeviceStatus(
                        name="extruder",
                        display_name="Extruder",
                        icon="extruder",
                        temperature=212.0,
                        target=0.0,
                    ),
                ),
            )
        )

    assert model.rowData(0)["target"] == 0.0
    assert model.rowData(0)["targetPending"] is False
    assert model.rowData(0)["targetState"] == "actual"


def test_temperature_device_list_model_tracks_failed_target_until_real_target_arrives(
    qtbot,
) -> None:
    model = TemperatureDeviceListModel()
    model.set_status(
        PrinterStatus(
            objects=("extruder",),
            temperature_devices=(
                TemperatureDeviceStatus(
                    name="extruder",
                    display_name="Extruder",
                    icon="extruder",
                    temperature=212.0,
                    target=215.0,
                ),
            ),
        )
    )

    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        model.setFailedTarget("extruder", 230.0)

    assert model.rowData(0)["target"] == 230.0
    assert model.rowData(0)["targetPending"] is False
    assert model.rowData(0)["targetState"] == "failed"

    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        model.set_status(
            PrinterStatus(
                objects=("extruder",),
                temperature_devices=(
                    TemperatureDeviceStatus(
                        name="extruder",
                        display_name="Extruder",
                        icon="extruder",
                        temperature=212.0,
                        target=215.0,
                    ),
                ),
            )
        )

    assert model.rowData(0)["target"] == 215.0
    assert model.rowData(0)["targetState"] == "actual"


def test_temperature_device_list_model_suppresses_target_series_without_active_target(
    qtbot,
) -> None:
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
                    target=0.0,
                ),
                TemperatureDeviceStatus(
                    name="heater_bed",
                    display_name="Heater Bed",
                    icon="bed",
                    temperature=59.0,
                    target=None,
                ),
            ),
        )
    )
    model.initialize_history(
        {
            "extruder": {
                "temperatures": [200.0, 205.0, 210.0],
                "targets": [220.0, 220.0, 0.0],
            },
            "heater_bed": {
                "temperatures": [50.0, 55.0, 58.0],
                "targets": [60.0, 60.0, 0.0],
            },
        }
    )

    assert [item["name"] for item in model.graphSeriesModel] == [
        "extruder",
        "heater_bed",
    ]


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
