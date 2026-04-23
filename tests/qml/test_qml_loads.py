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
    assert "Grid {" in qml
    assert "rows: root.vertical ? root.buttonLabels.length : 1" in qml
    assert "columns: root.vertical ? 1 : root.buttonLabels.length" in qml
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
    assert "source: Theme.iconSource(iconName)" in qml
    assert 'text: temperature + "°"' in qml
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
        qml_dir / "components" / "MenuTile.qml",
        qml_dir / "components" / "TemperatureSummary.qml",
        qml_dir / "components" / "FakeTemperatureGraph.qml",
        qml_dir / "models" / "MainMenuModel.qml",
        qml_dir / "models" / "TemperatureDeviceModel.qml",
        qml_dir / "panels" / "PlaceholderPanel.qml",
        qml_dir / "panels" / "TemperaturePanel.qml",
    ]

    missing = [path for path in expected if not path.exists()]

    assert missing == []


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
    assert 'ListElement { deviceName: "Extruder"; iconName: "extruder"; temperature: "21" }' in qml
    assert 'ListElement { deviceName: "Heater bed"; iconName: "bed"; temperature: "25" }' in qml
    assert 'ListElement { deviceName: "Pi"; iconName: "heat-up"; temperature: "44" }' in qml
    assert "TemperatureDeviceModel {" in component_qml
    assert "id: fallbackTemperatureModel" in component_qml
    assert 'typeof icon === "undefined" ? iconName : icon' in component_qml
    assert 'typeof displayName === "undefined" ? deviceName : displayName' in component_qml
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
    assert "TemperatureSummary {" in qml
    assert "FakeTemperatureGraph {" in qml
    assert "model: root.activeTemperatureModel" in qml
    assert 'typeof icon === "undefined" ? iconName : icon' in qml
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
