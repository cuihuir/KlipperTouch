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


def test_responsive_layout_components_exist() -> None:
    qml_dir = Path("src/klippertouch/qml")
    expected = [
        qml_dir / "Metrics.qml",
        qml_dir / "components" / "BaseShell.qml",
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
        qml_dir / "panels" / "MovePanel.qml",
        qml_dir / "panels" / "ExtrudePanel.qml",
    ]

    missing = [path for path in expected if not path.exists()]

    assert missing == []


def test_files_panel_is_only_read_only_file_management() -> None:
    qml = Path("src/klippertouch/qml/panels/FilesPanel.qml").read_text(encoding="utf-8")

    assert "property var fileModel" in qml
    assert 'text: "G-Code files"' not in qml
    assert 'property string rootPath: "gcodes"' in qml
    assert '"label": "Name"' in qml
    assert '"label": "Date"' in qml
    assert '"label": "Size"' in qml
    assert "No G-Code files found" in qml
    assert "Loading files..." in qml
    assert "function currentPathLabel" in qml
    assert "root.currentPathLabel()" in qml
    assert "function fileListPreferredHeight()" in qml
    assert "Layout.preferredHeight: root.fileListPreferredHeight()" in qml
    assert "function emptyTitle" in qml
    assert "Current folder is empty" in qml
    assert 'fileList.count + " items"' in qml
    assert "Search files" in qml
    assert "activeFileModel.setFilterText(text)" in qml
    assert "id: compactControlRow" in qml
    assert "id: pathLabel" in qml
    assert "sortDescending" in qml
    assert "Layout.fillWidth: true" in qml
    assert "activeFileModel.breadcrumbs" not in qml
    assert "breadcrumbText" not in qml
    assert "property bool compactFileRows" in qml
    assert "root.compactFileRows ? 2 : 5" in qml
    assert "root.activeFileModel.selectPath(path, isDirectory)" in qml
    assert "selectedPath" in qml
    assert "selectedDisplayName" in qml
    assert "selectedSizeLabel" in qml
    assert "selectedModifiedLabel" in qml
    assert "selectedPermissions" in qml
    assert "selectedPreviewThumbnailUrl" in qml
    assert "function selectedMetadataModel()" in qml
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
    assert "root.activeFileModel.selectedPreviewThumbnailUrl" in qml
    assert "id: detailsPanel" in qml
    assert "Read-only file details" in qml
    assert "id: selectedMetadataFlickable" in qml
    assert "id: selectedMetadataGrid" in qml
    assert "contentHeight: selectedMetadataGrid.implicitHeight" in qml
    assert "ScrollBar.vertical: ScrollBar" in qml
    assert "policy: ScrollBar.AsNeeded" in qml
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
    assert "property real positionX" in qml
    assert "property real positionY" in qml
    assert "property real positionZ" in qml
    assert "property real positionE" in qml
    assert "property string homedAxes" in qml
    assert "property var temperatureModel: null" in qml
    assert "property var fileModel: null" in qml
    assert "property var excludeObjectNames: []" in qml
    assert "property var excludedObjectNames: []" in qml
    assert "property string currentObject" in qml
    assert "signal objectExcludeRequested(string objectName)" in qml
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
    assert "id: jobActionGrid" in qml
    assert "component StatusCard: Rectangle" in qml
    assert "component MetricPill: Rectangle" in qml
    assert "component JobButton: Button" in qml
    assert "property int jobButtonHeight" in qml
    assert "property int jobButtonWidth" in qml
    assert 'readonly property color neutralAccent: "#8b9496"' in qml
    assert 'readonly property color mutedDangerAccent: "#9a8582"' in qml
    assert "property string buttonRole" in qml
    assert "property string iconText" in qml
    assert "function jobActionGridHeight()" in qml
    assert "function jobActionGridWidth()" in qml
    assert "function jobActionButtonWidth()" in qml
    assert "gradient: Gradient" in qml
    assert "id: statusPill" in qml
    assert "id: jobHeroLayout" in qml
    assert "id: compactProgressBox" in qml
    assert "function jobHeroHeight()" in qml
    assert "function temperatureStripHeight()" in qml
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
    assert "root.metrics.portrait && root.height > 760" in qml
    assert "&& root.temperatureModel" in qml
    assert "Layout.maximumWidth: Math.max(160" in qml
    assert "id: progressRail" in qml
    assert "id: progressFill" in qml
    assert 'iconText: "||"' in qml
    assert 'iconText: "X"' in qml
    assert 'iconText: "OBJ"' in qml
    assert 'iconText: "ADV"' in qml
    assert 'buttonRole: "danger"' in qml
    assert "background: Rectangle" in qml
    assert 'color: controlRoot.enabled ? "#263033" : "#151a1b"' in qml
    assert "implicitHeight: root.jobButtonHeight" in qml
    assert "Layout.preferredHeight: root.jobActionGridHeight()" in qml
    assert "Layout.preferredWidth: root.jobActionGridWidth()" in qml
    assert "Layout.preferredWidth: root.jobActionButtonWidth()" in qml
    assert "columns: root.metrics.portrait ? 2 : 4" in qml
    assert "Layout.preferredHeight: root.jobButtonHeight" in qml
    assert "Layout.preferredWidth: root.jobButtonWidth" in qml
    assert "Layout.alignment: Qt.AlignVCenter" in qml
    assert "root.primaryActionLabel()" in qml
    assert 'root.printState === "paused" ? "Resume" : "Pause"' in qml
    assert 'text: "Cancel"' in qml
    assert 'text: "Skip Object"' in qml
    assert 'root.detailPage = "exclude"' in qml
    assert 'text: "Advanced"' in qml
    assert "enabled: false" in qml
    assert "readonlyActionHint" in qml
    assert "property string detailPage" in qml
    assert 'root.detailPage = "advanced"' in qml
    assert 'root.detailPage = "summary"' in qml
    assert "id: advancedPage" in qml
    assert "id: excludePage" in qml
    assert "root.currentObject" in qml
    assert "model: root.excludeObjectNames" in qml
    assert "root.excludedObjectNames.indexOf(modelData) >= 0" in qml
    assert "root.objectExcludeRequested(modelData)" in qml
    assert "qmllint disable missing-property" in qml
    assert "function goBack()" in qml
    assert 'if (root.detailPage !== "summary")' in qml
    assert "return true" in qml
    assert "return false" in qml
    assert "Popup {" not in qml
    assert 'text: "Back"' not in qml
    assert "root.zOffsetLabel()" in qml
    assert "root.percentLabel(root.speedFactor)" in qml
    assert "root.percentLabel(root.extrudeFactor)" in qml
    assert "signal zOffsetAdjustRequested(real delta)" in qml
    assert "signal speedFactorAdjustRequested(real delta)" in qml
    assert "signal extrudeFactorAdjustRequested(real delta)" in qml
    assert "id: advancedControlRepeater" in qml
    assert "Layout.maximumHeight: 0" in qml
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


def test_move_panel_exposes_read_only_position_without_controls() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "property real positionX" in qml
    assert "property real positionY" in qml
    assert "property real positionZ" in qml
    assert "property real positionE" in qml
    assert "property string homedAxes" in qml
    assert 'property var distances: [".1", ".5", "1", "5", "10", "25", "50"]' in qml
    assert '"label": "Home"' in qml
    assert '"label": "Motors Off"' in qml
    assert "component LockedTile: Rectangle" in qml
    assert "root.positionX.toFixed(2)" in qml
    assert "root.homedAxes.length > 0" in qml
    assert "property string selectedDistance" in qml
    assert "function selectDistance(distance)" in qml
    assert "root.selectedDistance === modelData" in qml
    assert "Theme.color3" in qml
    assert "id: movePadGrid" in qml
    assert "id: distanceGrid" in qml
    assert "id: positionGrid" in qml
    assert "M18" not in qml
    assert "printer.gcode.script" not in qml


def test_extrude_panel_exposes_read_only_extruder_state_without_controls() -> None:
    qml = Path("src/klippertouch/qml/panels/ExtrudePanel.qml").read_text(encoding="utf-8")

    assert "property real extruderTemperature" in qml
    assert "property real extruderTarget" in qml
    assert "property real positionE" in qml
    assert "property string selectedDistance" in qml
    assert "property string selectedSpeed" in qml
    assert "property var actionButtons" in qml
    assert "property var settingsButtons" in qml
    assert '"label": "Load"' in qml
    assert '"label": "Unload"' in qml
    assert '"label": "Temperature"' in qml
    assert '"label": "Pressure Advance"' in qml
    assert '"label": "Retraction"' in qml
    assert '"label": "Spoolman"' in qml
    assert "component LockedTile: Rectangle" in qml
    assert "function selectDistance(distance)" in qml
    assert "function selectSpeed(speed)" in qml
    assert "root.selectedDistance === modelData" in qml
    assert "root.selectedSpeed === modelData" in qml
    assert "root.extruderTemperature.toFixed(1)" in qml
    assert "root.extruderTarget.toFixed(1)" in qml
    assert "root.positionE.toFixed(2)" in qml
    assert "printer.gcode.script" not in qml

    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "property real extruderTemperature:" in main_qml
    assert "property real extruderTarget:" in main_qml
    assert "property var excludeObjectNames:" in main_qml
    assert "property var excludedObjectNames:" in main_qml
    assert "property string currentObject:" in main_qml
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
    assert 'panelName: "system"' in model_qml
    assert 'panelName: "network"' in model_qml
    assert 'panelName: "logs"' in model_qml
    assert 'panelName: "language"' in model_qml
    assert 'panelName: "update"' in model_qml
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
    assert "id: panelLoader" in main_qml
    assert 'objectName: "panelLoader"' in main_qml
    assert 'typeof panelLoader.item.goBack === "function"' in main_qml
    assert "if (panelLoader.item.goBack())" in main_qml
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
    assert "TemperatureDevicePager {" in component_qml
    assert "temperatureModel: root.activeTemperatureModel" in component_qml
    assert 'text: "Target (°C)"' in component_qml
    assert "showTargets: true" in component_qml
    assert "color: Theme.mutedText" in component_qml
    assert "ListElement { deviceName:" not in component_qml


def test_temperature_device_pager_uses_page_based_navigation() -> None:
    qml = Path("src/klippertouch/qml/components/TemperatureDevicePager.qml").read_text(
        encoding="utf-8"
    )

    assert 'import "../Theme.js" as Theme' in qml
    assert "property var temperatureModel: null" in qml
    assert "property int pageIndex: 0" in qml
    assert "property int pageSize:" in qml
    assert "property int currentItemCount:" in qml
    assert "function pageCount()" in qml
    assert "function pagedModel()" in qml
    assert "function itemAt(pageRow, revision)" in qml
    assert "property int modelRevision: 0" in qml
    assert "function refreshVisibleItems()" in qml
    assert "function goToPreviousPage()" in qml
    assert "function goToNextPage()" in qml
    assert "function onDataChanged()" in qml
    assert "function onGraphSelectionChanged()" in qml
    assert "property var entry: root.itemAt(index, root.modelRevision)" in qml
    assert "property int touchTargetSize:" in qml
    assert "property bool targetEditorFullscreen: false" in qml
    assert "targetColumnWidth" in qml
    assert "actualTargetGrid" in qml
    assert "signal targetTemperatureRequested(string deviceName, real target)" in qml
    assert "function openTargetEditor(deviceName, displayName, actual, target)" in qml
    assert "function positionTargetEditor()" in qml
    assert "function bestExternalEditorRegion(minWidth, minHeight)" in qml
    assert "targetEditorPopup.parent" in qml
    assert "function appendTargetDigit(digit)" in qml
    assert "function confirmTargetEditor()" in qml
    assert 'typeof root.activeTemperatureModel.setPendingTarget === "function"' in qml
    assert "root.activeTemperatureModel.setPendingTarget(root.targetEditorDeviceName, value)" in qml
    assert "id: targetEditorPopup" in qml
    assert "parent: Overlay.overlay" in qml
    assert "id: targetKeypadGrid" in qml
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
    assert "function targetColor()" in qml
    assert 'if (targetState === "failed")' in qml
    assert 'if (targetState === "pending")' in qml
    assert "color: targetColor()" in qml
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
    assert "property int pageControlReservedHeight:" in qml
    assert "anchors.bottomMargin: root.pageControlReservedHeight" in qml
    assert "enabled: root.pageIndex > 0" in qml
    assert "enabled: root.pageIndex < root.pageCount() - 1" in qml
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
    assert "property bool hasExternalTemperatureModel" in qml
    assert "TemperatureSummary {" not in qml
    assert "FakeTemperatureGraph {" in qml
    assert "property int deviceColumns" in qml
    assert "TemperatureDevicePager {" in qml
    assert "deviceColumns: root.deviceColumns" in qml
    assert 'typeof temperatureModel !== "undefined"' in qml
    assert "root.hasExternalTemperatureModel" in qml
    assert 'typeof root.activeTemperatureModel.graphSeriesModel === "undefined"' in qml
    assert "Layout.minimumWidth: 0" in qml
    assert "Layout.minimumHeight: 0" in qml
    assert "root.metrics.portrait" in qml
    assert "readonly" in qml
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
    assert "excludeObjectNames: window.excludeObjectNames" in main_qml
    assert "excludedObjectNames: window.excludedObjectNames" in main_qml
    assert "currentObject: window.currentObject" in main_qml
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
    assert "title: window.panelTitles[window.currentPanel]" in main_qml
    assert "iconName: window.panelIcons[window.currentPanel]" in main_qml
    assert '"more": "More"' in main_qml
    assert '"system": "System"' in main_qml
    assert '"network": "Network"' in main_qml
    assert '"logs": "Logs"' in main_qml
    assert '"language": "Language"' in main_qml
    assert '"update": "Update"' in main_qml
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
    assert "return placeholderComponent" in main_qml
    assert '"network": "main"' in main_qml
    assert '"logs": "printer"' in main_qml
    assert '"language": "settings"' in main_qml
    assert '"update": "printer"' in main_qml


def test_move_panel_is_locked_and_responsive() -> None:
    qml = Path("src/klippertouch/qml/panels/MovePanel.qml").read_text(encoding="utf-8")

    assert "required property var metrics" in qml
    assert "property var moveButtons" in qml
    assert "property var distances" in qml
    assert "component LockedTile: Rectangle" in qml
    assert "id: movePadGrid" in qml
    assert "id: distanceGrid" in qml
    assert "Controls locked" in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "root.selectDistance(modelData)" in qml
    assert "printer.gcode.script" not in qml
    assert "G1" not in qml
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
    assert "Layout.preferredWidth: root.metrics.portrait" in qml
    assert "Layout.minimumWidth: 0" in qml
    assert "Extrusion locked" in qml
    assert "root.metrics.portrait" in qml
    assert "Repeater {" in qml
    assert "root.selectDistance(modelData)" in qml
    assert "root.selectSpeed(modelData)" in qml
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
    assert "onCurrentPanelChanged" in main_qml
    assert 'typeof bridgeModel.setActivePanel === "function"' in main_qml
    assert "bridgeModel.setActivePanel(window.currentPanel)" in main_qml
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
