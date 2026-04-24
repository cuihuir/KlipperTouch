import ast
from pathlib import Path

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


def test_main_qml_loads(qapp) -> None:
    engine = QQmlApplicationEngine()
    qml_path = Path("src/klippertouch/qml/main.qml").resolve()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    assert engine.rootObjects()


def test_action_bar_has_at_most_four_shell_buttons() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")
    marker = "property var buttonLabels:"
    model_line = next(line for line in qml.splitlines() if marker in line)
    model = ast.literal_eval(model_line.split(marker, maxsplit=1)[1].strip())

    assert len(model) <= 4


def test_action_bar_uses_klipperscreen_icon_names() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")

    assert 'property var buttonIcons: ["back", "main", "settings", "emergency"]' in qml
    assert 'property var buttonActions: ["back", "home", "menu", "stop"]' in qml
    assert "source: Theme.iconSource(modelData)" in qml
    assert "Button {" not in qml


def test_action_bar_uses_material_dark_icon_tiles() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")

    assert "signal actionRequested(string actionName)" in qml
    assert "id: iconButton" in qml
    assert "color: Theme.buttonsBg" in qml
    assert "radius: Math.round(Math.min(width, height) * 0.18)" in qml
    assert "border.color: Theme.actionBarBg" in qml
    assert "anchors.centerIn: parent" in qml
    assert "onClicked: root.actionRequested(root.buttonActions[index])" in qml


def test_action_bar_buttons_fill_available_axis() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")

    assert "Flow {" not in qml
    assert "Grid {" not in qml
    assert "id: buttonGrid" in qml
    assert "property int buttonCount: 4" in qml
    assert "x: root.vertical ? 0 : index * (buttonGrid.cellWidth + buttonGrid.spacing)" in qml
    assert "y: root.vertical ? index * (buttonGrid.cellHeight + buttonGrid.spacing) : 0" in qml
    assert "height: buttonGrid.cellHeight" in qml
    assert "width: buttonGrid.cellWidth" in qml


def test_material_dark_svg_assets_are_vendored() -> None:
    images = Path("src/klippertouch/qml/assets/material-dark/images")
    expected = {
        "back.svg",
        "bed.svg",
        "emergency.svg",
        "extruder.svg",
        "extrude.svg",
        "heat-up.svg",
        "main.svg",
        "move.svg",
        "printer.svg",
        "settings.svg",
    }

    assert {path.name for path in images.glob("*.svg")} == expected


def test_qml_theme_library_centralizes_material_dark_tokens() -> None:
    theme = Path("src/klippertouch/qml/Theme.js").read_text(encoding="utf-8")

    assert ".pragma library" in theme
    assert 'var bg = "#121212"' in theme
    assert 'var buttonsBg = "#090909"' in theme
    assert 'var titleBarBg = "#1f252b"' in theme
    assert 'var actionBarBg = "#2b3138"' in theme
    assert "function iconSource(iconName)" in theme
    assert 'return Qt.resolvedUrl("assets/material-dark/images/" + iconName + ".svg")' in theme


def test_core_qml_components_use_shared_theme_library() -> None:
    files = [
        Path("src/klippertouch/qml/components/ActionBar.qml"),
        Path("src/klippertouch/qml/components/BaseShell.qml"),
        Path("src/klippertouch/qml/components/MenuTile.qml"),
        Path("src/klippertouch/qml/components/StatusBar.qml"),
    ]

    for path in files:
        qml = path.read_text(encoding="utf-8")
        assert 'import "../Theme.js" as Theme' in qml or 'import "Theme.js" as Theme' in qml

    assert 'color: Theme.bg' in files[1].read_text(encoding="utf-8")
    assert 'color: Theme.buttonsBg' in files[2].read_text(encoding="utf-8")
    assert 'color: Theme.titleBarBg' in files[3].read_text(encoding="utf-8")


def test_status_bar_matches_klipperscreen_titlebar_structure() -> None:
    qml = Path("src/klippertouch/qml/components/StatusBar.qml").read_text(encoding="utf-8")

    assert 'import "../models"' in qml
    assert "property var temperatureModel: null" in qml
    assert "property var activeTemperatureModel:" in qml
    assert "property string printerName" in qml
    assert "property string panelTitle" in qml
    assert "property string clockText" in qml
    assert "id: heaterStrip" in qml
    assert "TemperatureDeviceModel {" in qml
    assert "id: fallbackTemperatureModel" in qml
    assert 'typeof icon === "undefined" ? iconName : icon' in qml
    assert "TemperatureIcon {" in qml
    assert "iconName: parent.resolvedIcon" in qml
    assert 'typeof temperature === "undefined" || temperature === null' in qml
    assert "model: root.activeTemperatureModel" in qml
    assert "id: titleLabel" in qml
    assert "id: clockLabel" in qml
    assert 'text: root.printerName + " | " + root.panelTitle' in qml
    assert "♨" not in qml
    assert "▥" not in qml


def test_fake_temperature_graph_matches_heater_graph_structure() -> None:
    qml = Path("src/klippertouch/qml/components/FakeTemperatureGraph.qml").read_text(
        encoding="utf-8"
    )

    assert 'import "../Theme.js" as Theme' in qml
    assert "id: horizontalGrid" in qml
    assert "id: verticalGrid" in qml
    assert "id: targetSegments" in qml
    assert "id: graphCanvas" in qml
    assert "onPaint:" in qml
    assert "drawSeries(ctx, extruderSeries, Theme.color2)" in qml
    assert "drawSeries(ctx, bedSeries, Theme.color1)" in qml
    assert "function normalizeTemperature" in qml
    assert "property real maxTemperature: 300" in qml
    assert "property var extruderSeries: []" in qml


def test_shell_has_responsive_orientation_hooks() -> None:
    metrics_qml = Path("src/klippertouch/qml/Metrics.qml").read_text(encoding="utf-8")
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(encoding="utf-8")
    action_bar_qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(
        encoding="utf-8"
    )

    assert "property bool portrait" in metrics_qml
    assert "property real fontSize" in metrics_qml
    assert "property int actionBarWidth" in metrics_qml
    assert "property int contentHeight" in metrics_qml
    assert "anchors.bottom: root.metrics.portrait ? parent.bottom : undefined" in shell_qml
    assert "property bool vertical" in action_bar_qml


def test_responsive_layout_components_exist() -> None:
    qml_dir = Path("src/klippertouch/qml")
    expected = [
        qml_dir / "Metrics.qml",
        qml_dir / "components" / "BaseShell.qml",
        qml_dir / "panels" / "MainMenuPanel.qml",
        qml_dir / "panels" / "MoreMenuPanel.qml",
        qml_dir / "components" / "MenuTile.qml",
        qml_dir / "components" / "TemperatureIcon.qml",
        qml_dir / "components" / "TemperatureSummary.qml",
        qml_dir / "components" / "FakeTemperatureGraph.qml",
        qml_dir / "models" / "MainMenuModel.qml",
        qml_dir / "models" / "MoreMenuModel.qml",
        qml_dir / "models" / "TemperatureDeviceModel.qml",
        qml_dir / "panels" / "PlaceholderPanel.qml",
        qml_dir / "panels" / "TemperaturePanel.qml",
        qml_dir / "panels" / "FilesPanel.qml",
        qml_dir / "panels" / "JobStatusPanel.qml",
        qml_dir / "panels" / "InfoPanel.qml",
        qml_dir / "panels" / "MovePanel.qml",
        qml_dir / "panels" / "ExtrudePanel.qml",
    ]

    missing = [path for path in expected if not path.exists()]

    assert missing == []


def test_files_panel_is_only_read_only_file_management() -> None:
    qml = Path("src/klippertouch/qml/panels/FilesPanel.qml").read_text(encoding="utf-8")

    assert "property var fileModel" in qml
    assert "G-Code files" in qml
    assert 'property string rootPath: "gcodes"' in qml
    assert "Sort: Name" in qml
    assert "Sort: Date" in qml
    assert "Sort: Size" in qml
    assert "No G-Code files found" in qml
    assert "Loading files..." in qml
    assert "function currentPathLabel" in qml
    assert "function emptyTitle" in qml
    assert "Current folder is empty" in qml
    assert 'fileList.count + " items"' in qml
    assert "Search files" in qml
    assert "activeFileModel.setFilterText(text)" in qml
    assert "activeFileModel.setBreadcrumbIndex(index)" in qml
    assert "activeFileModel.breadcrumbs" in qml
    assert "text: modelData" in qml
    assert "required property bool isDirectory" in qml
    assert "required property string modifiedLabel" in qml
    assert "activeFileModel.canGoUp" in qml
    assert "activeFileModel.setCurrentPath(path)" in qml
    assert "activeFileModel.setSortKey(sortKey)" in qml
    assert "activeFileModel.goUp()" in qml
    assert "property string printState" not in qml
    assert "property string printFilename" not in qml
    assert "property real printProgress" not in qml
    assert "ProgressBar" not in qml
    assert 'text: "Start"' not in qml
    assert 'text: "Pause"' not in qml
    assert 'text: "Cancel"' not in qml


def test_job_status_panel_is_separate_from_files_panel_and_read_only() -> None:
    qml = Path("src/klippertouch/qml/panels/JobStatusPanel.qml").read_text(encoding="utf-8")

    assert "property string printState" in qml
    assert "property string printFilename" in qml
    assert "property real printProgress" in qml
    assert "property string printMessage" in qml
    assert "ProgressBar" in qml
    assert "root.printProgress / 100" in qml
    assert "property real filamentUsed" in qml
    assert "property int currentLayer" in qml
    assert "property int totalLayers" in qml
    assert "property real requestedSpeed" in qml
    assert "property real speedFactor" in qml
    assert "property real extrudeFactor" in qml
    assert "property real zOffset" in qml
    assert "property real maxAccel" in qml
    assert "property real maxVelocity" in qml
    assert "property var temperatureModel: null" in qml
    assert "property var fileModel: null" in qml
    assert "root.fileModel.fileSizeLabelFor(root.printFilename)" in qml
    assert "root.fileModel.fileModifiedLabelFor(root.printFilename)" in qml
    assert "root.fileModel.filePathFor(root.printFilename)" in qml
    assert "File size" in qml
    assert "Modified" in qml
    assert "Path" in qml
    assert "model: root.temperatureModel" in qml
    assert "Temperatures" in qml
    assert "required property var temperature" in qml
    assert "required property var target" in qml
    assert 'typeof target === "undefined" || target === null' in qml
    assert 'typeof temperature === "undefined" || temperature === null' in qml
    assert "root.filamentLabel()" in qml
    assert "root.layerLabel()" in qml
    assert "function remainingLabel" in qml
    assert "function stateHeadline" in qml
    assert "function stateMessage" in qml
    assert "function stateAccentColor" in qml
    assert 'if (root.printState === "paused")' in qml
    assert 'if (root.printState === "complete")' in qml
    assert 'if (root.printState === "cancelled")' in qml
    assert 'if (root.printState === "error")' in qml
    assert "Paused" in qml
    assert "Cancelled" in qml
    assert "Completed" in qml
    assert "Printer error" in qml
    assert "Remaining" in qml
    assert "root.percentLabel(root.speedFactor)" in qml
    assert "root.zOffsetLabel()" in qml
    assert 'text: "Start"' not in qml
    assert 'text: "Pause"' not in qml
    assert 'text: "Cancel"' not in qml
    assert "printer.print." not in qml
    assert "printer.gcode.script" not in qml


def test_move_panel_exposes_read_only_position_without_controls() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "property real positionX" in qml
    assert "property real positionY" in qml
    assert "property real positionZ" in qml
    assert "property real positionE" in qml
    assert "property string homedAxes" in qml
    assert "root.positionX.toFixed(2)" in qml
    assert "root.homedAxes.length > 0" in qml
    assert "MouseArea" not in qml
    assert "printer.gcode.script" not in qml


def test_extrude_panel_exposes_read_only_extruder_state_without_controls() -> None:
    qml = Path("src/klippertouch/qml/panels/ExtrudePanel.qml").read_text(encoding="utf-8")

    assert "property real extruderTemperature" in qml
    assert "property real extruderTarget" in qml
    assert "property real positionE" in qml
    assert "root.extruderTemperature.toFixed(1)" in qml
    assert "root.extruderTarget.toFixed(1)" in qml
    assert "root.positionE.toFixed(2)" in qml
    assert "MouseArea" not in qml
    assert "printer.gcode.script" not in qml

    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "property real extruderTemperature:" in main_qml
    assert "property real extruderTarget:" in main_qml
    assert "extruderTemperature: window.extruderTemperature" in main_qml
    assert "extruderTarget: window.extruderTarget" in main_qml


def test_info_panel_exposes_read_only_versions_and_mcu_lists() -> None:
    qml = Path("src/klippertouch/qml/panels/InfoPanel.qml").read_text(encoding="utf-8")

    assert "property var mcuInfos" in qml
    assert "property var serviceVersions" in qml
    assert "ListView" in qml
    assert "model: root.mcuInfos" in qml
    assert "model: root.serviceVersions" in qml
    assert "No MCU version data" in qml
    assert "No service version data" in qml
    assert "MCU information" in qml
    assert "Service versions" in qml

    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "property var mcuInfos:" in main_qml
    assert "property var serviceVersions:" in main_qml
    assert "mcuInfos: window.mcuInfos" in main_qml
    assert "serviceVersions: window.serviceVersions" in main_qml


def test_more_menu_panel_uses_icon_list_entry_model() -> None:
    qml = Path("src/klippertouch/qml/panels/MoreMenuPanel.qml").read_text(encoding="utf-8")
    model_qml = Path("src/klippertouch/qml/models/MoreMenuModel.qml").read_text(encoding="utf-8")
    main_model_qml = Path("src/klippertouch/qml/models/MainMenuModel.qml").read_text(
        encoding="utf-8"
    )

    assert 'import "../models"' in qml
    assert "signal panelRequested(string panelName)" in qml
    assert "MoreMenuModel {" in qml
    assert "MenuTile {" in qml
    assert "onActivated: root.panelRequested(panelName)" in qml
    assert 'ListElement { tileLabel: "More"; tileIcon: "settings"' in main_model_qml
    assert 'panelName: "more"' in main_model_qml
    assert 'panelName: "system"' not in main_model_qml
    assert 'panelName: "network"' not in main_model_qml
    assert 'panelName: "logs"' not in main_model_qml
    assert 'ListElement { tileLabel: "System"; tileIcon: "settings"' in model_qml
    assert 'ListElement { tileLabel: "Network"; tileIcon: "main"' in model_qml
    assert 'ListElement { tileLabel: "Logs"; tileIcon: "printer"' in model_qml
    assert 'ListElement { tileLabel: "Language"; tileIcon: "settings"' in model_qml
    assert 'ListElement { tileLabel: "Update"; tileIcon: "printer"' in model_qml
    assert 'panelName: "language"' in model_qml
    assert 'panelName: "update"' in model_qml
    assert 'panelName: "system"' in model_qml
    assert 'panelName: "network"' in model_qml
    assert 'panelName: "logs"' in model_qml
    assert 'ListElement { tileLabel: "System"' in model_qml


def test_main_menu_matches_klipperscreen_split_and_autogrid_contract() -> None:
    qml = Path("src/klippertouch/qml/panels/MainMenuPanel.qml").read_text(encoding="utf-8")

    assert "property int virtualRows: 5" in qml
    assert "property int temperatureRows: 3" in qml
    assert "property int menuRows: 2" in qml
    assert "property int landscapeMenuRows: 3" in qml
    assert "property real landscapeTemperatureFraction: 0.5" in qml
    assert "width: root.metrics.portrait" in qml
    assert "height: root.metrics.portrait ? root.temperaturePanelHeight" in qml
    assert "columns: root.metrics.portrait ? 3 : 2" in qml
    assert "rows: root.metrics.portrait ? root.menuRows : root.landscapeMenuRows" in qml
    assert "Layout.columnSpan: root.shouldExpandLastTile(index) ? 2 : 1" in qml


def test_main_menu_uses_klipperscreen_default_top_level_items() -> None:
    qml = Path("src/klippertouch/qml/models/MainMenuModel.qml").read_text(encoding="utf-8")
    panel_qml = Path("src/klippertouch/qml/panels/MainMenuPanel.qml").read_text(
        encoding="utf-8"
    )

    assert 'tileLabel: "Move"; tileIcon: "move"; tileAccent: "#d46900"' in qml
    assert (
        'tileLabel: "Temperature"; tileIcon: "heat-up"; '
        'tileAccent: "#ed3c63"'
    ) in qml
    assert 'tileLabel: "Extrude"; tileIcon: "extrude"; tileAccent: "#849900"' in qml
    assert 'tileLabel: "More"; tileIcon: "settings"; tileAccent: "#007db4"' in qml
    assert 'tileLabel: "Print"; tileIcon: "printer"; tileAccent: "#d46900"' in qml
    assert 'panelName: "move"' in qml
    assert 'panelName: "temperature"' in qml
    assert 'panelName: "extrude"' in qml
    assert 'panelName: "more"' in qml
    assert 'panelName: "print"' in qml
    assert 'import "../models"' in panel_qml
    assert "MainMenuModel {" in panel_qml
    assert "ListElement { tileLabel:" not in panel_qml


def test_menu_tile_uses_material_dark_button_and_svg_icon() -> None:
    qml = Path("src/klippertouch/qml/components/MenuTile.qml").read_text(encoding="utf-8")

    assert "signal activated()" in qml
    assert "MouseArea {" in qml
    assert "onClicked: root.activated()" in qml
    assert "color: Theme.buttonsBg" in qml
    assert "border.color: root.accent" in qml
    assert "radius: Math.round(root.fontSize)" in qml
    assert "source: Theme.iconSource(root.iconText)" in qml


def test_main_menu_requests_safe_local_panels() -> None:
    qml = Path("src/klippertouch/qml/panels/MainMenuPanel.qml").read_text(encoding="utf-8")
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "signal panelRequested(string panelName)" in qml
    assert "required property string panelName" in qml
    assert "onActivated: root.panelRequested(panelName)" in qml
    assert "function showPanel(panelName)" in main_qml
    assert "currentPanel = panelName" in main_qml
    assert "onPanelRequested: function(panelName) { window.showPanel(panelName) }" in main_qml
    assert "printer.gcode.script" not in qml
    assert "printer.gcode.script" not in main_qml


def test_main_maintains_safe_local_panel_navigation_stack() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'property var panelStack: ["main"]' in main_qml
    assert "panelStack[panelStack.length - 1] !== panelName" in main_qml
    assert "var nextStack = panelStack.slice()" in main_qml
    assert "nextStack.push(panelName)" in main_qml
    assert "panelStack = nextStack" in main_qml
    assert 'panelStack = ["main"]' in main_qml
    assert "panelStack.slice(0, panelStack.length - 1)" in main_qml
    assert "currentPanel = panelStack[panelStack.length - 1]" in main_qml


def test_action_bar_requests_safe_local_navigation() -> None:
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(encoding="utf-8")
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "signal backRequested()" in shell_qml
    assert "signal homeRequested()" in shell_qml
    assert "signal menuRequested()" in shell_qml
    assert "onActionRequested:" in shell_qml
    assert "case \"back\":" in shell_qml
    assert "case \"home\":" in shell_qml
    assert "case \"menu\":" in shell_qml
    assert "case \"stop\":" in shell_qml
    assert "break" in shell_qml
    assert "function goBack()" in main_qml
    assert "onBackRequested: window.goBack()" in main_qml
    assert "onHomeRequested: window.goHome()" in main_qml
    assert 'onMenuRequested: window.showPanel("more")' in main_qml
    assert "emergency" not in main_qml.lower()
    assert "printer.gcode.script" not in shell_qml


def test_temperature_summary_uses_klipperscreen_device_icons_and_theme() -> None:
    qml = Path("src/klippertouch/qml/models/TemperatureDeviceModel.qml").read_text(
        encoding="utf-8"
    )
    component_qml = Path("src/klippertouch/qml/components/TemperatureSummary.qml").read_text(
        encoding="utf-8"
    )

    assert 'import "../Theme.js" as Theme' in component_qml
    assert 'import "../models"' in component_qml
    assert "property var temperatureModel: null" in component_qml
    assert "property var activeTemperatureModel:" in component_qml
    assert "clip: true" in component_qml
    assert 'ListElement { deviceName: "Extruder"; iconName: "extruder"; temperature: "21" }' in qml
    assert 'ListElement { deviceName: "Heater bed"; iconName: "bed"; temperature: "25" }' in qml
    assert 'ListElement { deviceName: "Pi"; iconName: "heat-up"; temperature: "44" }' in qml
    assert "TemperatureDeviceModel {" in component_qml
    assert "id: fallbackTemperatureModel" in component_qml
    assert 'typeof icon === "undefined" ? iconName : icon' in component_qml
    assert 'typeof displayName === "undefined" ? deviceName : displayName' in component_qml
    assert 'typeof temperature === "undefined" || temperature === null' in component_qml
    assert "TemperatureIcon {" in component_qml
    assert "iconName: parent.resolvedIcon" in component_qml
    assert "model: root.activeTemperatureModel" in component_qml
    assert "color: Theme.text" in component_qml
    assert "color: Theme.mutedText" in component_qml
    assert "ListElement { deviceName:" not in component_qml


def test_temperature_model_is_passed_from_app_to_shell_and_main_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(encoding="utf-8")
    panel_qml = Path("src/klippertouch/qml/panels/MainMenuPanel.qml").read_text(
        encoding="utf-8"
    )

    assert (
        'property var temperatureBridgeModel: typeof temperatureDeviceModel === "undefined" '
        "? null : temperatureDeviceModel"
    ) in main_qml
    assert "temperatureModel: window.temperatureBridgeModel" in main_qml
    assert "property var temperatureModel: null" in shell_qml
    assert "temperatureModel: root.temperatureModel" in shell_qml
    assert "property var temperatureModel: null" in panel_qml
    assert "temperatureModel: root.temperatureModel" in panel_qml


def test_temperature_panel_is_read_only_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/TemperaturePanel.qml").read_text(
        encoding="utf-8"
    )

    assert "required property var metrics" in qml
    assert "property var temperatureModel: null" in qml
    assert "TemperatureSummary {" not in qml
    assert "FakeTemperatureGraph {" in qml
    assert "extruderSeries: root.activeTemperatureModel.extruderSeries" in qml
    assert "bedSeries: root.activeTemperatureModel.bedSeries" in qml
    assert "model: root.activeTemperatureModel" in qml
    assert "Layout.minimumWidth: 0" in qml
    assert "Layout.minimumHeight: 0" in qml
    assert 'typeof icon === "undefined" ? iconName : icon' in qml
    assert "TemperatureIcon {" in qml
    assert "iconName: resolvedIcon" in qml
    assert 'typeof displayName === "undefined" ? deviceName : displayName' in qml
    assert 'typeof target === "undefined" || target === null' in qml
    assert 'typeof temperature === "undefined" || temperature === null' in qml
    assert "root.metrics.portrait" in qml
    assert "readonly" in qml
    assert "printer.gcode.script" not in qml
    assert "sendTextMessage" not in qml


def test_main_routes_temperature_to_read_only_temperature_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "function componentForPanel(panelName)" in main_qml
    assert 'case "main":' in main_qml
    assert 'case "temperature":' in main_qml
    assert "return temperatureComponent" in main_qml
    assert "return placeholderComponent" in main_qml
    assert "sourceComponent: window.componentForPanel(window.currentPanel)" in main_qml
    assert "TemperaturePanel {" in main_qml
    assert "temperatureModel: window.temperatureBridgeModel" in main_qml


def test_main_keeps_files_and_job_status_as_separate_routes() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert '"job_status": "Job Status"' in main_qml
    assert 'case "print":' in main_qml
    assert "return filesComponent" in main_qml
    assert 'case "job_status":' in main_qml
    assert "return jobStatusComponent" in main_qml
    assert "FilesPanel {" in main_qml
    assert "JobStatusPanel {" in main_qml
    assert "fileModel: window.gcodeFileBridgeModel" in main_qml
    assert "filamentUsed: window.filamentUsed" in main_qml
    assert "currentLayer: window.currentLayer" in main_qml
    assert "totalLayers: window.totalLayers" in main_qml
    assert "requestedSpeed: window.requestedSpeed" in main_qml
    assert "speedFactor: window.speedFactor" in main_qml
    assert "extrudeFactor: window.extrudeFactor" in main_qml
    assert "zOffset: window.zOffset" in main_qml
    assert "maxAccel: window.maxAccel" in main_qml
    assert "maxVelocity: window.maxVelocity" in main_qml
    assert "temperatureModel: window.temperatureBridgeModel" in main_qml
    assert "fileModel: window.gcodeFileBridgeModel" in main_qml
    assert "function shouldAutoEnterJobStatus()" in main_qml
    assert "function shouldKeepJobStatusVisible()" in main_qml
    assert "function syncJobStatusPanel()" in main_qml
    assert "onPrintStateChanged: window.syncJobStatusPanel()" in main_qml
    assert "Component.onCompleted: window.syncJobStatusPanel()" in main_qml
    assert 'window.currentPanel = "job_status"' in main_qml
    assert "PrintPanel {" not in main_qml


def test_main_keeps_job_status_visible_for_terminal_job_states() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'window.printState === "printing"' in main_qml
    assert 'window.printState === "paused"' in main_qml
    assert 'window.printState === "complete"' in main_qml
    assert 'window.printState === "cancelled"' in main_qml
    assert 'window.printState === "error"' in main_qml
    assert "if (window.shouldAutoEnterJobStatus())" in main_qml
    assert "else if (!window.shouldKeepJobStatusVisible()" in main_qml
    assert "window.goHome()" in main_qml


def test_files_panel_is_read_only_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/FilesPanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property var fileModel: null" in qml
    assert "model: root.activeFileModel" in qml
    assert "readonly" in qml
    assert "displayName" in qml
    assert "sizeLabel" in qml
    assert "root.metrics.portrait" in qml
    assert "MouseArea" in qml
    assert "activeFileModel.setCurrentPath(path)" in qml
    assert "printer.print.start" not in qml
    assert "printer.gcode.script" not in qml


def test_main_routes_print_to_read_only_files_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert (
        'property var gcodeFileBridgeModel: typeof gcodeFileModel === "undefined" '
        "? null : gcodeFileModel"
    ) in main_qml
    assert 'case "print":' in main_qml
    assert "return filesComponent" in main_qml
    assert "FilesPanel {" in main_qml
    assert "fileModel: window.gcodeFileBridgeModel" in main_qml


def test_info_panel_is_read_only_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/InfoPanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property string hostname" in qml
    assert "property string klippyState" in qml
    assert "property string klipperVersion" in qml
    assert "property string moonrakerVersion" in qml
    assert "property var mcuInfos" in qml
    assert "property var serviceVersions" in qml
    assert "MCU information" in qml
    assert "Service versions" in qml
    assert "Moonraker objects" not in qml
    assert "objectNames" not in qml
    assert "readonly" in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "printer.gcode.script" not in qml
    assert "MouseArea" not in qml


def test_main_routes_more_to_read_only_info_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'property string klipperVersion: bridgeModel ? bridgeModel.klipperVersion' in main_qml
    assert (
        "property string moonrakerVersion: bridgeModel ? bridgeModel.moonrakerVersion"
        in main_qml
    )
    assert 'case "more":' in main_qml
    assert "return moreMenuComponent" in main_qml
    assert 'case "system":' in main_qml
    assert "return infoComponent" in main_qml
    assert 'case "network":' in main_qml
    assert 'case "logs":' in main_qml
    assert 'case "language":' in main_qml
    assert 'case "update":' in main_qml
    assert '"language": "Language"' in main_qml
    assert '"update": "Update"' in main_qml
    assert "title: window.panelTitles[window.currentPanel]" in main_qml
    assert "iconName: window.panelIcons[window.currentPanel]" in main_qml
    assert '"more": "More"' in main_qml
    assert '"system": "System"' in main_qml
    assert '"network": "Network"' in main_qml
    assert '"logs": "Logs"' in main_qml
    assert "InfoPanel {" in main_qml
    assert "MoreMenuPanel {" in main_qml
    assert "hostname: window.hostname" in main_qml
    assert "klippyState: window.klippyState" in main_qml
    assert "klipperVersion: window.klipperVersion" in main_qml
    assert "moonrakerVersion: window.moonrakerVersion" in main_qml
    assert "mcuInfos: window.mcuInfos" in main_qml
    assert "serviceVersions: window.serviceVersions" in main_qml


def test_main_routes_network_and_logs_to_safe_placeholder_panels() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'case "network":' in main_qml
    assert 'case "logs":' in main_qml
    assert 'case "language":' in main_qml
    assert 'case "update":' in main_qml
    assert '"language": "settings"' in main_qml
    assert '"update": "printer"' in main_qml
    assert "return placeholderComponent" in main_qml
    assert '"network": "main"' in main_qml
    assert '"logs": "printer"' in main_qml


def test_move_panel_is_locked_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property var axes" in qml
    assert "property var distances" in qml
    assert "Controls locked" in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "MouseArea" not in qml
    assert "printer.gcode.script" not in qml
    assert "G1" not in qml
    assert "G28" not in qml


def test_extrude_panel_is_locked_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/ExtrudePanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property var distances" in qml
    assert "property var speeds" in qml
    assert "property real actionFraction: 0.42" in qml
    assert "property real settingsFraction: 0.58" in qml
    assert "Layout.preferredWidth: root.metrics.portrait" in qml
    assert "Layout.minimumWidth: 0" in qml
    assert "Extrusion locked" in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "MouseArea" not in qml
    assert "printer.gcode.script" not in qml
    assert "M83" not in qml
    assert "G1" not in qml


def test_main_routes_move_and_extrude_to_locked_panels() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'case "move":' in main_qml
    assert "return moveComponent" in main_qml
    assert 'case "extrude":' in main_qml
    assert "return extrudeComponent" in main_qml
    assert "MovePanel {" in main_qml
    assert "ExtrudePanel {" in main_qml


def test_main_uses_responsive_base_shell_and_main_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "BaseShell {" in main_qml
    assert "Loader {" in main_qml
    assert "Metrics {" in main_qml
    assert 'property string currentPanel: "main"' in main_qml
    assert 'property var panelTitles: ({"main": "Home"' in main_qml
    assert "panelTitle: window.panelTitles[window.currentPanel]" in main_qml
    assert (
        "sourceComponent: window.componentForPanel(window.currentPanel)"
    ) in main_qml


def test_placeholder_panel_supports_safe_empty_pages() -> None:
    qml = Path("src/klippertouch/qml/panels/PlaceholderPanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "required property string title" in qml
    assert "required property string iconName" in qml
    assert "No printer commands are enabled on this screen yet." in qml
    assert "Theme.iconSource(root.iconName)" in qml


@pytest.mark.parametrize(("width", "height"), [(800, 480), (1024, 600), (480, 800)])
def test_main_qml_loads_common_screen_shapes(qapp, width: int, height: int) -> None:
    engine = QQmlApplicationEngine()
    qml_path = Path("src/klippertouch/qml/main.qml").resolve()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    assert engine.rootObjects()

    root = engine.rootObjects()[0]
    root.setProperty("width", width)
    root.setProperty("height", height)
    qapp.processEvents()

    assert root.property("width") == width
    assert root.property("height") == height
