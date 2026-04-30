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


def test_main_qml_supports_context_controlled_fullscreen() -> None:
    qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "import QtQuick.Window" in qml
    assert "width: window.startFullScreen ? Screen.width : 1024" in qml
    assert "height: window.startFullScreen ? Screen.height : 600" in qml
    assert "property bool startFullScreen:" in qml
    assert 'typeof configuredFullScreen === "undefined" ? false : configuredFullScreen' in qml
    assert "visibility: window.startFullScreen ? Window.FullScreen : Window.Windowed" in qml


def test_main_qml_supports_context_controlled_read_only_mode() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")
    files_qml = Path("src/klippertouch/qml/panels/FilesPanel.qml").read_text(
        encoding="utf-8"
    )

    assert "property bool readOnlyMode:" in main_qml
    assert 'typeof configuredReadOnly === "undefined" ? true : configuredReadOnly' in main_qml
    assert "readOnlyMode: window.readOnlyMode" in main_qml
    assert "property bool readOnlyMode: true" in files_qml
    assert 'root.readOnlyMode ? "readonly" : "controls"' in files_qml
    assert 'root.readOnlyMode ? "Mode" : "Controls"' in files_qml
    assert "enabled: !root.readOnlyMode" in files_qml


def test_main_qml_supports_context_controlled_display_rotation() -> None:
    qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "property string displayRotation:" in qml
    assert (
        'typeof configuredDisplayRotation === "undefined" ? "" : configuredDisplayRotation'
        in qml
    )
    assert "property bool displayRotated:" in qml
    assert "property int sceneWidth: window.displayRotated ? window.height : window.width" in qml
    assert "property int sceneHeight: window.displayRotated ? window.width : window.height" in qml
    assert "viewportWidth: window.sceneWidth" in qml
    assert "viewportHeight: window.sceneHeight" in qml
    assert "id: sceneRoot" in qml
    assert "width: window.sceneWidth" in qml
    assert "height: window.sceneHeight" in qml
    assert "rotation: window.displayRotation === \"right\" ? 90" in qml


def test_numeric_editor_popups_are_parented_inside_rotated_scene() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")
    qml_paths = [
        Path("src/klippertouch/qml/components/TemperatureDevicePager.qml"),
        Path("src/klippertouch/qml/panels/ExtrudePanel.qml"),
    ]

    assert "id: scenePopupLayer" in main_qml
    assert "popupParent: scenePopupLayer" in main_qml

    for qml_path in qml_paths:
        qml = qml_path.read_text(encoding="utf-8")

        assert "Popup {" not in qml
        assert "parent: Overlay.overlay" not in qml
        assert "property Item popupParent: null" in qml
        assert "parent: root.popupParent === null ? root : root.popupParent" in qml
        assert "property real dialogWidth:" in qml
        assert "function open()" in qml
        assert "function close()" in qml


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
    assert (
        'color: root.navigationEnabled && actionPressArea.pressed ? "#182124"'
        " : Theme.buttonsBg"
    ) in qml
    assert "radius: Math.round(Math.min(width, height) * 0.18)" in qml
    assert (
        "border.color: root.navigationEnabled && actionPressArea.pressed"
        " ? Theme.text : Theme.actionBarBg"
    ) in qml
    assert "anchors.centerIn: parent" in qml
    assert "onClicked: root.actionRequested(root.buttonActions[index])" in qml


def test_action_bar_buttons_have_press_feedback() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")

    assert "id: actionPressArea" in qml
    assert "scale: root.navigationEnabled && actionPressArea.pressed ? 0.96 : 1.0" in qml
    assert (
        'color: root.navigationEnabled && actionPressArea.pressed ? "#182124"'
        " : Theme.buttonsBg"
    ) in qml
    assert (
        "border.color: root.navigationEnabled && actionPressArea.pressed"
        " ? Theme.text : Theme.actionBarBg"
    ) in qml
    assert "Behavior on scale" in qml
    assert "NumberAnimation { duration: 80" in qml
    assert "ColorAnimation { duration: 80" in qml


def test_menu_tile_has_press_feedback() -> None:
    qml = Path("src/klippertouch/qml/components/MenuTile.qml").read_text(encoding="utf-8")

    assert "id: tilePressArea" in qml
    assert "scale: tilePressArea.pressed ? 0.97 : 1.0" in qml
    assert 'color: tilePressArea.pressed ? "#182124" : Theme.buttonsBg' in qml
    assert "border.color: tilePressArea.pressed ? Theme.text : root.accent" in qml
    assert "Behavior on scale" in qml
    assert "NumberAnimation { duration: 80" in qml
    assert "ColorAnimation { duration: 80" in qml


def test_tactile_button_centralizes_pressed_down_feedback() -> None:
    qml = Path("src/klippertouch/qml/components/TactileButton.qml").read_text(
        encoding="utf-8"
    )

    assert "Button {" in qml
    assert "property real fontSize" in qml
    assert "property color baseColor" in qml
    assert "property color pressedColor" in qml
    assert "property color accentColor" in qml
    assert "property string iconName" in qml
    assert 'source: control.iconName.length > 0 ? Theme.iconSource(control.iconName) : ""' in qml
    assert "visible: control.iconName.length > 0" in qml
    assert "scale: control.down && control.enabled ? 0.97 : 1.0" in qml
    assert "id: tactileDepth" in qml
    assert "id: tactileSurface" in qml
    assert "visible: !control.down && control.enabled" in qml
    assert "anchors.topMargin: control.down" in qml
    assert "anchors.bottomMargin: control.down ? 0" in qml
    assert "Behavior on scale" in qml
    assert "NumberAnimation { duration: 70" in qml


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
        "advanced.svg",
        "bed.svg",
        "cancel.svg",
        "clear.svg",
        "confirm.svg",
        "emergency.svg",
        "extruder.svg",
        "extrude.svg",
        "fan.svg",
        "heat-up.svg",
        "home.svg",
        "load.svg",
        "logs.svg",
        "language.svg",
        "length.svg",
        "main.svg",
        "material.svg",
        "motor-off.svg",
        "move.svg",
        "network.svg",
        "notification.svg",
        "object.svg",
        "pause.svg",
        "placeholder.svg",
        "power.svg",
        "printer.svg",
        "restart.svg",
        "resume.svg",
        "settings.svg",
        "speed.svg",
        "tilt.svg",
        "update.svg",
        "unload.svg",
    }

    assert {path.name for path in images.glob("*.svg")} == expected


def test_action_button_icon_contract_is_explicit() -> None:
    qml_paths = [
        Path("src/klippertouch/qml/panels/MovePanel.qml"),
        Path("src/klippertouch/qml/panels/ExtrudePanel.qml"),
        Path("src/klippertouch/qml/panels/SplashPanel.qml"),
    ]

    for qml_path in qml_paths:
        for line in qml_path.read_text(encoding="utf-8").splitlines():
            if '{"label":' in line and '"action":' in line and '"direction":' not in line:
                assert '"iconName":' in line, f"{qml_path}:{line.strip()}"

    job_qml = Path("src/klippertouch/qml/panels/JobStatusPanel.qml").read_text(
        encoding="utf-8"
    )
    files_qml = Path("src/klippertouch/qml/panels/FilesPanel.qml").read_text(
        encoding="utf-8"
    )
    tactile_qml = Path("src/klippertouch/qml/components/TactileButton.qml").read_text(
        encoding="utf-8"
    )

    assert 'iconName: modelData.delta < 0 ? "back" : "confirm"' in job_qml
    assert 'text: "Skip Selected"' in job_qml
    assert 'text: "Skip Current"' in job_qml
    assert 'iconName: "object"' in job_qml
    assert "component FileActionButton: TactileButton" in files_qml
    assert "component RetryButton: TactileButton" in files_qml
    assert "property string iconName" in tactile_qml
    assert "Theme.iconSource(control.iconName)" in tactile_qml


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
    assert 'color: tilePressArea.pressed ? "#182124" : Theme.buttonsBg' in files[2].read_text(
        encoding="utf-8"
    )
    assert 'color: Theme.titleBarBg' in files[3].read_text(encoding="utf-8")


def test_status_bar_matches_klipperscreen_titlebar_structure() -> None:
    qml = Path("src/klippertouch/qml/components/StatusBar.qml").read_text(encoding="utf-8")

    assert 'import "../models"' in qml
    assert "property var temperatureModel: null" in qml
    assert "property bool hasExternalTemperatureModel" in qml
    assert "property var activeTemperatureModel:" in qml
    assert "property string printerName" in qml
    assert "property string panelTitle" in qml
    assert "property string clockText" in qml
    assert "function updateClock()" in qml
    assert "function scheduleNextClockTick()" in qml
    assert "id: clockTimer" in qml
    assert "interval: 1000" not in qml
    assert "id: heaterStrip" in qml
    assert "root.width < 520 ? 0.25 : 0.35" in qml
    assert "root.width < 520 ? 0.45 : 0.32" in qml
    assert "property int maxVisibleTemperatureItems" in qml
    assert "root.width < 700 ? 2 : 4" in qml
    assert "index < root.maxVisibleTemperatureItems" in qml
    assert "TemperatureDeviceModel {" in qml
    assert "id: fallbackTemperatureModel" in qml
    assert 'typeof icon === "undefined" ? iconName : icon' in qml
    assert "TemperatureIcon {" in qml
    assert "iconName: parent.resolvedIcon" in qml
    assert 'typeof temperature === "undefined" || temperature === null' in qml
    assert "model: root.activeTemperatureModel" in qml
    assert "id: titleLabel" in qml
    assert "id: clockLabel" in qml
    assert "id: notificationArea" in qml
    assert "id: notificationPressArea" in qml
    assert "scale: notificationPressArea.pressed && root.interactionEnabled ? 0.97 : 1.0" in qml
    assert "Behavior on scale" in qml
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
    assert "id: graphCanvas" in qml
    assert "Canvas {" in qml
    assert "onPaint:" in qml
    assert "getContext(\"2d\")" in qml
    assert "function drawSeries(ctx, item, plotWidth, plotHeight)" in qml
    assert "ctx.setLineDash" in qml
    assert "property int visiblePointCount" in qml
    assert "property bool redrawPending" in qml
    assert "function visibleSeries(series)" in qml
    assert "property var seriesModel: []" in qml
    assert "function seriesPoints(series, plotWidth, plotHeight)" in qml
    assert "id: redrawTimer" in qml
    assert "interval: 1000" in qml
    assert "redrawTimer.start()" in qml
    assert 'currentSeries[i] === null || typeof currentSeries[i] === "undefined"' in qml
    assert "points.push(null)" in qml
    assert "hasActiveSegment = false" in qml
    assert "item.dashed" in qml
    assert "function segmentModel(" not in qml
    assert "graphContent.visible = false" not in qml
    assert "transformOrigin: Item.Left" not in qml
    assert "ctx.stroke()" in qml
    assert "id: legendViewport" in qml
    assert "Flickable {" in qml
    assert "contentWidth: legendRow.implicitWidth" in qml
    assert "anchors.left: parent.left" in qml
    assert "anchors.right: parent.right" not in qml
    assert "clip: true" in qml
    assert "elide: Text.ElideRight" in qml
    assert "modelData.legendVisible === false" in qml
    assert 'text: modelData.displayName' in qml
    assert "function normalizeTemperature" in qml
    assert "property real maxTemperature: 300" in qml
    assert "maxTemperatureLabel" in qml
    assert "midTemperatureLabel" in qml
    assert "baseTemperatureLabel" in qml


def test_shell_has_responsive_orientation_hooks() -> None:
    metrics_qml = Path("src/klippertouch/qml/Metrics.qml").read_text(encoding="utf-8")
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(encoding="utf-8")
    action_bar_qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(
        encoding="utf-8"
    )

    assert "property bool portrait" in metrics_qml
    assert "property bool ultraWide" in metrics_qml
    assert "viewportWidth / viewportHeight >= 3.0" in metrics_qml
    assert "viewportHeight <= 520" in metrics_qml
    assert "property real fontSize" in metrics_qml
    assert "property int actionBarWidth" in metrics_qml
    assert "property int contentHeight" in metrics_qml
    assert "anchors.bottom: root.metrics.portrait ? parent.bottom : undefined" in shell_qml
    assert "property bool vertical" in action_bar_qml


def test_move_bed_tilt_preview_uses_rectangular_bed_geometry() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "id: bedRectCanvas" in qml
    assert "function bedCornerPoints(" in qml
    assert "function bedHeightOffset(value)" in qml
    assert "nearLeft: root.positionU" in qml
    assert "nearRight: root.positionW" in qml
    assert "farMid: root.positionV" in qml
    assert "farLeft" in qml
    assert "farRight" in qml
    assert "drawBaselineBed(ctx, points)" in qml
    assert "drawCurrentBed(ctx, points)" in qml
    assert "drawBedPoint(ctx, points.nearLeft, \"U\", root.positionU)" in qml
    assert "drawBedPoint(ctx, points.nearRight, \"W\", root.positionW)" in qml
    assert "drawBedPoint(ctx, points.farMid, \"V\", root.positionV)" in qml
    assert '"Bed plane"' not in qml


def test_move_bed_tilt_preview_maps_negative_uvw_toward_screen_top() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "return Math.max(-18, Math.min(18, (value - average) * 2.4))" in qml
    assert "return Math.max(-18, Math.min(18, (value - average) * -2.4))" not in qml


def test_move_bed_tilt_step_grid_fits_portrait() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "id: bedTiltStepGrid" in qml
    assert "columns: root.metrics.portrait ? 4 : 6" in qml
    assert "Math.max(92, Math.round(root.metrics.fontSize * 5.6))" in qml
    assert "Layout.columnSpan: root.metrics.portrait ? 3 : 1" in qml


def test_responsive_layout_components_exist() -> None:
    qml_dir = Path("src/klippertouch/qml")
    expected = [
        qml_dir / "Metrics.qml",
        qml_dir / "components" / "BaseShell.qml",
        qml_dir / "components" / "TactileButton.qml",
        qml_dir / "components" / "IconTileButton.qml",
        qml_dir / "panels" / "MainMenuPanel.qml",
        qml_dir / "panels" / "MoreMenuPanel.qml",
        qml_dir / "components" / "MenuTile.qml",
        qml_dir / "components" / "TemperatureIcon.qml",
        qml_dir / "components" / "TemperatureDevicePager.qml",
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
        qml_dir / "panels" / "FanPanel.qml",
        qml_dir / "panels" / "MovePanel.qml",
        qml_dir / "panels" / "ExtrudePanel.qml",
    ]

    missing = [path for path in expected if not path.exists()]

    assert missing == []


def test_files_panel_is_only_read_only_file_management() -> None:
    qml = Path("src/klippertouch/qml/panels/FilesPanel.qml").read_text(encoding="utf-8")

    assert "property var fileModel" in qml
    assert 'objectName: "filesPanel"' in qml
    assert "property string loadError" in qml
    assert 'text: "G-Code files"' not in qml
    assert 'property string rootPath: "gcodes"' in qml
    assert '"label": "Name"' in qml
    assert '"label": "Date"' in qml
    assert '"label": "Size"' in qml
    assert "No G-Code files found" in qml
    assert "Loading files..." in qml
    assert "Unable to load files" in qml
    assert "root.loadError.length > 0" in qml
    assert "function currentPathLabel" in qml
    assert "root.currentPathLabel()" in qml
    assert "function emptyTitle" in qml
    assert "function goBack()" in qml
    assert "function requestFileAction(action)" in qml
    assert "function clearFileAction()" in qml
    assert "signal refreshRequested()" in qml
    assert "root.refreshRequested()" in qml
    assert 'text: "Retry"' in qml
    assert "enabled: !root.loading" in qml
    assert "function handleFileDeleted(path)" in qml
    assert "function handleFilePrintStarted(path)" in qml
    assert "property bool detailPage" in qml
    assert "property string pendingFileAction" in qml
    assert "property string controlStatus" in qml
    assert "property string controlError" in qml
    assert "function controlFeedbackText()" in qml
    assert "signal fileActionRequested(string action, string path)" in qml
    assert "Current folder is empty" in qml
    assert 'fileList.count + " items"' in qml
    assert "Search files" in qml
    assert "activeFileModel.setFilterText(text)" in qml
    assert "property real savedContentY" in qml
    assert "function restoreScrollPosition()" in qml
    assert "function restoreFileListScroll()" in qml
    assert "fileList.restoreScrollPosition()" in qml
    assert "onModelChanged: restoreScrollPosition()" in qml
    assert "onCountChanged: restoreScrollPosition()" in qml
    assert "footer: Item" in qml
    assert "id: compactControlRow" in qml
    assert "id: pathLabel" in qml
    assert "sortDescending" in qml
    assert "Layout.fillWidth: true" in qml
    assert "activeFileModel.breadcrumbs" not in qml
    assert "breadcrumbText" not in qml
    assert "property bool compactFileRows" in qml
    assert "root.compactFileRows ? 2 : 5" in qml
    assert "root.activeFileModel.selectPath(path, isDirectory)" in qml
    assert "root.detailPage = true" in qml
    assert "root.pendingFileAction = action" in qml
    assert "selectedPath" in qml
    assert "selectedDisplayName" in qml
    assert "selectedSizeLabel" in qml
    assert "selectedModifiedLabel" in qml
    assert "selectedPermissions" in qml
    assert "selectedPreviewThumbnailUrl" in qml
    assert "function selectedMetadataModel()" in qml
    assert "function selectedMetadataSections()" in qml
    assert "activeFileModel.metadataRevision" in qml
    assert (
        "root.activeFileModel.fileEstimatedTimeLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert "root.activeFileModel.fileLayerHeightLabelFor(root.activeFileModel.selectedPath)" in qml
    assert "root.activeFileModel.fileObjectHeightLabelFor(root.activeFileModel.selectedPath)" in qml
    assert (
        "root.activeFileModel.fileFilamentTotalLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert (
        "root.activeFileModel.fileSlicerLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert (
        "root.activeFileModel.fileNozzleDiameterLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert (
        "root.activeFileModel.fileFilamentTypeLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert (
        "root.activeFileModel.fileFilamentNameLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert (
        "root.activeFileModel.fileFilamentWeightTotalLabelFor(root.activeFileModel.selectedPath)"
        in qml
    )
    assert '"label": "Estimated time"' in qml
    assert '"label": "Layer height"' in qml
    assert '"label": "Object height"' in qml
    assert '"label": "Filament total"' in qml
    assert '"label": "Slicer"' in qml
    assert '"label": "Nozzle"' in qml
    assert '"label": "Filament type"' in qml
    assert '"label": "Filament name"' in qml
    assert '"label": "Filament weight"' in qml
    assert "required property string thumbnailUrl" in qml
    assert "source: thumbnailUrl" in qml
    assert "activeFileModel.requestMetadata(path)" in qml
    assert "function ensureThumbnailMetadata()" in qml
    assert "Component.onCompleted: ensureThumbnailMetadata()" in qml
    assert "onPathChanged: ensureThumbnailMetadata()" in qml
    assert "cacheBuffer: Math.max" in qml
    assert 'asynchronous: thumbnailUrl.indexOf("file:") !== 0' in qml
    assert "cache: true" in qml
    assert "sourceSize.width" in qml
    assert "thumbnailImage.status === Image.Ready" in qml
    assert "thumbnailImage.status === Image.Error" in qml
    assert "root.activeFileModel.selectedPreviewThumbnailUrl" in qml
    assert "id: detailPageView" in qml
    assert "id: selectedPreviewAndMetadataLayout" in qml
    assert "id: selectedPreviewFrame" in qml
    assert "function selectedPreviewSize()" in qml
    assert "Math.min(300" in qml
    assert "var reservedActionHeight = root.pendingFileAction.length > 0" in qml
    assert "var reservedMetadataHeight = Math.max" in qml
    assert "root.metrics.portrait ? 220 : 96" in qml
    assert "root.selectedActionPreviewHeight()" in qml
    assert "Layout.preferredWidth: root.selectedPreviewSize()" in qml
    assert "Layout.preferredHeight: root.selectedPreviewSize()" in qml
    assert "visible: !root.detailPage" in qml
    assert "visible: root.detailPage" in qml
    assert "Read-only file actions" not in qml
    assert "File actions" in qml
    assert 'text: "Print"' in qml
    assert 'text: "Delete"' in qml
    assert 'actionRole: "print"' in qml
    assert 'actionRole: "delete"' in qml
    assert "root.requestFileAction(actionRole)" in qml
    assert 'import "../components"' in qml
    assert "fontSize: root.metrics.fontSize" in qml
    assert 'iconName: "printer"' in qml
    assert 'iconName: "cancel"' in qml
    assert 'iconName: "confirm"' in qml
    assert 'iconName: "update"' in qml
    assert "id: selectedMetadataFlickable" in qml
    assert "id: selectedMetadataGrid" in qml
    assert "component MetadataGroupCard: Rectangle" in qml
    assert '"section": "File"' in qml
    assert '"section": "Print"' in qml
    assert '"section": "Filament"' in qml
    assert '"section": "Access"' in qml
    assert "contentHeight: selectedMetadataGrid.implicitHeight" in qml
    assert "ScrollBar.vertical: ScrollBar" in qml
    assert "policy: ScrollBar.AsNeeded" in qml
    assert "id: selectedActionBar" in qml
    assert "visible: root.pendingFileAction.length === 0" in qml
    assert 'text: "Actions"' in qml
    assert "component FileActionButton: TactileButton" in qml
    assert "component RetryButton: TactileButton" in qml
    assert "if (actionRole.length > 0)" in qml
    assert "id: selectedActionPreview" in qml
    assert "visible: root.pendingFileAction.length > 0" in qml
    assert "Layout.preferredHeight: visible ? root.selectedActionPreviewHeight() : 0" in qml
    assert "function selectedActionPreviewHeight()" in qml
    assert "id: selectedActionPreviewLayout" in qml
    assert "columns: root.metrics.portrait ? 1 : 2" in qml
    assert "id: selectedActionPreviewButtonRow" in qml
    assert "Layout.fillWidth: root.metrics.portrait" in qml
    assert "Layout.alignment: root.metrics.portrait ? Qt.AlignRight : Qt.AlignVCenter" in qml
    assert "id: selectedActionFeedback" in qml
    assert "visible: root.controlFeedbackText().length > 0" in qml
    assert 'root.pendingFileAction === "delete"' in qml
    assert 'text: "Confirm file action"' in qml
    assert 'text: "Confirmation preview only"' not in qml
    assert 'text: "Confirm"' in qml
    assert 'text: "Confirm disabled"' not in qml
    assert "root.fileActionRequested(" in qml
    assert "root.clearFileAction()" in qml
    assert 'text: "Dismiss"' in qml
    assert "onClicked: root.clearFileAction()" in qml
    assert "readonly property bool pressedFeedback" in qml
    assert "fileRowMouse.pressed" in qml
    assert "chipMouse.pressed" in qml
    assert "scale: chipMouse.pressed ? 0.96 : 1.0" in qml
    assert "scale: fileRowMouse.pressed ? 0.985 : 1.0" in qml
    assert "id: sortChipDepth" in qml
    assert "id: fileRowDepth" in qml
    assert "visible: !chipMouse.pressed && root.isChipEnabled(modelData.sortKey)" in qml
    assert "visible: !fileRowMouse.pressed" in qml
    assert "Behavior on scale" in qml
    assert "File browser; select a file to inspect or manage it." in qml
    assert "Read-only file browser; print actions stay out of this page." not in qml
    assert "NumberAnimation { duration: 70" in qml
    assert 'baseColor: "#121b1d"' in qml
    assert 'baseColor: "#101617"' in qml
    assert "printer.print.start" not in qml
    assert "server.files.delete" not in qml
    assert "server/files/delete" not in qml
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
    assert "id: detailsPanel" not in qml


def test_job_status_panel_is_separate_from_files_panel_and_read_only() -> None:
    qml = Path("src/klippertouch/qml/panels/JobStatusPanel.qml").read_text(encoding="utf-8")

    assert "property string printState" in qml
    assert 'objectName: "jobStatusPanel"' in qml
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
    assert "property real bedMaxX" in qml
    assert "property real bedMaxY" in qml
    assert "property real positionX" in qml
    assert "property real positionY" in qml
    assert "property real positionZ" in qml
    assert "property real positionE" in qml
    assert "property string homedAxes" in qml
    assert "property string controlStatus" in qml
    assert "property string controlError" in qml
    assert "function controlFeedbackText()" in qml
    assert "property var temperatureModel: null" in qml
    assert "property var fileModel: null" in qml
    assert "property var excludeObjectNames: []" in qml
    assert "property var excludeObjects: []" in qml
    assert "property var excludedObjectNames: []" in qml
    assert "property string currentObject" in qml
    assert "signal objectExcludeRequested(string objectName)" in qml
    assert "signal jobActionRequested(string action, string objectName)" in qml
    assert "root.fileModel.fileSizeLabelFor(root.printFilename)" in qml
    assert "root.fileModel.fileModifiedLabelFor(root.printFilename)" in qml
    assert "root.fileModel.filePathFor(root.printFilename)" in qml
    assert "root.fileModel.filePreviewThumbnailUrlFor(root.printFilename)" in qml
    assert "root.fileModel.thumbnailRevision" in qml
    assert "root.fileModel.metadataRevision" in qml
    assert "root.fileModel.fileEstimatedTimeLabelFor(root.printFilename)" in qml
    assert "root.fileModel.fileFilamentTotalLabelFor(root.printFilename)" in qml
    assert "root.fileModel.fileObjectHeightLabelFor(root.printFilename)" in qml
    assert "root.fileModel.fileLayerHeightLabelFor(root.printFilename)" in qml
    assert "id: jobThumbnail" in qml
    assert "source: root.fileModel && root.fileModel.thumbnailRevision >= 0" in qml
    assert "jobThumbnail.status === Image.Ready" in qml
    assert "id: thumbnailFrame" in qml
    assert "id: thumbnailPlaceholder" in qml
    assert "visible: !jobThumbnail.visible" in qml
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
    assert "function timePrimaryLabel()" in qml
    assert "function timePrimaryValue()" in qml
    assert "function stateHeadline" in qml
    assert "function stateMessage" in qml
    assert "function stateAccentColor" in qml
    assert "function isTerminalState(state)" in qml
    assert "function isTransitionalState(state)" in qml
    assert "function stateFamily(state)" in qml
    assert "Read-only job status" not in qml
    assert "Read-only summary remains visible" not in qml
    assert "Print status remains visible" in qml
    assert 'if (state === "starting")' in qml
    assert 'if (state === "pausing")' in qml
    assert 'if (state === "paused")' in qml
    assert 'if (state === "resuming")' in qml
    assert 'if (state === "cancelling")' in qml
    assert 'if (state === "clearing")' in qml
    assert 'if (state === "complete")' in qml
    assert 'if (state === "cancelled")' in qml
    assert 'if (state === "error")' in qml
    assert "Starting" in qml
    assert "Pausing" in qml
    assert "Paused" in qml
    assert "Resuming" in qml
    assert "Cancelling" in qml
    assert "Clearing" in qml
    assert "Cancelled" in qml
    assert "Completed" in qml
    assert "Printer error" in qml
    assert "Remaining" in qml
    assert 'return root.terminalJobState() ? "Elapsed" : "Remaining"' in qml
    assert "return root.terminalJobState()" in qml
    assert "id: jobActionGrid" in qml
    assert "component StatusCard: Rectangle" in qml
    assert "component MetricPill: Rectangle" in qml
    assert 'import "../components"' in qml
    assert "component JobButton: TactileButton" in qml
    assert "property int jobButtonHeight" in qml
    assert "property int jobButtonWidth" in qml
    assert 'readonly property color neutralAccent: "#8b9496"' in qml
    assert 'readonly property color mutedDangerAccent: "#9a8582"' in qml
    assert "property string buttonRole" in qml
    assert "property string iconName: \"\"" not in qml
    assert 'iconName: root.effectivePrintState() === "paused" ? "resume" : "pause"' in qml
    assert (
        'source: controlRoot.iconName.length > 0 ? Theme.iconSource(controlRoot.iconName) : ""'
        not in qml
    )
    assert "function jobActionGridHeight()" in qml
    assert "function jobActionGridWidth()" in qml
    assert "function jobActionButtonWidth()" in qml
    assert "function clearActionButtonWidth()" in qml
    assert "gradient: Gradient" in qml
    assert "id: statusPill" in qml
    assert "id: jobHeroLayout" in qml
    assert "function compactHeroLayout()" in qml
    assert "columns: root.compactHeroLayout() ? 2 : 1" in qml
    assert "id: compactProgressBox" in qml
    assert "id: portraitMetricStrip" in qml
    assert "visible: root.metrics.portrait" in qml
    assert "function jobHeroHeight()" in qml
    assert "function temperatureStripHeight()" in qml
    assert "function summaryTemperatureStripVisible()" in qml
    assert "function ultraWideThumbnailSize()" in qml
    assert "function ultraWideActionButtonHeight()" in qml
    assert "function groupedSummaryModel()" in qml
    assert "function summaryZoneRows(zone)" in qml
    assert "function detailTitle()" in qml
    assert "function detailInfoModel(page)" in qml
    assert "function positionLabel()" in qml
    assert "Layout.preferredHeight: root.jobHeroHeight()" in qml
    assert "Layout.preferredHeight: root.temperatureStripHeight()" in qml
    assert "id: summaryZoneGrid" in qml
    assert "id: timeSummaryZone" in qml
    assert "id: motionSummaryZone" in qml
    assert "id: materialSummaryZone" in qml
    assert "root.groupedSummaryModel()" in qml
    assert 'root.detailPage = "time"' in qml
    assert 'root.detailPage = "motion"' in qml
    assert 'root.detailPage = "extrusion"' in qml
    assert "return Math.max(146" in qml
    assert "|| !root.temperatureModel" in qml
    assert "|| root.temperatureModel.rowCount() <= 0" in qml
    assert "id: summaryTemperatureStrip" in qml
    assert "visible: root.summaryTemperatureStripVisible()" in qml
    assert "root.pendingJobAction.length > 0" in qml
    assert "root.metrics.ultraWide" in qml
    assert "return !root.metrics.portrait" in qml
    assert "Layout.maximumWidth: Math.max(160" in qml
    assert "id: progressRail" in qml
    assert "id: progressFill" in qml
    assert 'iconName: root.effectivePrintState() === "paused" ? "resume" : "pause"' in qml
    assert 'iconName: "cancel"' in qml
    assert 'iconName: "clear"' in qml
    assert 'iconName: "object"' in qml
    assert 'iconName: "advanced"' in qml
    assert 'iconName: "confirm"' in qml
    assert 'buttonRole: "danger"' in qml
    assert 'baseColor: "#263033"' in qml
    assert 'pressedColor: "#172528"' in qml
    assert "accentColor: controlRoot.roleAccent" in qml
    assert "implicitHeight: root.jobButtonHeight" in qml
    assert "Layout.preferredHeight: root.jobActionGridHeight()" in qml
    assert "Layout.preferredWidth: root.jobActionGridWidth()" in qml
    assert "Layout.alignment: root.terminalJobState() ? Qt.AlignRight : Qt.AlignHCenter" in qml
    assert "Layout.preferredWidth: root.jobActionButtonWidth()" in qml
    assert "columns: root.metrics.portrait ? 2 : 4" in qml
    assert "Layout.preferredHeight: root.jobButtonHeight" in qml
    assert "Layout.preferredWidth: root.jobButtonWidth" in qml
    assert "Layout.alignment: Qt.AlignVCenter" in qml
    assert "root.primaryActionLabel()" in qml
    assert 'return state === "paused" || state === "resuming" ? "Resume" : "Pause"' in qml
    assert 'text: "Cancel"' in qml
    assert 'text: "Clear Status"' in qml
    assert "Layout.preferredWidth: root.clearActionButtonWidth()" in qml
    assert "function terminalJobState()" in qml
    assert "visible: root.terminalJobState()" in qml
    assert "enabled: !root.isTransitionalState(root.effectivePrintState())" in qml
    assert 'root.stageImmediateJobAction("clear")' in qml
    assert 'text: "Skip Object"' in qml
    assert 'root.detailPage = "exclude"' in qml
    assert 'text: "Advanced"' in qml
    assert "readonlyActionHint" in qml
    assert "property string detailPage" in qml
    assert "property string pendingJobAction" in qml
    assert "property string pendingJobObject" in qml
    assert "property string controlStatus" in qml
    assert "property string controlError" in qml
    assert "property string requestedPrintState" in qml
    assert "function effectivePrintState()" in qml
    assert 'root.requestedPrintState === "printing" && root.printState === "standby"' in qml
    assert 'root.requestedPrintState === "printing" && root.printState === "paused"' in qml
    assert 'root.requestedPrintState === "paused" && root.printState === "printing"' in qml
    assert 'root.requestedPrintState === "cancelled"' in qml
    assert 'root.requestedPrintState === "standby" && root.isTerminalState(root.printState)' in qml
    assert "function controlFeedbackText()" in qml
    assert "id: jobControlFeedback" in qml
    assert "visible: root.controlFeedbackText().length > 0" in qml
    assert "root.controlError.length > 0 ? root.controlError : root.controlStatus" in qml
    assert 'root.detailPage = "advanced"' in qml
    assert 'root.detailPage = "summary"' in qml
    assert "function requestJobAction(action, objectName)" in qml
    assert "function stageImmediateJobAction(action)" in qml
    assert "function clearJobAction()" in qml
    assert "root.pendingJobAction = action" in qml
    assert "root.pendingJobObject = objectName || \"\"" in qml
    assert 'root.pendingJobAction = "staged_" + action' not in qml
    assert "root.jobActionRequested(action, \"\")" in qml
    assert "id: jobActionPreview" in qml
    assert "visible: root.pendingJobAction.length > 0" in qml
    assert "function confirmationRequired()" in qml
    assert "root.pendingJobAction === \"cancel\"" in qml
    assert 'root.pendingJobAction === "skip"' in qml
    assert 'root.pendingJobAction === "staged_pause"' not in qml
    assert 'root.confirmationRequired() ? "Confirm action" : "Action sent"' in qml
    assert "Confirmation preview only" not in qml
    assert "readonly property bool confirmButtonVisible: root.confirmationRequired()" in qml
    assert "visible: previewRoot.confirmButtonVisible" in qml
    assert 'text: "Confirm"' in qml
    assert 'text: "Confirm disabled"' not in qml
    assert 'text: "Dismiss"' in qml
    assert "onClicked: root.clearJobAction()" in qml
    assert "id: advancedPage" in qml
    assert "id: advancedControlGrid" in qml
    assert "function advancedCardHeight()" in qml
    assert "Layout.preferredHeight: root.advancedCardHeight()" in qml
    assert "id: excludePage" in qml
    assert "id: excludePageLayout" in qml
    assert "columns: root.metrics.ultraWide ? 2 : 1" in qml
    assert "rows: root.metrics.ultraWide ? 1 : 2" in qml
    assert "id: excludeControlPanel" in qml
    assert "Layout.preferredWidth: root.metrics.ultraWide" in qml
    assert "columns: root.metrics.ultraWide ? 1 : 2" in qml
    assert "root.currentObject" in qml
    assert "property string selectedExcludeObject" in qml
    assert "function selectedExcludeObjectName()" in qml
    assert "function selectExcludeObject(objectName)" in qml
    assert "function activeExcludeObjectName()" in qml
    assert "function objectMapFillColor(excluded, current, selected)" in qml
    assert "function objectMapStrokeColor(current, selected)" in qml
    assert "function drawCurrentObjectMarker(ctx, objectInfo, bounds)" in qml
    assert 'return selected ? "#e0e6e8" : current ? "#f0b24b"' in qml
    assert 'ctx.strokeStyle = "#f0b24b"' in qml
    assert "id: objectMapCanvas" in qml
    assert "root.excludeObjects.length" in qml
    assert "function objectMapBounds()" in qml
    assert "root.bedMaxX > root.bedMinX" in qml
    assert "root.bedMaxY > root.bedMinY" in qml
    assert "function objectMapMinObjectPixels(width, height)" in qml
    assert "function objectMapDisplayPolygon(objectInfo, bounds, width, height)" in qml
    assert "Math.max(originalWidth, minSize)" in qml
    assert "Math.min(usableRight, Math.max(usableLeft, scaledX))" in qml
    assert "function objectAtPoint(screenX, screenY)" in qml
    assert "function drawExcludeObjectMap(ctx)" in qml
    assert "id: selectedObjectSkipButton" in qml
    assert "id: currentObjectSkipButton" in qml
    assert "root.requestJobAction(\"skip\", root.activeExcludeObjectName())" in qml
    assert "root.requestJobAction(\"skip_current\", \"\")" in qml
    assert "root.selectExcludeObject(objectName)" in qml
    assert 'root.requestJobAction("skip", objectName)' not in qml
    assert "ListView {" not in qml.split("id: excludePage", 1)[1]
    assert "model: root.excludeObjectNames" not in qml
    assert 'root.requestJobAction("skip", modelData)' not in qml
    assert "qmllint disable missing-property" in qml
    assert "function goBack()" in qml
    assert 'if (root.pendingJobAction.length > 0)' in qml
    assert 'if (root.detailPage !== "summary")' in qml
    assert "return true" in qml
    assert "return false" in qml
    assert "Popup {" not in qml
    assert 'text: "Back"' not in qml
    assert 'root.requestJobAction(root.printState === "paused" ? "resume" : "pause", "")' not in qml
    assert (
        'root.stageImmediateJobAction('
        'root.effectivePrintState() === "paused" ? "resume" : "pause")'
        in qml
    )
    assert "root.clearJobAction()" in qml
    assert "root.jobActionRequested(root.pendingJobAction, root.pendingJobObject)" in qml
    assert "root.zOffsetLabel()" in qml
    assert "function zOffsetCompactLabel()" in qml
    assert "root.zOffsetCompactLabel()" in qml
    assert "root.percentLabel(root.speedFactor)" in qml
    assert "root.percentLabel(root.extrudeFactor)" in qml
    assert "signal zOffsetAdjustRequested(real delta)" in qml
    assert "signal speedFactorAdjustRequested(real delta)" in qml
    assert "signal extrudeFactorAdjustRequested(real delta)" in qml
    assert "id: advancedControlRepeater" in qml
    assert "Layout.maximumHeight: 0" not in qml
    assert "id: advancedPageSpacer" in qml
    assert "root.zOffsetAdjustRequested(modelData.delta)" in qml
    assert "root.speedFactorAdjustRequested(modelData.delta)" in qml
    assert "root.extrudeFactorAdjustRequested(modelData.delta)" in qml
    assert '"minus": "-0.05"' in qml
    assert '"plus": "+0.05"' in qml
    assert '"minus": "-5%"' in qml
    assert '"plus": "+5%"' in qml
    assert "Buttons emit adjustment requests only" not in qml
    assert "Skip buttons emit objectExcludeRequested only" not in qml
    assert "printer.print.pause" not in qml
    assert "printer.print.cancel" not in qml
    assert "exclude_object" not in qml
    assert "root.percentLabel(root.speedFactor)" in qml
    assert "root.zOffsetLabel()" in qml
    assert "id: detailInfoPage" in qml
    assert "id: detailInfoGrid" in qml
    assert 'root.detailPage === "time"' in qml
    assert 'root.detailPage === "motion"' in qml
    assert 'root.detailPage === "extrusion"' in qml
    assert '"label": "Requested speed"' in qml
    assert '"label": "Max acceleration"' in qml
    assert '"label": "X position"' in qml
    assert '"label": "Y position"' in qml
    assert '"label": "Z position"' in qml
    assert '"label": "Homed axes"' in qml
    assert '"label": "Filament used"' in qml
    assert '"label": "Flow factor"' in qml
    assert '"label": "File estimate"' not in qml
    assert '"label": "Filament estimate"' not in qml
    assert "id: quickInfoGrid" not in qml
    assert "function quickInfoLimit()" not in qml
    assert "function summaryInfoModel()" not in qml
    assert "root.summaryInfoModel()" not in qml
    assert 'onClicked: root.detailPage = modelData.target' not in qml
    assert "id: cardGrid" not in qml
    assert "#ed3c63" not in qml
    assert "#28a7df" not in qml
    assert "#007db4" not in qml
    assert "#d46900" not in qml
    assert "#4caf50" not in qml
    assert "#d8615b" not in qml
    assert "Theme.color1" not in qml
    assert "Theme.color2" not in qml
    assert "Theme.color4" not in qml
    assert 'text: "Start"' not in qml
    assert "printer.print." not in qml
    assert "printer.gcode.script" not in qml

    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "function clampControlPercent(value)" in main_qml
    assert 'window.showPanel("job_status")' in main_qml
    assert (
        'requestedPrintState: window.jobControlBridgeModel ? '
        'window.jobControlBridgeModel.requestedPrintState : ""'
        in main_qml
    )
    assert "jobControlBridgeModel.requestZOffsetAdjust(delta)" in main_qml
    assert (
        "jobControlBridgeModel.requestSpeedFactor("
        "window.clampControlPercent(window.speedFactor + delta))"
        in main_qml
    )
    assert (
        "jobControlBridgeModel.requestExtrudeFactor("
        "window.clampControlPercent(window.extrudeFactor + delta))"
        in main_qml
    )


def test_job_status_summary_scrolls_on_small_portrait_screens() -> None:
    qml = Path("src/klippertouch/qml/panels/JobStatusPanel.qml").read_text(encoding="utf-8")

    assert "id: summaryFlickable" in qml
    assert "visible: root.detailPage === \"summary\"" in qml
    assert 'visible: root.detailPage === "summary" && root.metrics.ultraWide' in qml
    assert 'visible: root.detailPage === "summary" && !root.metrics.ultraWide' in qml
    assert "id: ultraWideSummaryGrid" in qml
    assert 'visible: !(root.detailPage === "summary" && root.metrics.ultraWide)' in qml
    assert "id: ultraWideThumbnailFrame" in qml
    assert "id: ultraWideProgressDialCard" in qml
    assert "id: ultraWideProgressCanvas" in qml
    assert "function drawUltraWideProgressDial(ctx)" in qml
    assert "ctx.arc(center, center, radius" in qml
    assert "id: ultraWideFileHeader" in qml
    assert "id: ultraWideStatusPill" in qml
    assert "id: ultraWideInfoCard" in qml
    assert "Layout.preferredWidth: Math.max(560, Math.round(root.width * 0.34))" in qml
    assert "id: ultraWideKeyInfoGrid" in qml
    assert "id: ultraWideActionGrid" in qml
    assert "Layout.preferredHeight: root.ultraWideActionButtonHeight()" in qml
    assert "contentHeight: summaryContent.implicitHeight + root.summaryBottomSafeArea()" in qml
    assert "id: summaryContent" in qml
    assert "id: summaryBottomSafeAreaItem" in qml
    assert "Layout.preferredHeight: root.summaryBottomSafeArea()" in qml
    assert "function summaryBottomSafeArea()" in qml
    assert "function summaryZoneGridHeight()" in qml
    assert "Layout.preferredHeight: root.summaryZoneGridHeight()" in qml
    assert "function compactHeroLayout()" in qml
    assert "Math.max(132, Math.round(root.metrics.fontSize * 8.1))" in qml
    assert "Math.max(168, Math.round(root.metrics.fontSize * 10.2))" in qml
    assert "Math.max(72, Math.round(root.metrics.fontSize * 4.2))" in qml
    assert "ScrollBar.vertical: ScrollBar" in qml


def test_move_panel_exposes_read_only_position_without_controls() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert 'objectName: "movePanel"' in qml
    assert "property real positionX" in qml
    assert "property real positionY" in qml
    assert "property real positionZ" in qml
    assert "property real positionE" in qml
    assert "property string homedAxes" in qml
    assert 'property var distances: [".1", ".5", "1", "5", "10", "25", "50"]' in qml
    assert 'property var xyButtons' in qml
    assert 'property var zButtons' in qml
    assert 'property var actionButtons' in qml
    assert 'property var moreActions' in qml
    action_buttons = qml.split("property var actionButtons: [", 1)[1].split(
        "property var moreActions: [", 1
    )[0]
    assert '"action": "bed_tilt"' in action_buttons
    assert '"action": "disable_motors"' in action_buttons
    assert '"action": "home_all"' in action_buttons
    assert '"action": "more"' in action_buttons
    assert action_buttons.index('"action": "home_all"') < action_buttons.index(
        '"action": "disable_motors"'
    )
    assert action_buttons.index('"action": "disable_motors"') < action_buttons.index(
        '"action": "bed_tilt"'
    )
    assert action_buttons.index('"action": "bed_tilt"') < action_buttons.index(
        '"action": "more"'
    )
    assert '"action": "home_uvw"' not in action_buttons
    assert '"action": "accelerator_level"' not in action_buttons
    assert '"label": "Home All"' in qml
    assert '"action": "home_all"' in qml
    assert '"hint": "XYZ"' in qml
    assert '"label": "XY Speed"' in qml
    assert '"action": "speed_xy"' in qml
    assert '"label": "UVW Home"' in qml
    assert '"action": "home_uvw"' in qml
    assert '"label": "Acc Level"' in qml
    assert '"action": "accelerator_level"' in qml
    assert '"label": "Z Tilt Adjust"' in qml
    assert '"action": "z_tilt_adjust"' in qml
    assert '"iconName": "tilt"' in qml
    assert "function visibleMoreActions()" in qml
    assert "function actionButtonColumns()" in qml
    assert "function actionButtonPanelWidth(parentWidth, zPadRight)" in qml
    assert "var desiredColumns = root.metrics.ultraWide ? 1 : 2" in qml
    assert "return root.metrics.ultraWide ? 1 : 2" in qml
    assert "Math.max(root.moveButtonSize * 3.05" in qml
    assert "parentWidth - zPadRight - root.motionSectionGap" in qml
    assert "var moreAction = null" in qml
    assert 'action.action === "more"' in qml
    assert "actions.length % columns === 0" in qml
    assert '{"placeholder": true}' in qml
    assert "function positionItems()" in qml
    assert "property bool confirmVisible" in qml
    assert "property string pendingConfirmAction" in qml
    assert "function actionNeedsConfirmation(action)" in qml
    assert "function requestConfirmedAction(action)" in qml
    assert "function confirmPendingAction()" in qml
    assert "id: moveConfirmOverlay" in qml
    assert 'action === "accelerator_level"' in qml
    assert 'action === "z_tilt_adjust"' in qml
    assert "root.fiveAxisAvailable" in qml
    assert "root.acceleratorLevelAvailable" in qml
    assert "root.zTiltAvailable" in qml
    assert 'property bool moreVisible' in qml
    assert 'property string detailPage: "main"' in qml
    assert 'signal moveActionRequested(string action, real distance, real speed)' in qml
    assert 'property var bedTiltButtons' in qml
    assert 'property var tiltDistances: [".01", ".05", ".1", ".5", "1"]' in qml
    assert 'property string selectedTiltDistance: ".1"' in qml
    assert 'property string selectedTiltSpeed: "2"' in qml
    assert 'function selectTiltDistance(distance)' in qml
    assert 'function showBedTilt()' in qml
    assert 'function bedHeightOffset(value)' in qml
    assert 'function bedCornerPoints(' in qml
    assert 'root.detailPage = "bed_tilt"' in qml
    assert '"label": "Bed Tilt"' in qml
    assert '"action": "bed_tilt"' in qml
    assert '"requires": "five_axis"' in qml
    assert 'id: bedTiltPage' in qml
    assert 'id: bedTiltPreviewPanel' in qml
    assert 'id: bedRectCanvas' in qml
    assert 'id: bedPositionStrip' in qml
    assert qml.index('id: bedTiltPreviewPanel') < qml.index('id: bedPositionStrip')
    position_strip_block = qml.split('id: bedPositionStrip', 1)[1].split('id: uvwTiltPad', 1)[0]
    assert 'id: bedTiltPreview' not in position_strip_block
    assert 'text: "Z " + root.positionZ.toFixed(3)' in qml
    assert 'text: "U " + root.positionU.toFixed(3)' in qml
    assert 'text: "V " + root.positionV.toFixed(3)' in qml
    assert 'text: "W " + root.positionW.toFixed(3)' in qml
    assert 'id: uvwTiltPad' in qml
    assert 'id: bedRectCanvas' in qml
    assert 'drawBaselineBed(ctx, points)' in qml
    assert 'drawCurrentBed(ctx, points)' in qml
    assert 'drawBedPoint(ctx, points.nearLeft, "U", root.positionU)' in qml
    assert 'drawBedPoint(ctx, points.nearRight, "W", root.positionW)' in qml
    assert 'drawBedPoint(ctx, points.farMid, "V", root.positionV)' in qml
    assert 'title: "V"' in qml
    assert 'title: "U"' in qml
    assert 'title: "W"' in qml
    assert '"actionPlus": "v_plus"' in qml
    assert '"actionMinus": "v_minus"' in qml
    assert '"actionPlus": "u_plus"' in qml
    assert '"actionMinus": "u_minus"' in qml
    assert '"actionPlus": "w_plus"' in qml
    assert '"actionMinus": "w_minus"' in qml
    assert 'property var xySpeeds: ["25", "50", "100", "150"]' in qml
    assert 'property var zSpeeds: ["2", "5", "10", "15"]' in qml
    assert 'property string selectedXYSpeed: "100"' in qml
    assert 'property string selectedZSpeed: "10"' in qml
    assert "function speedForAction(action)" in qml
    assert "function cycleSpeed(kind)" in qml
    assert "function moreActionHint(action, fallback)" in qml
    assert '"action": "y_plus"' in qml
    assert '"action": "x_minus"' in qml
    assert '"action": "x_plus"' in qml
    assert '"action": "y_minus"' in qml
    assert '"action": "z_plus"' in qml
    assert '"action": "z_minus"' in qml
    assert '"label": "Y+"' in qml
    assert '"label": "X-"' in qml
    assert '"label": "X+"' in qml
    assert '"label": "Y-"' in qml
    assert '"label": "Z+"' in qml
    assert '"label": "Z-"' in qml
    assert "component LockedTile: IconTileButton" in qml
    assert "component DirectionButton: Rectangle" in qml
    assert "property bool pressed: false" in qml
    assert 'import "../components"' in qml
    assert "scale: tileRoot.pressed && tileRoot.enabled ? 0.97 : 1.0" not in qml
    assert "scale: directionRoot.pressed && directionRoot.enabled ? 0.96 : 1.0" in qml
    assert "component ActionIconButton: IconTileButton" in qml
    assert "pressedFeedback: pressed" in qml
    assert "textMaximumLineCount: 2" in qml
    assert "textFontScale: 0.68" in qml
    assert "scale: tiltRoot.pressed && tiltRoot.enabled ? 0.97 : 1.0" in qml
    assert "onPressedChanged: parent.pressed = pressed" in qml
    assert "onPressedChanged: tiltRoot.pressed = pressed" in qml
    assert "id: tileDepth" not in qml
    assert "id: directionDepth" in qml
    assert "id: actionDepth" not in qml
    assert "id: tiltDepth" in qml
    assert "TactileButton {" in qml
    assert "id: cancelConfirmButton" in qml
    assert "id: confirmActionButton" in qml
    assert 'iconName: "cancel"' in qml
    assert 'iconName: "confirm"' in qml
    assert 'baseColor: "#0b1112"' in qml
    assert 'baseColor: "#1b2b2e"' in qml
    assert "Behavior on scale" in qml
    assert "NumberAnimation { duration: 80" in qml
    assert "ColorAnimation { duration: 80" in qml
    assert "function arrowGlyph(direction)" in qml
    assert "id: bedRectCanvas" in qml
    assert '"#eef3fb"' not in qml
    assert "root.positionX.toFixed(2)" in qml
    assert "root.positionU.toFixed(2)" in qml
    assert "root.homedAxes.length > 0" in qml
    assert "property string selectedDistance" in qml
    assert "function selectDistance(distance)" in qml
    assert "root.selectedDistance === modelData" in qml
    assert 'readonly property color selectedAccent: "#7f9298"' in qml
    assert "Theme.color3" not in qml
    assert "id: xyMovePad" in qml
    assert "id: zMovePad" in qml
    assert "id: motionPad" in qml
    assert "id: motionActions" in qml
    assert "id: positionPanel" in qml
    assert "id: moveControlFeedbackLabel" in qml
    assert "Layout.maximumWidth: Math.max(120, Math.round(positionPanel.width * 0.52))" in qml
    assert "maximumLineCount: 1" in qml
    assert "wrapMode: Text.NoWrap" in qml
    assert "id: distancePanel" in qml
    assert "root.metrics.ultraWide ? 3 : 1" in qml
    assert "root.metrics.ultraWide ? 1 : 3" in qml
    assert "placeholder" in qml
    assert 'iconName: "home"' in qml
    assert 'title: "XY"' in qml
    assert 'title: "Z"' in qml
    assert 'root.moveActionRequested("home_xy", 0, 0)' in qml
    assert 'root.moveActionRequested("home_z", 0, 0)' in qml
    assert "root.moveActionRequested(action, 0, 0)" in qml
    assert "root.handleMoreAction(modelData.action)" in qml
    assert "function handleMoreAction(action)" in qml
    assert '"label": "Disable Motors"' in qml
    assert '"action": "disable_motors"' in qml
    assert '"hint": "M84"' in qml
    assert '"iconName": "motor-off"' in qml
    assert '"label": "More"' in qml
    assert '"action": "more"' in qml
    assert '"iconName": "settings"' in qml
    assert "iconName: \"home\"" in qml
    assert "readonly property int moveButtonSize" in qml
    assert "readonly property int moveHomeSize" in qml
    assert "readonly property int moveActionIconSize" in qml
    assert "readonly property real motionSectionGap" in qml
    assert "function fittedMoveButtonSize(padWidth, padHeight)" in qml
    assert "Math.floor(padHeight / 3.08)" in qml
    assert (
        'source: tileRoot.iconName.length > 0 ? Theme.iconSource(tileRoot.iconName) : ""'
        not in qml
    )
    assert "source: Theme.iconSource(actionRoot.iconName)" not in qml
    assert "selectedColor: \"#1b2b2e\"" in qml
    assert "selectedAccentColor: root.selectedAccent" in qml
    assert "id: moveMorePanel" in qml
    assert "id: moveMorePage" in qml
    assert "source: Theme.iconSource(modelData.iconName)" not in qml
    assert "iconName: modelData.iconName" in qml
    assert "visible: root.hint.length > 0" in Path(
        "src/klippertouch/qml/components/IconTileButton.qml"
    ).read_text(encoding="utf-8")
    assert "function showMore()" in qml
    assert 'root.detailPage = "more"' in qml
    assert "function goBack()" in qml
    assert "visible: root.moreVisible && root.metrics.ultraWide" in qml
    assert (
        "root.moveActionRequested(modelData.action, parseFloat(root.selectedDistance), "
        "root.speedForAction(modelData.action))"
    ) in qml
    assert "id: distanceGrid" in qml
    assert "id: positionGrid" in qml
    assert "M18" not in qml
    assert "printer.gcode.script" not in qml


def test_extrude_panel_exposes_read_only_extruder_state_without_controls() -> None:
    qml = Path("src/klippertouch/qml/panels/ExtrudePanel.qml").read_text(encoding="utf-8")

    assert "property real extruderTemperature" in qml
    assert "property real extruderTarget" in qml
    assert "property bool extruderCanExtrude" in qml
    assert "property string klippyState" in qml
    assert "property string webhooksState" in qml
    assert "property real extruderPressureAdvance" in qml
    assert "property real extruderSmoothTime" in qml
    assert "property var filamentSensors" in qml
    assert "property bool materialSystemEnabled" in qml
    assert 'property string selectedMaterialSlot: "Slot 1"' in qml
    assert "property var materialActionButtons" in qml
    assert "property real actionEmphasis" in qml
    assert "property real positionE" in qml
    assert 'readonly property color selectedAccent: "#7f9298"' in qml
    assert "property string selectedDistance" in qml
    assert "property string selectedSpeed" in qml
    assert 'property string detailPage: "main"' in qml
    assert "property var actionButtons" in qml
    assert "property var settingsButtons" in qml
    assert "component NozzleStage: Rectangle" in qml
    assert "id: nozzleStage" in qml
    assert "id: retractButton" in qml
    assert "id: nozzleIcon" in qml
    assert 'source: Theme.iconSource("extruder")' in qml
    assert 'text: "⬟"' not in qml
    assert "id: extrudeButton" in qml
    assert (
        'root.extrudeActionRequested("retract", parseFloat(root.selectedDistance), '
        "parseFloat(root.selectedSpeed))"
        in qml
    )
    assert (
        'root.extrudeActionRequested("extrude", parseFloat(root.selectedDistance), '
        "parseFloat(root.selectedSpeed))"
        in qml
    )
    assert 'signal temperatureTargetRequested(string deviceName, real target)' in qml
    assert "signal pressureAdvanceRequested(real advance, real smoothTime)" in qml
    assert "function openTargetEditor()" in qml
    assert "function confirmTargetEditor()" in qml
    assert "property bool targetEditorReplaceOnNextInput: false" in qml
    assert "root.targetEditorReplaceOnNextInput = root.targetEditorValue.length > 0" in qml
    assert "if (root.targetEditorReplaceOnNextInput) {" in qml
    assert "root.targetEditorValue = digit" in qml
    assert "root.targetEditorReplaceOnNextInput = false" in qml
    assert "function openPressureAdvanceEditor()" in qml
    assert "function confirmPressureAdvanceEditor()" in qml
    assert "isNaN(advance) || isNaN(smoothTime)" in qml
    assert 'root.temperatureTargetRequested("extruder", value)' in qml
    assert "root.pressureAdvanceRequested(advance, smoothTime)" in qml
    assert "id: nozzleTemperatureArea" in qml
    assert "id: pressureAdvanceArea" in qml
    assert "id: targetEditorPopup" in qml
    assert "id: pressureAdvancePopup" in qml
    assert "id: targetKeypadGrid" in qml
    assert "id: landscapeTargetEditor" in qml
    assert "id: landscapeHeaderRow" in qml
    assert "id: landscapeInputRow" in qml
    assert "id: landscapeBottomRow" in qml
    assert "function positionTargetEditor()" in qml
    assert "targetEditorPopup.dialogX = Math.max(" in qml
    assert "targetEditorPopup.dialogY = Math.max(" in qml
    assert "id: landscapeBackspaceButton" in qml
    assert "id: landscapeCancelButton" in qml
    assert "id: landscapeSetButton" in qml
    assert 'model: ["1", "2", "3", "4", "5", "6", "7", "8", "9"]' in qml
    assert 'text: "."' in qml
    assert "Layout.minimumWidth: root.touchTargetSize" in qml
    assert "Layout.minimumHeight: root.touchTargetSize" in qml
    assert 'signal extrudeActionRequested(string action, real distance, real speed)' in qml
    assert '"action": "extrude"' in qml
    assert '"iconName": "extrude"' in qml
    assert '"action": "retract"' in qml
    assert '"iconName": "unload"' in qml
    assert '"label": "Load"' in qml
    assert '"iconName": "load"' in qml
    assert '"label": "Unload"' in qml
    assert '"iconName": "unload"' in qml
    assert '"label": "Temperature"' not in qml
    assert '"Set Temp"' not in qml
    assert '"action": "pressure_advance"' not in qml
    assert '"label": "Retraction"' not in qml
    assert '"action": "retraction"' not in qml
    assert '"label": "Materials"' in qml
    assert '"action": "materials"' in qml
    assert '"iconName": "material"' in qml
    assert 'iconName: "length"' in qml
    assert 'iconName: "speed"' in qml
    assert '"hint": "AFC / AMS"' in qml
    assert "component ActionTile: IconTileButton" in qml
    assert (
        'source: tileRoot.iconName.length > 0 ? Theme.iconSource(tileRoot.iconName) : ""'
        not in qml
    )
    assert "pressedFeedback: pressed" in qml
    assert "textMaximumLineCount: 2" in qml
    assert "component PlaceholderTile: Rectangle" in qml
    assert "function selectDistance(distance)" in qml
    assert "function selectSpeed(speed)" in qml
    assert "function feedSummaryText()" in qml
    assert "function closeFeedSetupAfterSelection()" in qml
    assert "function maxVisibleFilamentSensors()" in qml
    assert "function openSettingsAction(action)" in qml
    assert "function materialEntryVisible()" in qml
    assert "function selectMaterialSlot(slotLabel)" in qml
    assert "function goBack()" in qml
    assert 'if (root.detailPage !== "main")' in qml
    assert 'root.detailPage = "materials"' in qml
    assert 'if (!root.materialSystemEnabled)' in qml
    assert "visible: root.materialEntryVisible()" in qml
    assert 'visible: root.detailPage === "main"' in qml
    assert 'visible: root.detailPage === "materials"' in qml
    assert "AFC / AMS" in qml
    assert "Material slots" in qml
    assert (
        'text: root.metrics.portrait ? root.selectedMaterialSlot '
        ': "Selected: " + root.selectedMaterialSlot'
    ) in qml
    assert "Adapter pending" in qml
    assert "Load Selected" in qml
    assert "Unload Selected" in qml
    assert 'hint: "Not connected"' in qml
    assert "enabled: false" in qml
    assert "root.selectMaterialSlot(modelData.label)" in qml
    assert "id: filamentSensorTile" in qml
    assert "Layout.columnSpan: root.materialEntryVisible() ? 1 : 2" in qml
    assert "property bool pressed: false" in qml
    assert "scale: tileRoot.pressed && tileRoot.enabled ? 0.97 : 1.0" not in qml
    assert "id: actionTileDepth" not in qml
    assert "onPressedChanged: parent.pressed = pressed" in qml
    assert "component KeypadButton: TactileButton" in qml
    assert "implicitWidth: root.touchTargetSize" in qml
    assert "implicitHeight: root.touchTargetSize" in qml
    assert "padding: 0" in qml
    assert 'baseColor: keyRoot.primary && keyRoot.enabled ? "#1b2b2e" : "#101819"' in qml
    assert 'pressedColor: keyRoot.primary && keyRoot.enabled ? "#24383c" : "#182528"' in qml
    assert "id: nozzleTemperatureDepth" in qml
    assert "id: pressureAdvanceDepth" in qml
    assert "root.selectedDistance === modelData" in qml
    assert "root.selectedSpeed === modelData" in qml
    assert "root.closeFeedSetupAfterSelection()" in qml
    assert 'text: root.feedSummaryText()' in qml
    assert "id: filamentSensorList" in qml
    assert "clip: true" in qml
    assert "model: Math.min(root.filamentSensors.length, root.maxVisibleFilamentSensors())" in qml
    assert "var hidden = root.filamentSensors.length - root.maxVisibleFilamentSensors()" in qml
    assert "primary: true" in qml
    assert "property bool primary" in qml
    assert "root.extruderTemperature.toFixed(1)" in qml
    assert "root.extruderTarget.toFixed(1)" in qml
    assert "root.extruderPressureAdvance.toFixed(3)" in qml
    assert "root.extruderSmoothTime.toFixed(3)" in qml
    assert "id: pressureAdvanceValueRow" in qml
    assert "id: pressureAdvanceValueRowPortrait" in qml
    assert 'text: "ADV " + root.extruderPressureAdvance.toFixed(3)' in qml
    assert 'text: "SMT " + root.extruderSmoothTime.toFixed(3)' in qml
    assert '+ " / SMT " + root.extruderSmoothTime.toFixed(3)' not in qml
    assert "root.positionE.toFixed(2)" in qml
    assert "function nozzleHeating()" in qml
    assert "function nozzleStateText()" in qml
    assert "function nozzleDetailStateText()" in qml
    assert "function nozzleDetailText()" in qml
    assert "property string controlStatus" in qml
    assert "property string controlError" in qml
    assert "function controlFeedbackText()" in qml
    assert "function printerReady()" in qml
    assert "function extrusionAllowed()" in qml
    assert "function extrusionGuardText()" in qml
    assert 'return "Heating nozzle"' in qml
    assert 'return "Ready to extrude"' in qml
    assert (
        'return root.nozzleDetailStateText() + " · E " '
        '+ root.positionE.toFixed(2) + " mm"'
    ) in qml
    assert "enabled: root.extrusionAllowed()" in qml
    assert "hint: root.extrusionAllowed() ? \"pull back\" : root.extrusionGuardText()" in qml
    assert "hint: root.extrusionAllowed() ? \"push filament\" : root.extrusionGuardText()" in qml
    assert "function filamentSensorSummary()" in qml
    assert "root.filamentSensors.length" in qml
    assert "property var sensor: root.filamentSensors[index]" in qml
    assert "sensor.filament_detected" in qml
    assert "root.controlFeedbackText()" in qml

    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "property var fileRefreshBridgeModel:" in main_qml
    assert 'typeof gcodeFileRefresh === "undefined" ? null : gcodeFileRefresh' in main_qml
    assert (
        "loading: window.fileRefreshBridgeModel ? window.fileRefreshBridgeModel.loading : false"
        in main_qml
    )
    assert (
        'loadError: window.fileRefreshBridgeModel ? window.fileRefreshBridgeModel.lastError : ""'
        in main_qml
    )
    assert "Theme.color3" not in qml
    assert (
        "root.extrudeActionRequested(modelData.action, parseFloat(root.selectedDistance), "
        "parseFloat(root.selectedSpeed))"
        in qml
    )
    assert "printer.gcode.script" not in qml

    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "property real extruderTemperature:" in main_qml
    assert "property real extruderTarget:" in main_qml
    assert "property bool extruderCanExtrude:" in main_qml
    assert "property real extruderPressureAdvance:" in main_qml
    assert "property real extruderSmoothTime:" in main_qml
    assert "property var filamentSensors:" in main_qml
    assert "property bool materialSystemEnabled:" in main_qml
    assert "materialSystemEnabled: window.materialSystemEnabled" in main_qml
    assert "property var excludeObjectNames:" in main_qml
    assert "property var excludedObjectNames:" in main_qml
    assert "property var excludeObjects:" in main_qml
    assert "property real bedMaxX:" in main_qml
    assert "property real bedMaxY:" in main_qml
    assert "property string currentObject:" in main_qml
    assert "extruderTemperature: window.extruderTemperature" in main_qml
    assert "extruderTarget: window.extruderTarget" in main_qml
    assert "extruderCanExtrude: window.extruderCanExtrude" in main_qml
    assert "klippyState: window.klippyState" in main_qml
    assert "webhooksState: window.webhooksState" in main_qml
    assert "extruderPressureAdvance: window.extruderPressureAdvance" in main_qml
    assert "extruderSmoothTime: window.extruderSmoothTime" in main_qml
    assert "filamentSensors: window.filamentSensors" in main_qml
    assert (
        'controlStatus: window.jobControlBridgeModel ? '
        'window.jobControlBridgeModel.lastStatus : ""'
    ) in main_qml
    assert (
        'controlError: window.jobControlBridgeModel ? '
        'window.jobControlBridgeModel.lastError : ""'
    ) in main_qml
    assert "onExtrudeActionRequested: function(action, distance, speed)" in main_qml
    assert "onTemperatureTargetRequested: function(deviceName, target)" in main_qml
    assert "onPressureAdvanceRequested: function(advance, smoothTime)" in main_qml
    assert "window.requestTemperatureTarget(deviceName, target)" in main_qml
    assert "jobControlBridgeModel.requestPressureAdvance(advance, smoothTime)" in main_qml
    assert "onTemperaturePanelRequested" not in main_qml
    assert "jobControlBridgeModel.requestExtrudeFilament(action, distance, speed)" in main_qml
    assert "jobControlBridgeModel.requestLoadFilament(speed)" in main_qml
    assert "jobControlBridgeModel.requestUnloadFilament(speed)" in main_qml


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
    assert 'ListElement { tileLabel: "Network"; tileIcon: "network"' in model_qml
    assert 'ListElement { tileLabel: "Logs"; tileIcon: "logs"' in model_qml
    assert 'ListElement { tileLabel: "Language"; tileIcon: "language"' in model_qml
    assert 'ListElement { tileLabel: "Update"; tileIcon: "update"' in model_qml
    assert 'panelName: "system"' in model_qml
    assert 'panelName: "network"' in model_qml
    assert 'panelName: "logs"' in model_qml
    assert 'panelName: "language"' in model_qml
    assert 'panelName: "update"' in model_qml
    assert 'ListElement { tileLabel: "System"' in model_qml


def test_notification_center_is_globally_routed() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(encoding="utf-8")
    status_qml = Path("src/klippertouch/qml/components/StatusBar.qml").read_text(
        encoding="utf-8"
    )
    more_model_qml = Path("src/klippertouch/qml/models/MoreMenuModel.qml").read_text(
        encoding="utf-8"
    )
    panel_qml = Path("src/klippertouch/qml/panels/NotificationCenterPanel.qml").read_text(
        encoding="utf-8"
    )

    assert "property var notificationBridgeModel" in main_qml
    assert 'typeof notificationModel === "undefined" ? null : notificationModel' in main_qml
    assert '"notifications": "Notifications"' in main_qml
    assert 'case "notifications":' in main_qml
    assert "return notificationCenterComponent" in main_qml
    assert "NotificationCenterPanel {" in main_qml
    assert "notificationModel: window.notificationBridgeModel" in main_qml
    assert "onNotificationsRequested: window.showPanel(\"notifications\")" in main_qml
    assert "notificationUnreadCount: window.notificationBridgeModel" in main_qml
    assert "signal notificationsRequested()" in shell_qml
    assert "notificationUnreadCount: root.notificationUnreadCount" in shell_qml
    assert "onNotificationRequested: root.notificationsRequested()" in shell_qml
    assert "property int notificationUnreadCount" in status_qml
    assert "signal notificationRequested()" in status_qml
    assert "notificationBadge" in status_qml
    assert 'ListElement { tileLabel: "Notifications"; tileIcon: "notification"' in more_model_qml
    assert "required property var metrics" in panel_qml
    assert "property var notificationModel: null" in panel_qml
    assert "notificationModel.markAllRead()" in panel_qml
    assert "notificationModel.clear()" in panel_qml
    assert "No notifications" in panel_qml
    assert 'import "../components"' in panel_qml
    assert "TactileButton {" in panel_qml
    assert 'text: "Mark read"' in panel_qml
    assert 'text: "Clear"' in panel_qml
    assert 'iconName: "notification"' in panel_qml
    assert 'iconName: "clear"' in panel_qml


def test_job_control_events_are_forwarded_to_notifications() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "function notify(level, title, message, source, sticky, actionPanel)" in main_qml
    assert "function showToast(level, title, message)" in main_qml
    assert "function shouldStoreNotification(level, sticky)" in main_qml
    assert "id: toastCard" in main_qml
    assert "id: toastTimer" in main_qml
    assert "anchors.left: parent.left" in main_qml
    assert "anchors.right: parent.right" in main_qml
    assert "appMetrics.actionBarWidth + appMetrics.margin" in main_qml
    assert "width: undefined" not in main_qml
    assert "toastTimer.restart()" in main_qml
    assert "function onToastRequested(level, title, message)" in main_qml
    assert "window.showToast(level, title, message)" in main_qml
    assert "window.shouldStoreNotification(level, sticky)" in main_qml
    assert "notificationBridgeModel.addNotification" in main_qml
    assert "function onStatusChanged()" in main_qml
    assert "function onErrorChanged()" in main_qml
    assert 'window.notify("info", "Command sent"' in main_qml
    assert 'window.notify("error", "Command failed"' in main_qml


def test_splash_panel_handles_system_fault_states() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(
        encoding="utf-8"
    )
    action_bar_qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(
        encoding="utf-8"
    )
    panel_qml = Path("src/klippertouch/qml/panels/SplashPanel.qml").read_text(
        encoding="utf-8"
    )

    assert "property string webhooksState" in main_qml
    assert "property string webhooksMessage" in main_qml
    assert "property bool bootstrapComplete" in main_qml
    assert "property bool startupSplashHoldComplete: false" in main_qml
    assert "property bool startupSplashVisible:" in main_qml
    assert "!window.startupSplashHoldComplete" in main_qml
    assert "id: startupSplashHoldTimer" in main_qml
    assert "interval: 2000" in main_qml
    assert "window.startupSplashHoldComplete = true" in main_qml
    assert "startupSplashHoldTimer.restart()" in main_qml
    assert "function printerReadyForUi()" in main_qml
    assert "property bool systemFaultVisible:" in main_qml
    assert "window.startupSplashVisible || window.systemFaultVisible" in main_qml
    assert "function systemFaultActive()" in main_qml
    assert "function moonrakerFaultActive()" in main_qml
    assert "function klippyFaultActive()" in main_qml
    assert "function webhooksFaultActive()" in main_qml
    assert "window.klippyState.length <= 0 || window.klippyState !== \"ready\"" in main_qml
    assert (
        "function klippyFaultActive() {\n"
        '        return window.klippyState.length <= 0 || window.klippyState !== "ready"'
        in main_qml
    )
    assert 'if (window.webhooksState === "ready")' in main_qml
    assert "sourceComponent: window.startupSplashVisible || window.systemFaultVisible" in main_qml
    assert "return splashComponent" in main_qml
    assert "SplashPanel {" in main_qml
    assert "klippyState: window.klippyState" in main_qml
    assert "moonrakerVersion: window.moonrakerVersion" in main_qml
    assert "webhooksState: window.webhooksState" in main_qml
    assert "webhooksMessage: window.webhooksMessage" in main_qml
    assert "controlStatus: window.jobControlBridgeModel" in main_qml
    assert "controlError: window.jobControlBridgeModel" in main_qml
    assert "onRecoveryActionRequested: function(action)" in main_qml
    assert (
        "navigationEnabled: !(window.startupSplashVisible || window.systemFaultVisible)"
        in main_qml
    )
    assert "property bool navigationEnabled: true" in shell_qml
    assert "navigationEnabled: root.navigationEnabled" in shell_qml
    assert "interactionEnabled: root.navigationEnabled" in shell_qml
    assert "property bool navigationEnabled: true" in action_bar_qml
    assert "enabled: root.navigationEnabled" in action_bar_qml
    status_bar_qml = Path("src/klippertouch/qml/components/StatusBar.qml").read_text(
        encoding="utf-8"
    )
    assert "property bool interactionEnabled: true" in status_bar_qml
    assert "enabled: root.interactionEnabled" in status_bar_qml
    assert "function requestRecoveryControl(action)" in main_qml
    assert "jobControlBridgeModel.requestFirmwareRestart()" in main_qml
    assert "jobControlBridgeModel.requestKlipperRestart()" in main_qml
    assert "bridgeModel.requestStatusRetry()" in main_qml
    assert 'jobControlBridgeModel.requestPlaceholderControl("Restart Moonraker")' not in main_qml
    assert "Moonraker offline" in panel_qml
    assert "Moonraker disconnected" in panel_qml
    assert "Klipper is attempting to start" in panel_qml
    assert "Klippy not ready" in panel_qml
    assert "Shutdown due to webhooks" in panel_qml
    assert "property string controlStatus" in panel_qml
    assert "property string controlError" in panel_qml
    assert "property bool connecting" in panel_qml
    assert "property bool ready: false" in panel_qml
    assert 'property string recoveryPage: "main"' in panel_qml
    assert "property var mainRecoveryActions:" in panel_qml
    assert "property var shutdownRecoveryActions:" in panel_qml
    assert "property var activeRecoveryActions:" in panel_qml
    assert "function recoveryActionModel()" not in panel_qml
    assert "function handleRecoveryAction(action)" in panel_qml
    assert "function triggerRecoveryAction(action)" in panel_qml
    assert 'property string recoveryFeedbackAction: ""' in panel_qml
    assert "id: recoveryFeedbackTimer" in panel_qml
    assert "interval: 160" in panel_qml
    assert "ready: window.printerReadyForUi()" in main_qml
    assert 'return "Preparing interface..."' in panel_qml
    assert "property bool compactVertical" in panel_qml
    assert "root.height < 380" in panel_qml
    assert "function recoveryStatusText()" in panel_qml
    assert "function detailPageSize()" in panel_qml
    assert "function detailPageCount()" in panel_qml
    assert "function detailPageText(pageIndex)" in panel_qml
    assert "Math.ceil(root.activeDetailText.length / root.detailPageSize())" in panel_qml
    assert "property string activeDetailText: root.detail()" in panel_qml
    assert "property int detailPageIndex: 0" in panel_qml
    assert "function setDetailPageIndex(pageIndex)" in panel_qml
    assert "onActiveDetailTextChanged: root.setDetailPageIndex(0)" in panel_qml
    assert (
        "onDetailPageIndexChanged: messagePager.setCurrentIndex(root.detailPageIndex)"
        not in panel_qml
    )
    assert "onCurrentIndexChanged:" not in panel_qml
    assert 'return ""' in panel_qml
    assert "return root.webhooksMessage\n" not in panel_qml
    assert "id: messagePageLoader" in panel_qml
    assert "sourceComponent: root.detailPageIndex < root.detailPageCount()" in panel_qml
    assert "id: detailPageComponent" in panel_qml
    assert "id: servicePageComponent" in panel_qml
    assert "SwipeView {" not in panel_qml
    assert "model: root.detailPageCount()" not in panel_qml
    assert "anchors.bottom: pagerControls.top" in panel_qml
    assert "anchors.bottom: pagerIndicator.top" not in panel_qml
    assert "Repeater {" in panel_qml
    assert "PageIndicator {" not in panel_qml
    assert "id: pagerIndexLabel" in panel_qml
    assert 'text: (root.detailPageIndex + 1) + " / " + root.pagerPageCount()' in panel_qml
    assert "function pagerPageCount()" in panel_qml
    assert "id: previousPageArea" in panel_qml
    assert "id: nextPageArea" in panel_qml
    assert "id: previousPageDepth" in panel_qml
    assert "id: nextPageDepth" in panel_qml
    assert "id: detailLabel" in panel_qml
    assert "root.detailPageText(pageIndex)" in panel_qml
    assert "clip: true" in panel_qml
    assert "ScrollBar.vertical" not in panel_qml
    assert "id: recoveryNavBar" in panel_qml
    assert "anchors.bottom: parent.bottom" in panel_qml
    assert "anchors.bottom: recoveryNavBar.top" in panel_qml
    assert "id: recoveryActions" in panel_qml
    assert "anchors.fill: recoveryNavBar" in panel_qml
    assert "model: root.activeRecoveryActions" in panel_qml
    assert "model: root.recoveryActionModel()" not in panel_qml
    assert "signal recoveryActionRequested(string action)" in panel_qml
    assert '"Firmware Restart"' in panel_qml
    assert '"Restart Klipper"' in panel_qml
    assert '"Shutdown"' in panel_qml
    assert '"iconName": "update"' in panel_qml
    assert '"iconName": "power"' in panel_qml
    assert '"iconName": "restart"' in panel_qml
    assert '"iconName": "settings"' not in panel_qml
    assert "IconTileButton {" in panel_qml
    assert (
        'iconName: modelData.iconName.length > 0 ? modelData.iconName : "placeholder"'
        in panel_qml
    )
    assert "textFontScale: root.metrics.portrait ? 0.62 : 0.76" in panel_qml
    assert "hintFontScale: root.metrics.portrait ? 0.50 : 0.60" in panel_qml
    assert "iconSize: Math.max(16, Math.round(root.metrics.fontSize *" in panel_qml
    assert 'Theme.iconSource(root.iconName.length > 0 ? root.iconName : "placeholder")' in Path(
        "src/klippertouch/qml/components/IconTileButton.qml"
    ).read_text(encoding="utf-8")
    assert '"KlipperTouch Restart"' in panel_qml
    assert '"System Shutdown"' in panel_qml
    assert '"System Restart"' in panel_qml
    assert "id: recoveryPressArea" not in panel_qml
    assert "id: pressArea" in Path("src/klippertouch/qml/components/IconTileButton.qml").read_text(
        encoding="utf-8"
    )
    assert "property bool feedbackActive:" not in panel_qml
    assert "id: recoveryActionDepth" not in panel_qml
    assert "onClicked: root.triggerRecoveryAction(modelData.action)" in panel_qml
    assert '"Retry"' in panel_qml
    assert '"Restart Moonraker"' not in panel_qml
    assert '"Emergency Stop"' not in panel_qml
    assert '"emergency_stop"' not in panel_qml
    assert "root.recoveryActionRequested(action)" in panel_qml
    assert "Printer movement controls are unavailable while recovery is active." in panel_qml


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
    assert 'color: tilePressArea.pressed ? "#182124" : Theme.buttonsBg' in qml
    assert "border.color: tilePressArea.pressed ? Theme.text : root.accent" in qml
    assert "radius: Math.round(root.fontSize)" in qml
    assert "source: Theme.iconSource(root.iconText)" in qml


def test_main_menu_requests_safe_local_panels() -> None:
    qml = Path("src/klippertouch/qml/panels/MainMenuPanel.qml").read_text(encoding="utf-8")
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "signal panelRequested(string panelName)" in qml
    assert "signal targetTemperatureRequested(string deviceName, real target)" in qml
    assert "required property string panelName" in qml
    assert "onActivated: root.panelRequested(panelName)" in qml
    assert "onTargetTemperatureRequested: function(deviceName, target)" in qml
    assert "root.targetTemperatureRequested(deviceName, target)" in qml
    assert "function showPanel(panelName)" in main_qml
    assert "currentPanel = panelName" in main_qml
    assert "onPanelRequested: function(panelName) { window.showPanel(panelName) }" in main_qml
    assert (
        "onTargetTemperatureRequested: function(deviceName, target) {\n"
        "                    window.requestTemperatureTarget(deviceName, target)\n"
        "                }"
    ) in main_qml
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
    assert "signal stopRequested()" in shell_qml
    assert "onActionRequested:" in shell_qml
    assert "case \"back\":" in shell_qml
    assert "case \"home\":" in shell_qml
    assert "case \"menu\":" in shell_qml
    assert "case \"stop\":" in shell_qml
    assert "break" in shell_qml
    assert "function goBack()" in main_qml
    assert "id: panelLoader" in main_qml
    assert 'objectName: "panelLoader"' in main_qml
    assert 'typeof panelLoader.item.goBack === "function"' in main_qml
    assert "if (panelLoader.item.goBack())" in main_qml
    assert "onBackRequested: window.goBack()" in main_qml
    assert "onHomeRequested: window.goHome()" in main_qml
    assert 'onMenuRequested: window.showPanel("more")' in main_qml
    assert "printer.emergency_stop" not in shell_qml
    assert "onStopRequested: window.requestEmergencyStop()" in main_qml
    assert "function requestEmergencyStop()" in main_qml
    assert "jobControlBridgeModel.requestEmergencyStop()" in main_qml
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
    assert "property Item popupParent: null" in component_qml
    assert "property var activeTemperatureModel:" in component_qml
    assert "clip: true" in component_qml
    assert 'ListElement { deviceName: "Extruder"; iconName: "extruder"; temperature: "21" }' in qml
    assert 'ListElement { deviceName: "Heater bed"; iconName: "bed"; temperature: "25" }' in qml
    assert 'ListElement { deviceName: "Pi"; iconName: "heat-up"; temperature: "44" }' in qml
    assert "TemperatureDeviceModel {" in component_qml
    assert "id: fallbackTemperatureModel" in component_qml
    assert "TemperatureDevicePager {" in component_qml
    assert "temperatureModel: root.activeTemperatureModel" in component_qml
    assert "popupParent: root.popupParent" in component_qml
    assert "signal targetTemperatureRequested(string deviceName, real target)" in component_qml
    assert "onTargetTemperatureRequested: function(deviceName, target)" in component_qml
    assert "root.targetTemperatureRequested(deviceName, target)" in component_qml
    assert 'text: "Target (°C)"' in component_qml
    assert "showTargets: true" in component_qml
    assert "color: Theme.mutedText" in component_qml
    assert "ListElement { deviceName:" not in component_qml


def test_temperature_device_pager_uses_page_based_navigation() -> None:
    qml = Path("src/klippertouch/qml/components/TemperatureDevicePager.qml").read_text(
        encoding="utf-8"
    )

    assert 'import "../Theme.js" as Theme' in qml
    assert 'objectName: "temperatureDevicePager"' in qml
    assert "property var temperatureModel: null" in qml
    assert "property int pageIndex: 0" in qml
    assert "property int pageSize:" in qml
    assert "property int pageCountValue: 1" in qml
    assert "property int totalItemCount: 0" in qml
    assert "property int totalItemCount: root.modelCount" not in qml
    assert "function refreshModelCount()" in qml
    assert "function refreshPageMetrics()" in qml
    assert "function scheduleModelCountRefresh()" in qml
    assert "function refreshVisibleItemsImmediately()" in qml
    assert "modelCountRefreshTimer.stop()" in qml
    assert "id: modelCountRefreshTimer" in qml
    assert "interval: 80" in qml
    assert "interval: 1" not in qml
    assert "property int currentItemCount:" in qml
    assert "root.modelCount(root.modelRevision)" in qml
    assert "function pageCount()" in qml
    assert "function pagedModel()" in qml
    assert "function itemAt(pageRow, revision)" in qml
    assert "row >= root.totalItemCount" in qml
    assert "row >= root.modelCount(revision)" not in qml
    assert "property int modelRevision: 0" in qml
    assert "function refreshVisibleItems()" in qml
    assert "root.refreshModelCount()" in qml
    assert "onPageSizeChanged: root.refreshPageMetrics()" in qml
    assert "onPageSizeChanged: root.refreshModelCount()" not in qml
    assert "onActiveTemperatureModelChanged: root.refreshVisibleItemsImmediately()" in qml
    assert "Component.onCompleted: root.refreshVisibleItemsImmediately()" in qml
    assert "function goToPreviousPage()" in qml
    assert "function goToNextPage()" in qml
    assert "function onDataChanged()" in qml
    assert "function onGraphSelectionChanged()" in qml
    assert "property var entry: root.itemAt(index, root.modelRevision)" in qml
    assert "property int touchTargetSize:" in qml
    assert "property bool targetEditorFullscreen: false" in qml
    assert "property bool targetEditorReplaceOnNextInput: false" in qml
    assert "function targetEditorPortrait()" in qml
    assert "return root.editorParentHeight() > root.editorParentWidth()" in qml
    assert "targetColumnWidth" in qml
    assert "actualTargetGrid" in qml
    assert "signal targetTemperatureRequested(string deviceName, real target)" in qml
    assert "function openTargetEditor(deviceName, displayName, actual, target)" in qml
    assert (
        "function openTargetEditorIfSettable(deviceName, displayName, actual, "
        "target, targetSettable)"
    ) in qml
    assert "function positionTargetEditor()" in qml
    assert "function bestExternalEditorRegion(minWidth, minHeight)" in qml
    assert "targetEditorPopup.parent" in qml
    assert "Math.round(parentWidth * 0.5)" in qml
    assert "Math.round(parentHeight * 0.82)" in qml
    assert "targetEditorPopup.dialogWidth" in qml
    assert "targetEditorPopup.dialogHeight" in qml
    assert "function appendTargetDigit(digit)" in qml
    assert "root.targetEditorReplaceOnNextInput = root.targetEditorValue.length > 0" in qml
    assert "if (root.targetEditorReplaceOnNextInput) {" in qml
    assert "root.targetEditorValue = digit" in qml
    assert "root.targetEditorReplaceOnNextInput = false" in qml
    assert "function confirmTargetEditor()" in qml
    assert 'typeof root.activeTemperatureModel.setPendingTarget === "function"' in qml
    assert "root.activeTemperatureModel.setPendingTarget(root.targetEditorDeviceName, value)" in qml
    assert "id: targetEditorPopup" in qml
    assert "parent: root.popupParent === null ? root : root.popupParent" in qml
    assert "id: targetKeypadGrid" in qml
    assert "id: landscapeTargetEditor" in qml
    assert "visible: !root.targetEditorPortrait()" in qml
    assert "anchors.fill: parent" in qml
    assert "Layout.fillHeight: true" in qml
    assert "id: landscapeTargetKeypadGrid" in qml
    assert "id: landscapeBackspaceButton" in qml
    assert "id: landscapeCancelButton" in qml
    assert "id: landscapeDigitRow" in qml
    assert "id: landscapeSetButton" in qml
    assert "visible: root.targetEditorPortrait()" in qml
    assert 'model: ["1", "2", "3", "4", "5", "6", "7", "8", "9"]' in qml
    assert "Layout.minimumWidth: root.touchTargetSize" in qml
    assert "Layout.minimumHeight: root.touchTargetSize" in qml
    assert "Layout.minimumHeight: root.touchTargetSize" in qml
    assert "root.targetTemperatureRequested(root.targetEditorDeviceName, value)" in qml
    assert "id: graphToggleArea" in qml
    assert "id: compactGraphStateBar" in qml
    assert "id: compactGraphStateBorder" in qml
    assert "deviceGraphVisible ? Theme.color4 : \"#465456\"" in qml
    assert "deviceGraphVisible ? Theme.text : Theme.mutedText" in qml
    assert "id: compactValueArea" in qml
    assert "id: cardValueArea" in qml
    assert "id: cardTitleLabel" in qml
    assert "wrapMode: Text.NoWrap" in qml
    assert "maximumLineCount: 1" in qml
    assert (
        "Layout.preferredHeight: Math.max(root.touchTargetSize, "
        "Math.round(root.fontSize * 3.2))"
    ) in qml
    assert (
        'property string targetState: entry.targetState === undefined '
        '? "actual" : entry.targetState'
    ) in qml
    assert (
        'property bool targetSettable: entry.targetSettable === undefined '
        '? false : entry.targetSettable'
    ) in qml
    assert "enabled: targetSettable" in qml
    assert "opacity: targetSettable ? 1.0 : 0.46" in qml
    assert "function targetColor()" in qml
    assert 'if (targetState === "failed")' in qml
    assert 'if (targetState === "pending")' in qml
    assert "color: targetSettable ? targetColor() : Theme.mutedText" in qml
    assert 'text: "Target"' in qml
    assert "visible: root.showTargets" in qml
    assert "WheelHandler {" in qml
    assert "root.goToNextPage()" in qml
    assert "root.goToPreviousPage()" in qml
    assert "Flickable {" not in qml
    assert "GridView {" in qml
    assert "model: root.currentItemCount" in qml
    assert "id: previousPageButton" in qml
    assert "id: nextPageButton" in qml
    assert 'import "../components"' in qml
    assert "component KeypadButton: TactileButton" in qml
    assert "implicitWidth: root.touchTargetSize" in qml
    assert "implicitHeight: root.touchTargetSize" in qml
    assert "padding: 0" in qml
    assert "component PageControlButton: TactileButton" in qml
    assert "textColor: Theme.text" in qml
    assert "accentColor: pageButton.enabled ? Theme.color4 : \"#465456\"" in qml
    assert "property int pageControlReservedHeight:" in qml
    assert "anchors.bottomMargin: root.pageControlReservedHeight" in qml
    assert "enabled: root.pageIndex > 0" in qml
    assert "enabled: root.pageIndex < root.pageCountValue - 1" in qml
    assert "enabled: root.pageIndex < root.pageCount() - 1" not in qml
    assert "visible: root.pageCountValue > 1" in qml
    assert "text: (root.pageIndex + 1) + \" / \" + root.pageCountValue" in qml
    assert "Math.floor(deviceGrid.height / rowHeight)" not in qml
    assert 'typeof root.activeTemperatureModel.toggleGraphDevice === "function"' in qml
    assert "root.activeTemperatureModel.toggleGraphDevice(deviceKey)" in qml
    assert "targetEditorPopup.open()" in qml


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
    assert "signal targetTemperatureRequested(string deviceName, real target)" in qml
    assert "property bool hasExternalTemperatureModel" in qml
    assert "TemperatureSummary {" not in qml
    assert "FakeTemperatureGraph {" in qml
    assert "property int deviceColumns" in qml
    assert "TemperatureDevicePager {" in qml
    assert "onTargetTemperatureRequested: function(deviceName, target)" in qml
    assert "root.targetTemperatureRequested(deviceName, target)" in qml
    assert "deviceColumns: root.deviceColumns" in qml
    assert 'typeof temperatureModel !== "undefined"' in qml
    assert "root.hasExternalTemperatureModel" in qml
    assert 'typeof root.activeTemperatureModel.graphSeriesModel === "undefined"' in qml
    assert "Layout.minimumWidth: 0" in qml
    assert "Layout.minimumHeight: 0" in qml
    assert "root.metrics.portrait" in qml
    assert "target control" in qml
    assert "graph.requestRedraw()" not in qml
    assert "printer.gcode.script" not in qml
    assert "sendTextMessage" not in qml


def test_main_routes_temperature_to_read_only_temperature_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "function componentForPanel(panelName)" in main_qml
    assert 'case "main":' in main_qml
    assert 'case "temperature":' in main_qml
    assert "return temperatureComponent" in main_qml
    assert "return placeholderComponent" in main_qml
    assert "sourceComponent: window.startupSplashVisible || window.systemFaultVisible" in main_qml
    assert "window.componentForPanel(window.currentPanel)" in main_qml
    assert "TemperaturePanel {" in main_qml
    assert "temperatureModel: window.temperatureBridgeModel" in main_qml
    assert "function requestTemperatureTarget(deviceName, target)" in main_qml
    assert "jobControlBridgeModel.requestTemperatureTarget(deviceName, target)" in main_qml
    assert "temperatureBridgeModel.setFailedTarget(deviceName, target)" in main_qml
    assert "onTargetTemperatureRequested: function(deviceName, target)" in main_qml


def test_main_keeps_files_and_job_status_as_separate_routes() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert '"job_status": "Job Status"' in main_qml
    assert 'case "print":' in main_qml
    assert "return filesComponent" in main_qml
    assert 'case "job_status":' in main_qml
    assert "return jobStatusComponent" in main_qml
    assert "property var jobControlBridgeModel" in main_qml
    assert "typeof jobControlModel === \"undefined\" ? null : jobControlModel" in main_qml
    assert "function requestJobControl(action, objectName)" in main_qml
    assert "jobControlBridgeModel.requestPause()" in main_qml
    assert "jobControlBridgeModel.requestResume()" in main_qml
    assert "jobControlBridgeModel.requestCancel()" in main_qml
    assert "jobControlBridgeModel.requestClearJob()" in main_qml
    assert "jobControlBridgeModel.requestSkipObject(objectName)" in main_qml
    assert "jobControlBridgeModel.requestSkipCurrentObject()" in main_qml
    assert "function requestFileControl(action, path)" in main_qml
    assert "Qt.callLater(function() { jobControlBridgeModel.requestStartPrint(path) })" in main_qml
    assert "jobControlBridgeModel.requestStartPrint(path)" in main_qml
    assert "panelLoader.item.handleFilePrintStarted(path)" in main_qml
    assert main_qml.index('window.showPanel("job_status")') < main_qml.index(
        "jobControlBridgeModel.requestStartPrint(path)"
    )
    assert "window.jobControlBridgeModel.lastError.length <= 0" not in main_qml
    assert "jobControlBridgeModel.requestDeleteFile(path)" in main_qml
    assert "function onFileDeleted(path)" in main_qml
    assert "window.gcodeFileBridgeModel.removeFile(path)" in main_qml
    assert "panelLoader.item.handleFileDeleted(path)" in main_qml
    assert (
        "controlStatus: window.jobControlBridgeModel ? "
        'window.jobControlBridgeModel.lastStatus : ""'
    ) in main_qml
    assert (
        "controlError: window.jobControlBridgeModel ? "
        'window.jobControlBridgeModel.lastError : ""'
    )
    assert "onJobActionRequested: function(action, objectName)" in main_qml
    assert "onFileActionRequested: function(action, path)" in main_qml
    assert "onRefreshRequested: function()" in main_qml
    assert "window.fileRefreshBridgeModel.refresh_once()" in main_qml
    assert (
        "controlStatus: window.jobControlBridgeModel ? "
        'window.jobControlBridgeModel.lastStatus : ""'
        in main_qml
    )
    assert (
        "controlError: window.jobControlBridgeModel ? "
        'window.jobControlBridgeModel.lastError : ""'
        in main_qml
    )
    assert "FilesPanel {" in main_qml
    assert "JobStatusPanel {" in main_qml
    assert "fileModel: window.gcodeFileBridgeModel" in main_qml
    assert "filamentUsed: window.filamentUsed" in main_qml
    assert "currentLayer: window.currentLayer" in main_qml
    assert "totalLayers: window.totalLayers" in main_qml
    assert "positionX: window.positionX" in main_qml
    assert "positionY: window.positionY" in main_qml
    assert "positionZ: window.positionZ" in main_qml
    assert "positionE: window.positionE" in main_qml
    assert "homedAxes: window.homedAxes" in main_qml
    assert "requestedSpeed: window.requestedSpeed" in main_qml
    assert "speedFactor: window.speedFactor" in main_qml
    assert "extrudeFactor: window.extrudeFactor" in main_qml
    assert "zOffset: window.zOffset" in main_qml
    assert "maxAccel: window.maxAccel" in main_qml
    assert "maxVelocity: window.maxVelocity" in main_qml
    assert "bedMaxX: window.bedMaxX" in main_qml
    assert "bedMaxY: window.bedMaxY" in main_qml
    assert "excludeObjectNames: window.excludeObjectNames" in main_qml
    assert "excludeObjects: window.excludeObjects" in main_qml
    assert "excludedObjectNames: window.excludedObjectNames" in main_qml
    assert "currentObject: window.currentObject" in main_qml
    assert "temperatureModel: window.temperatureBridgeModel" in main_qml
    assert "fileModel: window.gcodeFileBridgeModel" in main_qml
    assert "function shouldAutoEnterJobStatus()" in main_qml
    assert "function shouldKeepJobStatusVisible()" in main_qml
    assert "function syncJobStatusPanel()" in main_qml
    assert "function syncRequestedPrintState()" in main_qml
    assert 'window.requestedPrintState === "standby"' in main_qml
    assert 'window.printState === "standby"' in main_qml
    assert 'window.currentPanel === "job_status"' in main_qml
    assert 'window.panelStack = ["main", "print"]' in main_qml
    assert 'window.currentPanel = "print"' in main_qml
    assert "onPrintStateChanged: window.syncJobStatusPanel()" in main_qml
    assert "onRequestedPrintStateChanged: window.syncRequestedPrintState()" in main_qml
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
    assert 'case "fans":' in main_qml
    assert "return fanComponent" in main_qml
    assert 'case "network":' in main_qml
    assert 'case "logs":' in main_qml
    assert 'case "language":' in main_qml
    assert 'case "update":' in main_qml
    assert "title: window.panelTitles[window.currentPanel]" in main_qml
    assert "iconName: window.panelIcons[window.currentPanel]" in main_qml
    assert '"more": "More"' in main_qml
    assert '"system": "System"' in main_qml
    assert '"fans": "Fans"' in main_qml
    assert '"network": "Network"' in main_qml
    assert '"logs": "Logs"' in main_qml
    assert '"language": "Language"' in main_qml
    assert '"update": "Update"' in main_qml
    assert "InfoPanel {" in main_qml
    assert "FanPanel {" in main_qml
    assert "MoreMenuPanel {" in main_qml
    assert "hostname: window.hostname" in main_qml
    assert "klippyState: window.klippyState" in main_qml
    assert "klipperVersion: window.klipperVersion" in main_qml
    assert "moonrakerVersion: window.moonrakerVersion" in main_qml
    assert "mcuInfos: window.mcuInfos" in main_qml
    assert "serviceVersions: window.serviceVersions" in main_qml


def test_fan_panel_lists_read_only_and_settable_fans() -> None:
    qml = Path("src/klippertouch/qml/panels/FanPanel.qml").read_text(encoding="utf-8")
    model_qml = Path("src/klippertouch/qml/models/MoreMenuModel.qml").read_text(
        encoding="utf-8"
    )
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'objectName: "fanPanel"' in qml
    assert "property var fanDevices" in qml
    assert "signal fanSpeedRequested(string deviceName, real percent)" in qml
    assert "modelData.speed_settable" in qml
    assert "root.metrics.portrait ? 156 : 144" in qml
    assert "root.metrics.portrait ? 9.8 : 6.4" in qml
    assert "root.metrics.portrait ? 62 : 54" in qml
    assert "root.metrics.portrait ? 3.9 : 2.4" in qml
    assert "Slider {" in qml
    assert "stepSize: 0" in qml
    assert "hasRpm" in qml
    assert "Math.round(fanCard.rpmValue) + \" RPM\"" in qml
    assert "property real savedContentY" in qml
    assert "function restoreScrollPosition()" in qml
    assert "onModelChanged: restoreScrollPosition()" in qml
    assert "onCountChanged: restoreScrollPosition()" in qml
    assert "footer: Item" in qml
    assert "root.fanSpeedRequested(fanCard.modelData.name, fanCard.draftSpeed)" in qml
    assert 'model: [0, 100]' in qml
    assert 'model: [0, 25, 50, 75, 100]' not in qml
    assert "scale: fanShortcutMouse.pressed ? 0.96 : 1.0" in qml
    assert "id: fanShortcutDepth" in qml
    assert "Behavior on scale" in qml
    assert '"auto"' in qml
    assert 'ListElement { tileLabel: "Fans"; tileIcon: "fan"' in model_qml
    assert 'panelName: "fans"' in model_qml
    assert "property var fanDevices: bridgeModel ? bridgeModel.fanDevices : []" in main_qml
    assert "fanDevices: window.fanDevices" in main_qml
    assert "onFanSpeedRequested: function(deviceName, percent)" in main_qml
    assert "jobControlBridgeModel.requestFanSpeed(deviceName, percent)" in main_qml


def test_main_routes_network_and_logs_to_safe_placeholder_panels() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'case "network":' in main_qml
    assert 'case "logs":' in main_qml
    assert 'case "language":' in main_qml
    assert 'case "update":' in main_qml
    assert "return placeholderComponent" in main_qml
    assert '"network": "network"' in main_qml
    assert '"logs": "logs"' in main_qml
    assert '"language": "language"' in main_qml
    assert '"update": "update"' in main_qml


def test_move_panel_is_locked_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property string klippyState" in qml
    assert "property string webhooksState" in qml
    assert "property var moveButtons" in qml
    assert "property var distances" in qml
    assert "component LockedTile: IconTileButton" in qml
    assert "component DirectionButton: Rectangle" in qml
    assert "function arrowGlyph(direction)" in qml
    assert "id: bedRectCanvas" in qml
    assert "id: moveMorePanel" in qml
    assert "id: controlGroupGrid" in qml
    assert "id: motionPad" in qml
    assert "id: motionActions" in qml
    assert "id: positionPanel" in qml
    assert "id: distancePanel" in qml
    assert "id: xyMovePad" in qml
    assert "id: zMovePad" in qml
    assert "direction: modelData.direction" in qml
    assert "id: distanceGrid" in qml
    assert "root.controlFeedbackText()" in qml
    assert "function printerReady()" in qml
    assert "function movementGuardText()" in qml
    assert "function actionAxis(action)" in qml
    assert "function tiltAction(action)" in qml
    assert "function axisHomed(axis)" in qml
    assert "function unhomedMoveAxesText()" in qml
    assert "function jogAction(action)" in qml
    assert "function actionRequiresReady(action)" in qml
    assert "function actionAllowed(action)" in qml
    assert "function actionUnavailableReason(action)" in qml
    assert "function actionHint(action, fallback)" in qml
    assert "function controlFeedbackColor()" in qml
    assert 'return "Printer not ready"' in qml
    assert 'return "Home " + axes + " first"' in qml
    assert 'return "Home " + axis.toUpperCase() + " first"' in qml
    assert 'return "Five-axis controls unavailable"' in qml
    assert 'return "Accelerator leveling unavailable"' in qml
    assert 'return "Z tilt unavailable"' in qml
    assert "var reason = root.actionUnavailableReason(action)" in qml
    assert "return reason.length > 0 ? reason : fallback" in qml
    assert 'hint: modelData.placeholder' in qml
    assert ': root.actionHint(modelData.action, modelData.hint)' in qml
    assert 'hint: root.actionHint("home_uvw", "UVW_HOME")' in qml
    assert 'hint: root.actionHint("accelerator_level", "MOVE=1")' in qml
    assert 'hint: root.actionHint("z_tilt_adjust", "adjust")' in qml
    assert 'return "#ff7777"' in qml
    assert 'return "#d8dee0"' in qml
    assert 'color: root.controlFeedbackColor()' in qml
    assert 'root.axisHomed(root.actionAxis(action))' in qml
    assert "enabled: !modelData.placeholder && root.actionAllowed(modelData.action)" in qml
    assert 'enabled: root.actionAllowed("home_xy")' in qml
    assert 'enabled: root.actionAllowed("home_z")' in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "root.selectDistance(modelData)" in qml
    assert "printer.gcode.script" not in qml
    assert "G0" not in qml
    assert "G28" not in qml


def test_extrude_panel_is_locked_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/ExtrudePanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property var distances" in qml
    assert "property var speeds" in qml
    assert "property var actionButtons" in qml
    assert "property var settingsButtons" in qml
    assert "property real actionFraction: 0.42" in qml
    assert "property real settingsFraction: 0.58" in qml
    assert "component ActionTile: IconTileButton" in qml
    assert "component PlaceholderTile: Rectangle" in qml
    assert "component NozzleStage: Rectangle" in qml
    assert "Layout.preferredWidth: root.metrics.portrait" in qml
    assert "Layout.minimumWidth: 0" in qml
    assert "root.controlFeedbackText()" in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "root.selectDistance(modelData)" in qml
    assert "root.selectSpeed(modelData)" in qml
    assert "printer.gcode.script" not in qml
    assert "M83" not in qml
    assert "G0" not in qml


def test_main_routes_move_and_extrude_to_locked_panels() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert 'case "move":' in main_qml
    assert "return moveComponent" in main_qml
    assert 'case "extrude":' in main_qml
    assert "return extrudeComponent" in main_qml
    assert "MovePanel {" in main_qml
    assert "klippyState: window.klippyState" in main_qml
    assert "webhooksState: window.webhooksState" in main_qml
    assert (
        'controlStatus: window.jobControlBridgeModel ? '
        'window.jobControlBridgeModel.lastStatus : ""'
    ) in main_qml
    assert (
        'controlError: window.jobControlBridgeModel ? '
        'window.jobControlBridgeModel.lastError : ""'
    ) in main_qml
    assert "onMoveActionRequested: function(action, distance, speed)" in main_qml
    assert "function requestMoveControl(action, distance, speed)" in main_qml
    assert "jobControlBridgeModel.requestMoveJog(action, distance, speed)" in main_qml
    assert 'action === "u_minus" || action === "u_plus"' in main_qml
    assert 'action === "v_minus" || action === "v_plus"' in main_qml
    assert 'action === "w_minus" || action === "w_plus"' in main_qml
    assert 'jobControlBridgeModel.requestHome("xy")' in main_qml
    assert 'jobControlBridgeModel.requestHome("z")' in main_qml
    assert 'jobControlBridgeModel.requestHome("all")' in main_qml
    assert 'jobControlBridgeModel.requestHome("uvw")' in main_qml
    assert "jobControlBridgeModel.requestZTiltAdjust()" in main_qml
    assert "jobControlBridgeModel.requestAcceleratorLevel()" in main_qml
    assert "positionU: window.positionU" in main_qml
    assert "positionV: window.positionV" in main_qml
    assert "positionW: window.positionW" in main_qml
    assert "fiveAxisAvailable: window.fiveAxisAvailable" in main_qml
    assert "acceleratorLevelAvailable: window.acceleratorLevelAvailable" in main_qml
    assert "zTiltAvailable: window.zTiltAvailable" in main_qml
    assert "jobControlBridgeModel.requestDisableMotors()" in main_qml
    assert "ExtrudePanel {" in main_qml


def test_main_uses_responsive_base_shell_and_main_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "BaseShell {" in main_qml
    assert "Loader {" in main_qml
    assert "Metrics {" in main_qml
    assert 'property string currentPanel: "main"' in main_qml
    assert "onCurrentPanelChanged" in main_qml
    assert 'typeof bridgeModel.setActivePanel === "function"' in main_qml
    assert "bridgeModel.setActivePanel(window.currentPanel)" in main_qml
    assert 'property var panelTitles: ({"main": "Home"' in main_qml
    assert "panelTitle: window.panelTitles[window.currentPanel]" in main_qml
    assert "sourceComponent: window.startupSplashVisible || window.systemFaultVisible" in main_qml
    assert "window.componentForPanel(window.currentPanel)" in main_qml


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
