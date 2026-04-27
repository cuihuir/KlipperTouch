import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    objectName: "jobStatusPanel"
    required property var metrics
    property string printState: "standby"
    property string printFilename: ""
    property real printProgress: 0
    property string printMessage: ""
    property real printDuration: 0
    property real totalDuration: 0
    property real filamentUsed: 0
    property int currentLayer: 0
    property int totalLayers: 0
    property real requestedSpeed: 0
    property real speedFactor: 100
    property real extrudeFactor: 100
    property real zOffset: 0
    property real maxAccel: 0
    property real maxVelocity: 0
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
    property string homedAxes: ""
    property var temperatureModel: null
    property var fileModel: null
    property var excludeObjectNames: []
    property var excludedObjectNames: []
    property string currentObject: ""
    property string detailPage: "summary"
    property string pendingJobAction: ""
    property string pendingJobObject: ""
    property string controlStatus: ""
    property string controlError: ""
    property string requestedPrintState: ""
    readonly property color neutralAccent: "#8b9496"
    readonly property color mutedDangerAccent: "#9a8582"
    readonly property color accentColor: root.stateAccentColor()
    property int jobButtonHeight: Math.min(54, Math.max(48, Math.round(root.metrics.fontSize * 2.65)))
    property int jobButtonWidth: Math.min(156, Math.max(132, Math.round(root.metrics.fontSize * 7.8)))
    signal zOffsetAdjustRequested(real delta)
    signal speedFactorAdjustRequested(real delta)
    signal extrudeFactorAdjustRequested(real delta)
    signal objectExcludeRequested(string objectName)
    signal jobActionRequested(string action, string objectName)

    component StatusCard: Rectangle {
        id: statusCard
        property color accent: root.accentColor
        default property alias contentData: statusContent.data

        color: "#081112"
        border.color: statusCard.accent
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.42)
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#101b1e" }
            GradientStop { position: 0.58; color: "#081112" }
            GradientStop { position: 1.0; color: "#050809" }
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 2
            color: statusCard.accent
            opacity: 0.8
        }

        ColumnLayout {
            id: statusContent
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap
        }
    }

    component MetricPill: Rectangle {
        id: metricRoot
        property string label: ""
        property string value: ""
        property color accent: "#263233"

        implicitHeight: Math.max(32, Math.round(root.metrics.fontSize * 2.1))
        color: "#091314"
        border.color: metricRoot.accent
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.28)
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#101a1c" }
            GradientStop { position: 1.0; color: "#071011" }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Math.max(7, Math.round(root.metrics.fontSize * 0.45))
            anchors.rightMargin: anchors.leftMargin
            spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.3))

            Label {
                color: Theme.mutedText
                text: metricRoot.label
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: metricRoot.value
                horizontalAlignment: Text.AlignRight
                elide: Text.ElideRight
                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.86))
            }
        }
    }

    component JobButton: Button {
        id: controlRoot
        property color accent: root.neutralAccent
        property string buttonRole: "normal"
        property string iconText: ""
        readonly property color roleAccent: buttonRole === "danger"
            ? root.mutedDangerAccent
            : buttonRole === "primary" ? root.accentColor : accent
        implicitHeight: root.jobButtonHeight
        implicitWidth: root.jobButtonWidth

        contentItem: RowLayout {
            spacing: Math.max(5, Math.round(root.metrics.fontSize * 0.32))

            Label {
                visible: controlRoot.iconText.length > 0
                Layout.preferredWidth: Math.max(24, Math.round(root.metrics.fontSize * 1.55))
                Layout.fillHeight: true
                color: controlRoot.enabled ? controlRoot.roleAccent : Theme.mutedText
                text: controlRoot.iconText
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
            }

            Label {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: controlRoot.enabled ? Theme.text : Theme.mutedText
                text: controlRoot.text
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.82))
            }
        }

        background: Rectangle {
            color: controlRoot.enabled ? "#263033" : "#151a1b"
            border.color: controlRoot.enabled ? controlRoot.roleAccent : "#263233"
            border.width: controlRoot.enabled ? 2 : 1
            radius: Math.round(root.metrics.fontSize * 0.32)
            opacity: controlRoot.enabled ? 1.0 : 0.72
            gradient: Gradient {
                GradientStop {
                    position: 0.0
                    color: controlRoot.enabled ? "#142126" : "#151a1b"
                }
                GradientStop {
                    position: 1.0
                    color: controlRoot.enabled ? "#091112" : "#101415"
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: controlRoot.enabled ? 3 : 1
                color: controlRoot.roleAccent
                opacity: controlRoot.enabled ? 0.85 : 0.25
                radius: parent.radius
            }
        }
    }

    component JobActionPreview: Rectangle {
        id: previewRoot
        readonly property bool confirmButtonVisible: root.confirmationRequired()

        Layout.fillWidth: true
        Layout.preferredHeight: root.metrics.portrait
            ? Math.max(78, Math.round(root.metrics.fontSize * 5.4))
            : Math.max(62, Math.round(root.metrics.fontSize * 4.2))
        Layout.fillHeight: false
        visible: root.pendingJobAction.length > 0
        color: root.pendingJobAction === "cancel" ? "#181311" : "#111819"
        border.color: root.pendingJobAction === "cancel" ? "#4a3430" : "#354346"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.32)

        GridLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            columns: root.metrics.portrait ? 1 : 2
            rowSpacing: Math.max(4, Math.round(root.metrics.fontSize * 0.28))
            columnSpacing: root.metrics.gap

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: root.confirmationRequired() ? "Confirmation preview only" : "Action staged"
                    font.bold: true
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: root.pendingJobActionLabel()
                    elide: Text.ElideMiddle
                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                }
            }

            RowLayout {
                Layout.fillWidth: root.metrics.portrait
                Layout.alignment: root.metrics.portrait ? Qt.AlignRight : Qt.AlignVCenter
                Layout.preferredWidth: root.metrics.portrait
                    ? -1
                    : root.jobButtonWidth * 2 + root.metrics.gap
                Layout.preferredHeight: root.jobButtonHeight
                Layout.fillHeight: false
                spacing: root.metrics.gap

                JobButton {
                    Layout.fillWidth: root.metrics.portrait
                    visible: previewRoot.confirmButtonVisible
                    text: "Confirm"
                    enabled: true
                    onClicked: {
                        root.jobActionRequested(root.pendingJobAction, root.pendingJobObject)
                        root.clearJobAction()
                    }
                }

                JobButton {
                    Layout.fillWidth: root.metrics.portrait
                    text: "Dismiss"
                    onClicked: root.clearJobAction()
                }
            }
        }
    }

    component SummaryZone: Rectangle {
        id: zoneRoot
        property string title: ""
        property string primaryLabel: ""
        property string primaryValue: ""
        property var rows: []
        signal activated()

        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.1))
        color: "#101617"
        border.color: summaryTap.pressed ? root.accentColor : "#354043"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.34)
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#111a1c" }
            GradientStop { position: 0.64; color: "#0b1314" }
            GradientStop { position: 1.0; color: "#070d0e" }
        }

        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 3
            color: root.neutralAccent
            opacity: 0.62
            radius: parent.radius
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Math.max(8, Math.round(root.metrics.fontSize * 0.55))
            spacing: Math.max(3, Math.round(root.metrics.fontSize * 0.22))

            RowLayout {
                Layout.fillWidth: true
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: zoneRoot.title
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.96))
                }

                Label {
                    color: Theme.mutedText
                    text: "Details"
                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Label {
                    color: Theme.mutedText
                    text: zoneRoot.primaryLabel
                    elide: Text.ElideRight
                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: zoneRoot.primaryValue
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Math.max(20, Math.round(root.metrics.fontSize * 1.38))
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: Math.max(1, Math.round(root.metrics.fontSize * 0.08))

                Repeater {
                    model: zoneRoot.rows

                    RowLayout {
                        required property var modelData

                        Layout.fillWidth: true
                        spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.28))

                        Label {
                            color: Theme.mutedText
                            text: modelData.label
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: modelData.value
                            horizontalAlignment: Text.AlignRight
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.78))
                        }
                    }
                }
            }
        }

        MouseArea {
            id: summaryTap
            anchors.fill: parent
            onClicked: zoneRoot.activated()
        }
    }

    function durationLabel(seconds) {
        var safeSeconds = Math.max(0, Math.round(seconds))
        var minutes = Math.floor(safeSeconds / 60)
        var hours = Math.floor(minutes / 60)
        minutes = minutes % 60
        if (hours > 0) {
            return hours + "h " + minutes + "m"
        }
        return minutes + "m"
    }

    function remainingLabel() {
        if (root.totalDuration <= 0 || root.printDuration <= 0) {
            return "-"
        }
        return root.durationLabel(Math.max(0, root.totalDuration - root.printDuration))
    }

    function filamentLabel() {
        return (root.filamentUsed / 1000).toFixed(1) + " m"
    }

    function layerLabel() {
        if (root.totalLayers > 0) {
            return root.currentLayer + " / " + root.totalLayers
        }
        if (root.currentLayer > 0) {
            return String(root.currentLayer)
        }
        return "-"
    }

    function percentLabel(value) {
        return Math.round(value) + "%"
    }

    function speedLabel(value) {
        if (value <= 0) {
            return "-"
        }
        return Math.round(value) + " mm/s"
    }

    function accelLabel() {
        if (root.maxAccel <= 0) {
            return "-"
        }
        return Math.round(root.maxAccel) + " mm/s^2"
    }

    function zOffsetLabel() {
        return root.zOffset.toFixed(2) + " mm"
    }

    function positionLabel() {
        return "X " + root.positionX.toFixed(2)
            + "  Y " + root.positionY.toFixed(2)
            + "  Z " + root.positionZ.toFixed(2)
    }

    function fileEstimatedTimeLabel() {
        if (!root.fileModel) {
            return "-"
        }
        root.fileModel.metadataRevision
        return root.fileModel.fileEstimatedTimeLabelFor(root.printFilename)
    }

    function fileFilamentTotalLabel() {
        if (!root.fileModel) {
            return "-"
        }
        root.fileModel.metadataRevision
        return root.fileModel.fileFilamentTotalLabelFor(root.printFilename)
    }

    function fileObjectHeightLabel() {
        if (!root.fileModel) {
            return "-"
        }
        root.fileModel.metadataRevision
        return root.fileModel.fileObjectHeightLabelFor(root.printFilename)
    }

    function fileLayerHeightLabel() {
        if (!root.fileModel) {
            return "-"
        }
        root.fileModel.metadataRevision
        return root.fileModel.fileLayerHeightLabelFor(root.printFilename)
    }

    function stateHeadline() {
        var state = root.effectivePrintState()
        if (state === "paused") {
            return "Paused"
        }
        if (state === "complete") {
            return "Completed"
        }
        if (state === "cancelled") {
            return "Cancelled"
        }
        if (state === "error") {
            return "Printer error"
        }
        return "Printing"
    }

    function stateMessage() {
        if (root.printMessage.length > 0) {
            return root.printMessage
        }
        var state = root.effectivePrintState()
        if (state === "paused") {
            return "Print paused. Print status remains visible."
        }
        if (state === "complete") {
            return "Print completed. Print status remains visible."
        }
        if (state === "cancelled") {
            return "Print cancelled. Print status remains visible."
        }
        if (state === "error") {
            return "Printer error reported. Print status remains visible."
        }
        return root.printFilename.length > 0 ? root.printFilename : "Current print status"
    }

    function stateAccentColor() {
        var state = root.effectivePrintState()
        if (state === "paused") {
            return "#918a7f"
        }
        if (state === "complete") {
            return "#87908a"
        }
        if (state === "cancelled") {
            return "#837e7a"
        }
        if (state === "error") {
            return root.mutedDangerAccent
        }
        return root.neutralAccent
    }

    function stateProgressValue() {
        if (root.printState === "complete") {
            return 1
        }
        return Math.max(0, Math.min(1, root.printProgress / 100))
    }

    function primaryActionLabel() {
        return root.effectivePrintState() === "paused" ? "Resume" : "Pause"
    }

    function terminalJobState() {
        var state = root.effectivePrintState()
        return state === "cancelled" || state === "complete"
    }

    function effectivePrintState() {
        if (root.printState === "complete"
                || root.printState === "cancelled"
                || root.printState === "error"
                || root.printState === "paused") {
            return root.printState
        }
        return root.requestedPrintState.length > 0 ? root.requestedPrintState : root.printState
    }

    function readonlyActionHint(actionName) {
        return actionName + " is staged for the control layer."
    }

    function controlFeedbackText() {
        return root.controlError.length > 0 ? root.controlError : root.controlStatus
    }

    function requestJobAction(action, objectName) {
        root.pendingJobAction = action
        root.pendingJobObject = objectName || ""
    }

    function stageImmediateJobAction(action) {
        root.clearJobAction()
        root.jobActionRequested(action, "")
    }

    function clearJobAction() {
        root.pendingJobAction = ""
        root.pendingJobObject = ""
    }

    function confirmationRequired() {
        return root.pendingJobAction === "cancel" || root.pendingJobAction === "skip"
    }

    function pendingJobActionLabel() {
        if (root.pendingJobAction === "cancel") {
            return "Cancel " + (root.printFilename.length > 0 ? root.printFilename : "current print")
        }
        if (root.pendingJobAction === "skip") {
            return "Skip object " + (root.pendingJobObject.length > 0 ? root.pendingJobObject : "-")
        }
        return ""
    }

    function jobActionGridHeight() {
        var buttonCount = root.terminalJobState() ? 1 : 4
        var columns = root.metrics.portrait ? 2 : 4
        var rows = Math.ceil(buttonCount / columns)
        return root.jobButtonHeight * rows + root.metrics.gap * (rows - 1)
    }

    function jobActionGridWidth() {
        if (root.terminalJobState()) {
            return root.clearActionButtonWidth()
        }
        var columns = root.metrics.portrait ? 2 : 4
        return root.jobButtonWidth * columns + root.metrics.gap * (columns - 1)
    }

    function jobActionButtonWidth() {
        return root.jobButtonWidth
    }

    function clearActionButtonWidth() {
        var minWidth = Math.max(196, Math.round(root.metrics.fontSize * 12.5))
        var maxWidth = root.metrics.portrait
            ? Math.max(minWidth, root.width - root.metrics.gap * 4)
            : root.jobButtonWidth * 2 + root.metrics.gap
        return Math.min(maxWidth, Math.max(minWidth, root.jobButtonWidth))
    }

    function jobHeroHeight() {
        if (root.metrics.portrait) {
            return Math.max(196, Math.round(root.metrics.fontSize * 12.2))
        }
        return Math.max(146, Math.round(root.metrics.fontSize * 9.2))
    }

    function temperatureStripHeight() {
        return Math.max(
            root.metrics.portrait ? 60 : 50,
            Math.round(root.metrics.fontSize * (root.metrics.portrait ? 3.8 : 3.1))
        )
    }

    function summaryZoneRows(zone) {
        if (zone === "time") {
            return [
                {"label": "Elapsed", "value": root.durationLabel(root.printDuration)},
                {"label": "Total", "value": root.durationLabel(root.totalDuration)}
            ]
        }
        if (zone === "motion") {
            return [
                {"label": "Speed", "value": root.speedLabel(root.requestedSpeed)},
                {"label": "Z offset", "value": root.zOffsetLabel()}
            ]
        }
        if (zone === "extrusion") {
            return [
                {"label": "Flow", "value": root.percentLabel(root.extrudeFactor)},
                {"label": "Total", "value": root.fileFilamentTotalLabel()}
            ]
        }
        return []
    }

    function groupedSummaryModel() {
        return [
            {
                "title": "Time",
                "primaryLabel": "Remaining",
                "primaryValue": root.remainingLabel(),
                "rows": root.summaryZoneRows("time")
            },
            {
                "title": "Motion",
                "primaryLabel": "Layer",
                "primaryValue": root.layerLabel(),
                "rows": root.summaryZoneRows("motion")
            },
            {
                "title": "Material",
                "primaryLabel": "Used",
                "primaryValue": root.filamentLabel(),
                "rows": root.summaryZoneRows("extrusion")
            }
        ]
    }

    function detailTitle() {
        if (root.detailPage === "advanced") {
            return "Advanced tuning"
        }
        if (root.detailPage === "exclude") {
            return "Object exclusion"
        }
        if (root.detailPage === "time") {
            return "Time details"
        }
        if (root.detailPage === "motion") {
            return "Motion details"
        }
        if (root.detailPage === "extrusion") {
            return "Extrusion details"
        }
        return root.printFilename.length > 0 ? root.printFilename : "Job Status"
    }

    function detailInfoModel(page) {
        if (page === "time") {
            return [
                {"label": "Elapsed", "value": root.durationLabel(root.printDuration)},
                {"label": "Remaining", "value": root.remainingLabel()},
                {"label": "Estimated total", "value": root.durationLabel(root.totalDuration)},
                {"label": "Slicer estimate", "value": root.fileEstimatedTimeLabel()},
                {"label": "File estimate", "value": "-"},
                {"label": "Filament estimate", "value": "-"},
                {"label": "File size", "value": root.fileModel ? root.fileModel.fileSizeLabelFor(root.printFilename) : "-"},
                {"label": "Modified", "value": root.fileModel ? root.fileModel.fileModifiedLabelFor(root.printFilename) : "-"},
                {"label": "Path", "value": root.fileModel ? root.fileModel.filePathFor(root.printFilename) : ""}
            ]
        }
        if (page === "motion") {
            return [
                {"label": "Requested speed", "value": root.speedLabel(root.requestedSpeed)},
                {"label": "Speed factor", "value": root.percentLabel(root.speedFactor)},
                {"label": "Max acceleration", "value": root.accelLabel()},
                {"label": "Max velocity", "value": root.speedLabel(root.maxVelocity)},
                {"label": "X position", "value": root.positionX.toFixed(2) + " mm"},
                {"label": "Y position", "value": root.positionY.toFixed(2) + " mm"},
                {"label": "Z position", "value": root.positionZ.toFixed(2) + " mm"},
                {"label": "Homed axes", "value": root.homedAxes.length > 0 ? root.homedAxes : "-"},
                {"label": "Z offset", "value": root.zOffsetLabel()},
                {"label": "Layer", "value": root.layerLabel()},
                {"label": "Object height", "value": root.fileObjectHeightLabel()},
                {"label": "Layer height", "value": root.fileLayerHeightLabel()}
            ]
        }
        if (page === "extrusion") {
            return [
                {"label": "Filament used", "value": root.filamentLabel()},
                {"label": "Filament total", "value": root.fileFilamentTotalLabel()},
                {"label": "Flow factor", "value": root.percentLabel(root.extrudeFactor)},
                {"label": "Extruder position", "value": root.positionE.toFixed(2) + " mm"},
                {"label": "Layer", "value": root.layerLabel()}
            ]
        }
        return []
    }

    // qmllint disable missing-property
    function goBack() {
        if (root.pendingJobAction.length > 0) {
            root.clearJobAction()
            return true
        }
        if (root.detailPage !== "summary") {
            root.detailPage = "summary"
            return true
        }
        return false
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        color: "#050909"
        border.color: "#31464a"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.45)
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0d1517" }
            GradientStop { position: 0.45; color: "#070b0c" }
            GradientStop { position: 1.0; color: "#030506" }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap

            RowLayout {
                Layout.fillWidth: true
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: root.detailTitle()
                    elide: Text.ElideMiddle
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Rectangle {
                    id: statusPill
                    visible: root.detailPage === "summary"
                    Layout.preferredWidth: Math.max(92, Math.round(root.metrics.fontSize * 6.2))
                    Layout.preferredHeight: Math.max(26, Math.round(root.metrics.fontSize * 1.75))
                    color: "#101617"
                    border.color: root.accentColor
                    border.width: 1
                    radius: height / 2

                    Label {
                        anchors.centerIn: parent
                        color: root.accentColor
                        text: root.stateHeadline()
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.bold: true
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.78))
                    }
                }
            }

            StatusCard {
                visible: root.detailPage === "summary"
                Layout.fillWidth: true
                Layout.preferredHeight: root.jobHeroHeight()
                accent: root.accentColor

                GridLayout {
                    id: jobHeroLayout
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: root.metrics.portrait ? 1 : 2
                    rows: root.metrics.portrait ? 2 : 1
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Rectangle {
                        id: thumbnailFrame
                        Layout.preferredWidth: root.metrics.portrait
                            ? Math.min(parent.width, Math.max(180, Math.round(root.metrics.fontSize * 13.6)))
                            : Math.max(126, Math.round(root.metrics.fontSize * 8.8))
                        Layout.preferredHeight: root.metrics.portrait
                            ? Math.max(78, Math.round(root.metrics.fontSize * 5.0))
                            : Math.max(96, Math.round(root.metrics.fontSize * 6.6))
                        Layout.fillHeight: !root.metrics.portrait
                        Layout.alignment: Qt.AlignHCenter
                        color: "#0b1112"
                        border.color: "#3b4648"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.34)
                        clip: true

                        Image {
                            id: jobThumbnail
                            anchors.fill: parent
                            anchors.margins: 4
                            source: root.fileModel && root.fileModel.thumbnailRevision >= 0
                                ? root.fileModel.filePreviewThumbnailUrlFor(root.printFilename)
                                : ""
                            fillMode: Image.PreserveAspectFit
                            visible: source.toString().length > 0
                        }

                        ColumnLayout {
                            id: thumbnailPlaceholder
                            visible: !jobThumbnail.visible
                            anchors.centerIn: parent
                            width: parent.width - root.metrics.gap * 2
                            spacing: 0

                            Label {
                                Layout.fillWidth: true
                                color: root.neutralAccent
                                text: "G"
                                horizontalAlignment: Text.AlignHCenter
                                font.bold: true
                                font.pixelSize: Math.max(28, Math.round(root.metrics.fontSize * 2.2))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: "G-code"
                                horizontalAlignment: Text.AlignHCenter
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.stateMessage()
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                        }

                        ProgressBar {
                            id: jobProgressBar
                            Layout.maximumWidth: Math.max(160, Math.round(root.metrics.fontSize * 12.5))
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.max(18, Math.round(root.metrics.fontSize * 1.15))
                            value: root.stateProgressValue()
                            background: Rectangle {
                                color: "#050809"
                                border.color: "#2c3b3e"
                                border.width: 1
                                radius: height / 2
                            }
                            contentItem: Item {
                                Rectangle {
                                    id: progressRail
                                    anchors.fill: parent
                                    anchors.margins: 2
                                    color: "#071112"
                                    radius: height / 2

                                    Rectangle {
                                        id: progressFill
                                        anchors.left: parent.left
                                        anchors.top: parent.top
                                        anchors.bottom: parent.bottom
                                        width: Math.max(height, jobProgressBar.visualPosition * parent.width)
                                        radius: height / 2
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: "#687477" }
                                            GradientStop { position: 1.0; color: root.accentColor }
                                        }
                                    }
                                }
                            }
                        }

                        RowLayout {
                            id: compactProgressBox
                            Layout.fillWidth: true
                            spacing: root.metrics.gap

                            Label {
                                color: Theme.text
                                text: Math.round(root.stateProgressValue() * 100) + "%"
                                font.bold: true
                                font.pixelSize: Math.max(24, Math.round(root.metrics.fontSize * 1.72))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: root.printState === "complete"
                                    ? "Done"
                                    : root.printState === "cancelled"
                                        ? "Stopped"
                                        : root.printState === "error"
                                            ? "Check printer"
                                            : root.remainingLabel() + " remaining"
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                            }
                        }

                        RowLayout {
                            visible: !root.metrics.portrait
                            Layout.fillWidth: true
                            spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))

                            Repeater {
                                model: [
                                    {"label": "Z", "value": root.zOffsetLabel()},
                                    {"label": "Speed", "value": root.percentLabel(root.speedFactor)},
                                    {"label": "Flow", "value": root.percentLabel(root.extrudeFactor)}
                                ]

                                MetricPill {
                                    Layout.fillWidth: true
                                    label: modelData.label
                                    value: modelData.value
                                    accent: "#263233"
                                }
                            }
                        }
                    }
                }
            }

            GridLayout {
                id: jobActionGrid
                visible: root.detailPage === "summary"
                Layout.preferredWidth: root.jobActionGridWidth()
                Layout.preferredHeight: root.jobActionGridHeight()
                Layout.alignment: Qt.AlignHCenter
                columns: root.metrics.portrait ? 2 : 4
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: root.primaryActionLabel()
                    iconText: "||"
                    buttonRole: "primary"
                    enabled: true
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                    onClicked: root.stageImmediateJobAction(root.effectivePrintState() === "paused" ? "resume" : "pause")
                }

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Cancel"
                    iconText: "X"
                    buttonRole: "danger"
                    accent: root.mutedDangerAccent
                    enabled: true
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                    onClicked: root.requestJobAction("cancel", "")
                }

                JobButton {
                    visible: root.terminalJobState()
                    Layout.preferredWidth: root.clearActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Clear Status"
                    iconText: ""
                    buttonRole: "primary"
                    enabled: true
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                    onClicked: root.stageImmediateJobAction("clear")
                }

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Skip Object"
                    iconText: "OBJ"
                    enabled: root.excludeObjectNames.length > 0
                    ToolTip.visible: hovered
                    ToolTip.text: enabled ? "Open object exclusion list" : "No object data"
                    onClicked: root.detailPage = "exclude"
                }

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Advanced"
                    iconText: "ADV"
                    onClicked: root.detailPage = "advanced"
                }
            }

            JobActionPreview {
                id: jobActionPreview
                visible: root.detailPage === "summary" && root.pendingJobAction.length > 0
            }

            Rectangle {
                id: jobControlFeedback
                visible: root.controlFeedbackText().length > 0
                Layout.fillWidth: true
                Layout.preferredHeight: visible ? Math.max(34, Math.round(root.metrics.fontSize * 2.35)) : 0
                Layout.fillHeight: false
                color: root.controlError.length > 0 ? "#181311" : "#111819"
                border.color: root.controlError.length > 0 ? "#4a3430" : "#354346"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.28)

                Label {
                    anchors.fill: parent
                    anchors.leftMargin: root.metrics.gap
                    anchors.rightMargin: root.metrics.gap
                    color: Theme.text
                    text: root.controlFeedbackText()
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                }
            }

            Rectangle {
                visible: root.detailPage === "summary"
                    && root.metrics.portrait && root.height > 760
                    && root.temperatureModel
                    && root.temperatureModel.rowCount() > 0
                Layout.fillWidth: true
                Layout.preferredHeight: root.temperatureStripHeight()
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#10191b" }
                    GradientStop { position: 1.0; color: "#081112" }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        color: Theme.mutedText
                        text: "Temperatures"
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        orientation: ListView.Horizontal
                        clip: true
                        spacing: root.metrics.gap
                        model: root.temperatureModel

                        delegate: Rectangle {
                            required property string displayName
                            required property var temperature
                            required property var target

                            width: Math.max(150, Math.round(root.metrics.fontSize * 10.8))
                            height: parent ? parent.height : Math.max(34, root.metrics.fontSize * 2.3)
                            color: "#0b1112"
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.25)

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: Math.max(5, Math.round(root.metrics.fontSize * 0.35))
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: displayName
                                    elide: Text.ElideRight
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.text
                                    text: (typeof temperature === "undefined" || temperature === null
                                        ? "--"
                                        : Math.round(temperature) + "°")
                                        + " / "
                                        + (typeof target === "undefined" || target === null
                                            ? "--"
                                            : Math.round(target) + "°")
                                    elide: Text.ElideRight
                                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.92))
                                }
                            }
                        }
                    }
                }
            }

            GridLayout {
                id: summaryZoneGrid
                visible: root.detailPage === "summary"
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 1 : 3
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                SummaryZone {
                    id: timeSummaryZone
                    property var zoneData: root.groupedSummaryModel()[0]
                    title: zoneData.title
                    primaryLabel: zoneData.primaryLabel
                    primaryValue: zoneData.primaryValue
                    rows: zoneData.rows
                    onActivated: root.detailPage = "time"
                }

                SummaryZone {
                    id: motionSummaryZone
                    property var zoneData: root.groupedSummaryModel()[1]
                    title: zoneData.title
                    primaryLabel: zoneData.primaryLabel
                    primaryValue: zoneData.primaryValue
                    rows: zoneData.rows
                    onActivated: root.detailPage = "motion"
                }

                SummaryZone {
                    id: materialSummaryZone
                    property var zoneData: root.groupedSummaryModel()[2]
                    title: zoneData.title
                    primaryLabel: zoneData.primaryLabel
                    primaryValue: zoneData.primaryValue
                    rows: zoneData.rows
                    onActivated: root.detailPage = "extrusion"
                }
            }

            ColumnLayout {
                id: detailInfoPage
                visible: root.detailPage === "time"
                    || root.detailPage === "motion"
                    || root.detailPage === "extrusion"
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Flickable {
                    id: detailInfoFlickable
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    contentWidth: width
                    contentHeight: detailInfoGrid.implicitHeight

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    GridLayout {
                        id: detailInfoGrid
                        width: detailInfoFlickable.width
                        columns: root.metrics.portrait ? 1 : 2
                        rowSpacing: root.metrics.gap
                        columnSpacing: root.metrics.gap

                        Repeater {
                            model: root.detailInfoModel(root.detailPage)

                            delegate: Rectangle {
                                required property var modelData

                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.5))
                                color: "#101617"
                                border.color: "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.32)
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: "#111a1c" }
                                    GradientStop { position: 1.0; color: "#081112" }
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: root.metrics.gap
                                    spacing: 0

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.mutedText
                                        text: modelData.label
                                        elide: Text.ElideRight
                                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        color: Theme.text
                                        text: modelData.value
                                        verticalAlignment: Text.AlignVCenter
                                        elide: Text.ElideRight
                                        font.bold: true
                                        font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
                                    }
                                }
                            }
                        }
                    }
                }
            }

            ColumnLayout {
                id: advancedPage
                visible: root.detailPage === "advanced"
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Repeater {
                    id: advancedControlRepeater
                    Layout.minimumHeight: 0
                    Layout.preferredHeight: 0
                    Layout.maximumHeight: 0
                    model: [
                        {
                            "label": "Z offset",
                            "value": root.zOffsetLabel(),
                            "minus": "-0.05",
                            "plus": "+0.05",
                            "negativeDelta": -0.05,
                            "positiveDelta": 0.05,
                            "target": "z"
                        },
                        {
                            "label": "Speed factor",
                            "value": root.percentLabel(root.speedFactor),
                            "minus": "-5%",
                            "plus": "+5%",
                            "negativeDelta": -5,
                            "positiveDelta": 5,
                            "target": "speed"
                        },
                        {
                            "label": "Extrude factor",
                            "value": root.percentLabel(root.extrudeFactor),
                            "minus": "-5%",
                            "plus": "+5%",
                            "negativeDelta": -5,
                            "positiveDelta": 5,
                            "target": "extrude"
                        }
                    ]

                    Rectangle {
                        id: adjustmentCard
                        property string adjustmentTarget: modelData.target

                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(root.jobButtonHeight + root.metrics.gap * 2, Math.round(root.metrics.fontSize * 3.8))
                        color: "#101617"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#101a1d" }
                            GradientStop { position: 1.0; color: "#071011" }
                        }

                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: 3
                            color: root.accentColor
                            opacity: 0.7
                            radius: parent.radius
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: root.metrics.gap
                            spacing: root.metrics.gap

                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: modelData.label
                                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: Theme.text
                                    text: modelData.value
                                    verticalAlignment: Text.AlignVCenter
                                    font.bold: true
                                    font.pixelSize: Math.max(20, Math.round(root.metrics.fontSize * 1.45))
                                }
                            }

                            Repeater {
                                model: [
                                    {"text": modelData.minus, "delta": modelData.negativeDelta},
                                    {"text": modelData.plus, "delta": modelData.positiveDelta}
                                ]

                                JobButton {
                                    Layout.preferredWidth: root.jobButtonWidth
                                    Layout.preferredHeight: root.jobButtonHeight
                                    Layout.alignment: Qt.AlignVCenter
                                    text: modelData.text
                                    onClicked: {
                                        if (adjustmentCard.adjustmentTarget === "z") {
                                            root.zOffsetAdjustRequested(modelData.delta)
                                        } else if (adjustmentCard.adjustmentTarget === "speed") {
                                            root.speedFactorAdjustRequested(modelData.delta)
                                        } else if (adjustmentCard.adjustmentTarget === "extrude") {
                                            root.extrudeFactorAdjustRequested(modelData.delta)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Item {
                    id: advancedPageSpacer
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }

            }

            ColumnLayout {
                id: excludePage
                visible: root.detailPage === "exclude"
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.6))
                    color: "#101617"
                    border.color: root.currentObject.length > 0 ? root.neutralAccent : "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#101a1d" }
                        GradientStop { position: 1.0; color: "#071011" }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Current object"
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.currentObject.length > 0 ? root.currentObject : "-"
                            elide: Text.ElideMiddle
                            font.bold: true
                            font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.12))
                        }
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: root.metrics.gap
                    model: root.excludeObjectNames
                    boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: Math.max(58, Math.round(root.metrics.fontSize * 4.1))
                        color: root.excludedObjectNames.indexOf(modelData) >= 0
                            ? "#171717"
                            : "#101617"
                        border.color: modelData === root.currentObject ? root.neutralAccent : "#263233"
                        border.width: modelData === root.currentObject ? 2 : 1
                        radius: Math.round(root.metrics.fontSize * 0.32)
                        gradient: Gradient {
                            GradientStop {
                                position: 0.0
                                color: modelData === root.currentObject ? "#172023" : "#101a1d"
                            }
                            GradientStop { position: 1.0; color: "#071011" }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: root.metrics.gap
                            spacing: root.metrics.gap

                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.text
                                    text: String(modelData)
                                    elide: Text.ElideMiddle
                                    font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: root.excludedObjectNames.indexOf(modelData) >= 0
                                        ? "Excluded"
                                        : modelData === root.currentObject ? "Printing now" : "Available"
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }
                            }

                            JobButton {
                                Layout.preferredWidth: root.jobButtonWidth
                                Layout.preferredHeight: root.jobButtonHeight
                                Layout.alignment: Qt.AlignVCenter
                                text: "Skip"
                                enabled: root.excludedObjectNames.indexOf(modelData) < 0
                                onClicked: root.requestJobAction("skip", modelData)
                            }
                        }
                    }
                }

                JobActionPreview {
                    visible: root.pendingJobAction.length > 0
                }

            }
        }
    }
}
