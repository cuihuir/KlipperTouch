import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
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
    property real bedMinX: 0
    property real bedMinY: 0
    property real bedMaxX: 0
    property real bedMaxY: 0
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
    property var excludeObjects: []
    property var excludedObjectNames: []
    property string currentObject: ""
    property string detailPage: "summary"
    property string pendingJobAction: ""
    property string pendingJobObject: ""
    property string selectedExcludeObject: ""
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

    onExcludeObjectsChanged: root.requestObjectMapRepaint()
    onExcludedObjectNamesChanged: root.requestObjectMapRepaint()
    onCurrentObjectChanged: root.requestObjectMapRepaint()
    onSelectedExcludeObjectChanged: root.requestObjectMapRepaint()

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
                Layout.preferredWidth: Math.max(
                    14,
                    Math.round(root.metrics.fontSize * (metricRoot.label.length <= 1 ? 1.2 : 3.2))
                )
                color: Theme.mutedText
                text: metricRoot.label
                elide: Text.ElideRight
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

    component JobButton: TactileButton {
        id: controlRoot
        property color accent: root.neutralAccent
        property string buttonRole: "normal"
        readonly property color roleAccent: buttonRole === "danger"
            ? root.mutedDangerAccent
            : buttonRole === "primary" ? root.accentColor : accent
        implicitHeight: root.jobButtonHeight
        implicitWidth: root.jobButtonWidth
        fontSize: root.metrics.fontSize
        baseColor: "#263033"
        pressedColor: "#172528"
        disabledColor: "#151a1b"
        accentColor: controlRoot.roleAccent
        disabledAccentColor: "#263233"
        disabledOpacity: 0.72
        iconSize: Math.max(24, Math.round(root.metrics.fontSize * 1.55))
        depthSize: Math.max(3, Math.round(root.metrics.fontSize * 0.20))
        showLeadingAccent: true
        leadingAccentWidth: controlRoot.enabled ? 3 : 1
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
                    text: root.confirmationRequired() ? "Confirm action" : "Action sent"
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
                    iconName: "confirm"
                    enabled: true
                    onClicked: {
                        root.jobActionRequested(root.pendingJobAction, root.pendingJobObject)
                        root.clearJobAction()
                    }
                }

                JobButton {
                    Layout.fillWidth: root.metrics.portrait
                    text: "Dismiss"
                    iconName: "cancel"
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

    function timePrimaryLabel() {
        return root.terminalJobState() ? "Elapsed" : "Remaining"
    }

    function timePrimaryValue() {
        return root.terminalJobState()
            ? root.durationLabel(root.printDuration)
            : root.remainingLabel()
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

    function zOffsetCompactLabel() {
        return root.zOffset.toFixed(2)
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
        if (state === "starting") {
            return "Starting"
        }
        if (state === "pausing") {
            return "Pausing"
        }
        if (state === "paused") {
            return "Paused"
        }
        if (state === "resuming") {
            return "Resuming"
        }
        if (state === "cancelling") {
            return "Cancelling"
        }
        if (state === "clearing") {
            return "Clearing"
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
        if (state === "starting") {
            return "Starting " + (root.printFilename.length > 0 ? root.printFilename : "selected file")
        }
        if (state === "pausing") {
            return "Pause command sent. Waiting for printer state."
        }
        if (state === "paused") {
            return "Print paused. Print status remains visible."
        }
        if (state === "resuming") {
            return "Resume command sent. Waiting for printer state."
        }
        if (state === "cancelling") {
            return "Cancel command sent. Waiting for printer state."
        }
        if (state === "clearing") {
            return "Clear command sent. Waiting for standby state."
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
        if (root.isTransitionalState(state)) {
            return "#77888b"
        }
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

    function isTerminalState(state) {
        return state === "complete" || state === "cancelled" || state === "error"
    }

    function isTransitionalState(state) {
        return state === "starting"
            || state === "pausing"
            || state === "resuming"
            || state === "cancelling"
            || state === "clearing"
    }

    function stateFamily(state) {
        if (root.isTerminalState(state)) {
            return "terminal"
        }
        if (root.isTransitionalState(state)) {
            return "transitional"
        }
        if (state === "printing" || state === "paused") {
            return "active"
        }
        return "standby"
    }

    function stateProgressValue() {
        if (root.printState === "complete") {
            return 1
        }
        return Math.max(0, Math.min(1, root.printProgress / 100))
    }

    function primaryActionLabel() {
        var state = root.effectivePrintState()
        return state === "paused" || state === "resuming" ? "Resume" : "Pause"
    }

    function terminalJobState() {
        var state = root.effectivePrintState()
        return root.isTerminalState(state) || state === "clearing"
    }

    function effectivePrintState() {
        if (root.requestedPrintState === "printing" && root.printState === "standby") {
            return "starting"
        }
        if (root.requestedPrintState === "printing" && root.printState === "paused") {
            return "resuming"
        }
        if (root.requestedPrintState === "paused" && root.printState === "printing") {
            return "pausing"
        }
        if (root.requestedPrintState === "cancelled"
                && (root.printState === "printing" || root.printState === "paused")) {
            return "cancelling"
        }
        if (root.requestedPrintState === "standby" && root.isTerminalState(root.printState)) {
            return "clearing"
        }
        if (root.isTerminalState(root.printState) || root.printState === "paused") {
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
        return root.pendingJobAction === "cancel"
            || root.pendingJobAction === "skip"
            || root.pendingJobAction === "skip_current"
    }

    function pendingJobActionLabel() {
        if (root.pendingJobAction === "cancel") {
            return "Cancel " + (root.printFilename.length > 0 ? root.printFilename : "current print")
        }
        if (root.pendingJobAction === "skip_current") {
            return "Skip current object " + (root.currentObject.length > 0 ? root.currentObject : "-")
        }
        if (root.pendingJobAction === "skip") {
            return "Skip object " + (root.pendingJobObject.length > 0 ? root.pendingJobObject : "-")
        }
        return ""
    }

    function requestObjectMapRepaint() {
        if (typeof objectMapCanvas !== "undefined") {
            objectMapCanvas.requestPaint()
        }
    }

    function selectExcludeObject(objectName) {
        if (objectName.length > 0 && root.excludedObjectNames.indexOf(objectName) < 0) {
            root.selectedExcludeObject = objectName
        }
    }

    function selectedExcludeObjectName() {
        if (root.selectedExcludeObject.length > 0
                && root.excludedObjectNames.indexOf(root.selectedExcludeObject) < 0
                && root.excludeObjectNames.indexOf(root.selectedExcludeObject) >= 0) {
            return root.selectedExcludeObject
        }
        if (root.currentObject.length > 0
                && root.excludedObjectNames.indexOf(root.currentObject) < 0
                && root.excludeObjectNames.indexOf(root.currentObject) >= 0) {
            return root.currentObject
        }
        for (var i = 0; i < root.excludeObjectNames.length; i += 1) {
            if (root.excludedObjectNames.indexOf(root.excludeObjectNames[i]) < 0) {
                return root.excludeObjectNames[i]
            }
        }
        return ""
    }

    function activeExcludeObjectName() {
        return root.selectedExcludeObjectName()
    }

    function excludeObjectHasPolygon(objectInfo) {
        return objectInfo && objectInfo.polygon && objectInfo.polygon.length >= 3
    }

    function objectMapHasPolygons() {
        for (var i = 0; i < root.excludeObjects.length; i += 1) {
            if (root.excludeObjectHasPolygon(root.excludeObjects[i])) {
                return true
            }
        }
        return false
    }

    function objectMapBounds() {
        if (root.bedMaxX > root.bedMinX && root.bedMaxY > root.bedMinY) {
            return {
                "valid": true,
                "minX": root.bedMinX,
                "minY": root.bedMinY,
                "maxX": root.bedMaxX,
                "maxY": root.bedMaxY
            }
        }
        var minX = Number.POSITIVE_INFINITY
        var minY = Number.POSITIVE_INFINITY
        var maxX = Number.NEGATIVE_INFINITY
        var maxY = Number.NEGATIVE_INFINITY
        for (var i = 0; i < root.excludeObjects.length; i += 1) {
            var objectInfo = root.excludeObjects[i]
            if (!root.excludeObjectHasPolygon(objectInfo)) {
                continue
            }
            for (var j = 0; j < objectInfo.polygon.length; j += 1) {
                var point = objectInfo.polygon[j]
                minX = Math.min(minX, point[0])
                minY = Math.min(minY, point[1])
                maxX = Math.max(maxX, point[0])
                maxY = Math.max(maxY, point[1])
            }
        }
        if (!isFinite(minX) || !isFinite(minY) || maxX <= minX || maxY <= minY) {
            return {"valid": false, "minX": 0, "minY": 0, "maxX": 1, "maxY": 1}
        }
        return {"valid": true, "minX": minX, "minY": minY, "maxX": maxX, "maxY": maxY}
    }

    function objectMapPadding() {
        return Math.max(12, Math.round(root.metrics.fontSize * 0.85))
    }

    function objectMapMinObjectPixels(width, height) {
        var padding = root.objectMapPadding()
        var usableMin = Math.min(Math.max(1, width - padding * 2), Math.max(1, height - padding * 2))
        return Math.max(44, Math.min(76, Math.round(usableMin * 0.18)))
    }

    function objectMapXToCanvas(x, bounds, width) {
        var padding = root.objectMapPadding()
        return padding + ((x - bounds.minX) / Math.max(0.001, bounds.maxX - bounds.minX))
            * Math.max(1, width - padding * 2)
    }

    function objectMapYToCanvas(y, bounds, height) {
        var padding = root.objectMapPadding()
        return height - padding - ((y - bounds.minY) / Math.max(0.001, bounds.maxY - bounds.minY))
            * Math.max(1, height - padding * 2)
    }

    function objectMapCanvasToX(screenX, bounds, width) {
        var padding = root.objectMapPadding()
        return bounds.minX + ((screenX - padding) / Math.max(1, width - padding * 2))
            * Math.max(0.001, bounds.maxX - bounds.minX)
    }

    function objectMapCanvasToY(screenY, bounds, height) {
        var padding = root.objectMapPadding()
        return bounds.minY + ((height - padding - screenY) / Math.max(1, height - padding * 2))
            * Math.max(0.001, bounds.maxY - bounds.minY)
    }

    function objectMapDisplayPolygon(objectInfo, bounds, width, height) {
        if (!root.excludeObjectHasPolygon(objectInfo)) {
            return []
        }
        var padding = root.objectMapPadding()
        var usableLeft = padding
        var usableTop = padding
        var usableRight = Math.max(usableLeft + 1, width - padding)
        var usableBottom = Math.max(usableTop + 1, height - padding)
        var points = []
        var minX = Number.POSITIVE_INFINITY
        var minY = Number.POSITIVE_INFINITY
        var maxX = Number.NEGATIVE_INFINITY
        var maxY = Number.NEGATIVE_INFINITY
        for (var i = 0; i < objectInfo.polygon.length; i += 1) {
            var point = objectInfo.polygon[i]
            var canvasX = root.objectMapXToCanvas(point[0], bounds, width)
            var canvasY = root.objectMapYToCanvas(point[1], bounds, height)
            points.push({"x": canvasX, "y": canvasY})
            minX = Math.min(minX, canvasX)
            minY = Math.min(minY, canvasY)
            maxX = Math.max(maxX, canvasX)
            maxY = Math.max(maxY, canvasY)
        }

        var minSize = root.objectMapMinObjectPixels(width, height)
        var originalWidth = Math.max(1, maxX - minX)
        var originalHeight = Math.max(1, maxY - minY)
        var targetWidth = Math.min(usableRight - usableLeft, Math.max(originalWidth, minSize))
        var targetHeight = Math.min(usableBottom - usableTop, Math.max(originalHeight, minSize))
        var scaleX = targetWidth / originalWidth
        var scaleY = targetHeight / originalHeight
        var centerX = (minX + maxX) / 2
        var centerY = (minY + maxY) / 2
        var scaled = []
        var scaledMinX = Number.POSITIVE_INFINITY
        var scaledMinY = Number.POSITIVE_INFINITY
        var scaledMaxX = Number.NEGATIVE_INFINITY
        var scaledMaxY = Number.NEGATIVE_INFINITY
        for (var j = 0; j < points.length; j += 1) {
            var scaledX = centerX + (points[j].x - centerX) * scaleX
            var scaledY = centerY + (points[j].y - centerY) * scaleY
            scaled.push({"x": scaledX, "y": scaledY})
            scaledMinX = Math.min(scaledMinX, scaledX)
            scaledMinY = Math.min(scaledMinY, scaledY)
            scaledMaxX = Math.max(scaledMaxX, scaledX)
            scaledMaxY = Math.max(scaledMaxY, scaledY)
        }

        var shiftX = 0
        var shiftY = 0
        if (scaledMinX < usableLeft) {
            shiftX = usableLeft - scaledMinX
        }
        if (scaledMaxX + shiftX > usableRight) {
            shiftX = usableRight - scaledMaxX
        }
        if (scaledMinY < usableTop) {
            shiftY = usableTop - scaledMinY
        }
        if (scaledMaxY + shiftY > usableBottom) {
            shiftY = usableBottom - scaledMaxY
        }

        var display = []
        for (var k = 0; k < scaled.length; k += 1) {
            var scaledX = scaled[k].x + shiftX
            var scaledY = scaled[k].y + shiftY
            display.push({
                "x": Math.min(usableRight, Math.max(usableLeft, scaledX)),
                "y": Math.min(usableBottom, Math.max(usableTop, scaledY))
            })
        }
        return display
    }

    function objectAtPoint(screenX, screenY) {
        var bounds = root.objectMapBounds()
        if (!bounds.valid) {
            return ""
        }
        for (var i = root.excludeObjects.length - 1; i >= 0; i -= 1) {
            var objectInfo = root.excludeObjects[i]
            if (!root.excludeObjectHasPolygon(objectInfo)
                    || root.excludedObjectNames.indexOf(objectInfo.name) >= 0) {
                continue
            }
            var displayPolygon = root.objectMapDisplayPolygon(objectInfo, bounds, objectMapCanvas.width, objectMapCanvas.height)
            var minX = Number.POSITIVE_INFINITY
            var minY = Number.POSITIVE_INFINITY
            var maxX = Number.NEGATIVE_INFINITY
            var maxY = Number.NEGATIVE_INFINITY
            for (var j = 0; j < displayPolygon.length; j += 1) {
                var point = displayPolygon[j]
                minX = Math.min(minX, point.x)
                minY = Math.min(minY, point.y)
                maxX = Math.max(maxX, point.x)
                maxY = Math.max(maxY, point.y)
            }
            if (screenX >= minX && screenX <= maxX && screenY >= minY && screenY <= maxY) {
                return objectInfo.name
            }
        }
        return ""
    }

    function objectMapFillColor(excluded, current, selected) {
        if (excluded) {
            return "#202020"
        }
        if (selected) {
            return "#344246"
        }
        if (current) {
            return "#162a33"
        }
        return "#141f21"
    }

    function objectMapStrokeColor(current, selected) {
        return selected ? "#e0e6e8" : current ? "#f0b24b" : "#4b5659"
    }

    function drawCurrentObjectMarker(ctx, objectInfo, bounds) {
        if (!root.excludeObjectHasPolygon(objectInfo)) {
            return
        }
        ctx.save()
        ctx.setLineDash([])
        ctx.strokeStyle = "#f0b24b"
        ctx.lineWidth = 4
        ctx.beginPath()
        var displayPolygon = root.objectMapDisplayPolygon(objectInfo, bounds, objectMapCanvas.width, objectMapCanvas.height)
        for (var j = 0; j < displayPolygon.length; j += 1) {
            var point = displayPolygon[j]
            if (j === 0) {
                ctx.moveTo(point.x, point.y)
            } else {
                ctx.lineTo(point.x, point.y)
            }
        }
        ctx.closePath()
        ctx.stroke()
        ctx.restore()
    }

    function drawExcludeObjectMap(ctx) {
        var bounds = root.objectMapBounds()
        ctx.clearRect(0, 0, objectMapCanvas.width, objectMapCanvas.height)
        if (!bounds.valid) {
            return
        }
        var padding = root.objectMapPadding()
        ctx.strokeStyle = "#344044"
        ctx.lineWidth = 1
        ctx.strokeRect(padding, padding, objectMapCanvas.width - padding * 2, objectMapCanvas.height - padding * 2)
        ctx.setLineDash([2, 4])
        ctx.strokeStyle = "#263233"
        ctx.beginPath()
        ctx.moveTo(objectMapCanvas.width / 2, padding)
        ctx.lineTo(objectMapCanvas.width / 2, objectMapCanvas.height - padding)
        ctx.moveTo(padding, objectMapCanvas.height / 2)
        ctx.lineTo(objectMapCanvas.width - padding, objectMapCanvas.height / 2)
        ctx.stroke()
        ctx.setLineDash([])

        for (var i = 0; i < root.excludeObjects.length; i += 1) {
            var objectInfo = root.excludeObjects[i]
            if (!root.excludeObjectHasPolygon(objectInfo)) {
                continue
            }
            var excluded = root.excludedObjectNames.indexOf(objectInfo.name) >= 0
            var current = objectInfo.name === root.currentObject
            var selected = objectInfo.name === root.activeExcludeObjectName()
            var displayPolygon = root.objectMapDisplayPolygon(objectInfo, bounds, objectMapCanvas.width, objectMapCanvas.height)
            ctx.beginPath()
            for (var j = 0; j < displayPolygon.length; j += 1) {
                var point = displayPolygon[j]
                if (j === 0) {
                    ctx.moveTo(point.x, point.y)
                } else {
                    ctx.lineTo(point.x, point.y)
                }
            }
            ctx.closePath()
            ctx.fillStyle = root.objectMapFillColor(excluded, current, selected)
            ctx.strokeStyle = root.objectMapStrokeColor(current, selected)
            ctx.lineWidth = selected ? 3 : current ? 2 : 1
            ctx.fill()
            ctx.stroke()
            if (current) {
                root.drawCurrentObjectMarker(ctx, objectInfo, bounds)
            }
        }
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
            return root.compactHeroLayout()
                ? Math.max(132, Math.round(root.metrics.fontSize * 8.1))
                : Math.max(168, Math.round(root.metrics.fontSize * 10.2))
        }
        return Math.max(146, Math.round(root.metrics.fontSize * 9.2))
    }

    function compactHeroLayout() {
        return !root.metrics.portrait || root.width >= 420
    }

    function advancedCardHeight() {
        return root.metrics.portrait
            ? Math.max(88, Math.round(root.metrics.fontSize * 5.6))
            : Math.max(70, Math.round(root.metrics.fontSize * 4.3))
    }

    function temperatureStripHeight() {
        return Math.max(
            root.metrics.portrait ? 60 : 50,
            Math.round(root.metrics.fontSize * (root.metrics.portrait ? 3.8 : 3.1))
        )
    }

    function summaryTemperatureStripVisible() {
        if (root.detailPage !== "summary"
                || root.pendingJobAction.length > 0
                || !root.temperatureModel
                || root.temperatureModel.rowCount() <= 0
                || root.metrics.ultraWide) {
            return false
        }
        return !root.metrics.portrait
    }

    function summaryBottomSafeArea() {
        return root.metrics.portrait
            ? Math.max(root.metrics.gap * 2, Math.round(root.metrics.fontSize * 2.0))
            : root.metrics.gap
    }

    function summaryZoneGridHeight() {
        var zoneHeight = Math.max(78, Math.round(root.metrics.fontSize * 4.9))
        if (root.metrics.portrait) {
            return zoneHeight * 3 + root.metrics.gap * 2
        }
        return Math.max(96, Math.round(root.metrics.fontSize * 5.8))
    }

    function ultraWideThumbnailSize() {
        return Math.max(250, Math.min(340, Math.round(root.height - root.metrics.margin * 2 - root.metrics.gap * 8)))
    }

    function ultraWideActionButtonHeight() {
        return Math.max(98, Math.min(132, Math.round((root.height - root.metrics.margin * 2 - root.metrics.gap * 8) / 2.7)))
    }

    function drawUltraWideProgressDial(ctx) {
        var size = Math.min(ultraWideProgressCanvas.width, ultraWideProgressCanvas.height)
        ctx.clearRect(0, 0, ultraWideProgressCanvas.width, ultraWideProgressCanvas.height)
        if (size <= 0) {
            return
        }
        var center = size / 2
        var radius = Math.max(1, center - Math.max(12, Math.round(root.metrics.fontSize * 1.0)))
        var lineWidth = Math.max(12, Math.round(root.metrics.fontSize * 0.9))
        ctx.save()
        ctx.translate((ultraWideProgressCanvas.width - size) / 2, (ultraWideProgressCanvas.height - size) / 2)
        ctx.lineCap = "round"
        ctx.lineWidth = lineWidth
        ctx.strokeStyle = "#172426"
        ctx.beginPath()
        ctx.arc(center, center, radius, 0, Math.PI * 2)
        ctx.stroke()
        ctx.strokeStyle = root.accentColor
        ctx.beginPath()
        ctx.arc(center, center, radius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * root.stateProgressValue())
        ctx.stroke()
        ctx.restore()
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
                "primaryLabel": root.timePrimaryLabel(),
                "primaryValue": root.timePrimaryValue(),
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
                visible: !(root.detailPage === "summary" && root.metrics.ultraWide)
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

            GridLayout {
                id: ultraWideSummaryGrid
                visible: root.detailPage === "summary" && root.metrics.ultraWide
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: 4
                rows: 1
                columnSpacing: root.metrics.gap
                rowSpacing: root.metrics.gap

                Rectangle {
                    id: ultraWideThumbnailCard
                    Layout.preferredWidth: root.ultraWideThumbnailSize() + root.metrics.gap * 2
                    Layout.fillHeight: true
                    color: "#081112"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)
                    clip: true

                    Rectangle {
                        id: ultraWideThumbnailFrame
                        width: root.ultraWideThumbnailSize()
                        height: width
                        anchors.centerIn: parent
                        color: "#0b1112"
                        border.color: "#3b4648"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.34)
                        clip: true

                        Image {
                            id: ultraWideJobThumbnail
                            anchors.fill: parent
                            anchors.margins: 4
                            source: root.fileModel && root.fileModel.thumbnailRevision >= 0
                                ? root.fileModel.filePreviewThumbnailUrlFor(root.printFilename)
                                : ""
                            fillMode: Image.PreserveAspectFit
                            asynchronous: source.toString().indexOf("file:") !== 0
                            cache: true
                            sourceSize.width: width
                            sourceSize.height: height
                            visible: source.toString().length > 0
                                && ultraWideJobThumbnail.status === Image.Ready
                        }

                        ColumnLayout {
                            id: ultraWideThumbnailPlaceholder
                            visible: !ultraWideJobThumbnail.visible
                            anchors.centerIn: parent
                            width: parent.width - root.metrics.gap * 2
                            spacing: 0

                            Label {
                                Layout.fillWidth: true
                                color: root.neutralAccent
                                text: "G"
                                horizontalAlignment: Text.AlignHCenter
                                font.bold: true
                                font.pixelSize: Math.max(34, Math.round(root.metrics.fontSize * 2.6))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: "G-code"
                                horizontalAlignment: Text.AlignHCenter
                                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.78))
                            }
                        }
                    }
                }

                Rectangle {
                    id: ultraWideProgressDialCard
                    Layout.preferredWidth: root.ultraWideThumbnailSize() + root.metrics.gap * 2
                    Layout.fillHeight: true
                    color: "#081112"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)
                    clip: true

                    Canvas {
                        id: ultraWideProgressCanvas
                        width: root.ultraWideThumbnailSize()
                        height: width
                        anchors.centerIn: parent
                        antialiasing: true
                        renderStrategy: Canvas.Threaded
                        onPaint: root.drawUltraWideProgressDial(getContext("2d"))
                        onWidthChanged: requestPaint()
                        onHeightChanged: requestPaint()
                        Component.onCompleted: requestPaint()
                    }

                    ColumnLayout {
                        anchors.centerIn: parent
                        width: Math.max(120, Math.round(root.ultraWideThumbnailSize() * 0.62))
                        spacing: Math.max(2, Math.round(root.metrics.fontSize * 0.16))

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: Math.round(root.stateProgressValue() * 100) + "%"
                            horizontalAlignment: Text.AlignHCenter
                            font.bold: true
                            font.pixelSize: Math.max(44, Math.round(root.metrics.fontSize * 3.2))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.timePrimaryLabel()
                            horizontalAlignment: Text.AlignHCenter
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.86))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.timePrimaryValue()
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(24, Math.round(root.metrics.fontSize * 1.6))
                        }
                    }
                }

                StatusCard {
                    id: ultraWideInfoCard
                    Layout.preferredWidth: Math.max(560, Math.round(root.width * 0.34))
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    accent: "#354346"

                    RowLayout {
                        id: ultraWideFileHeader
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.printFilename.length > 0 ? root.printFilename : "No active file"
                            elide: Text.ElideMiddle
                            font.bold: true
                            font.pixelSize: Math.max(22, Math.round(root.metrics.fontSize * 1.48))
                        }

                        Rectangle {
                            id: ultraWideStatusPill
                            Layout.preferredWidth: Math.max(92, Math.round(root.metrics.fontSize * 6.2))
                            Layout.preferredHeight: Math.max(28, Math.round(root.metrics.fontSize * 1.85))
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

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: root.stateMessage()
                        elide: Text.ElideRight
                        font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.94))
                    }

                    GridLayout {
                        id: ultraWideKeyInfoGrid
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 3
                        rowSpacing: root.metrics.gap
                        columnSpacing: root.metrics.gap

                        Repeater {
                            model: [
                                {"label": "Elapsed", "value": root.durationLabel(root.printDuration)},
                                {"label": "Total", "value": root.durationLabel(root.totalDuration)},
                                {"label": "Remain", "value": root.remainingLabel()},
                                {"label": "Layer", "value": root.layerLabel()},
                                {"label": "Used", "value": root.filamentLabel()},
                                {"label": "Total", "value": root.fileFilamentTotalLabel()},
                                {"label": "Z", "value": root.zOffsetCompactLabel()},
                                {"label": "Speed", "value": root.percentLabel(root.speedFactor)},
                                {"label": "Flow", "value": root.percentLabel(root.extrudeFactor)}
                            ]

                            MetricPill {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                label: modelData.label
                                value: modelData.value
                                accent: "#263233"
                            }
                        }
                    }
                }

                Rectangle {
                    id: ultraWideActionPanel
                    Layout.preferredWidth: Math.max(360, Math.round(root.width * 0.22))
                    Layout.fillHeight: true
                    color: "#081112"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: root.metrics.gap

                        GridLayout {
                            id: ultraWideActionGrid
                            Layout.fillWidth: true
                            Layout.fillHeight: root.pendingJobAction.length <= 0
                            columns: 2
                            rows: 2
                            rowSpacing: root.metrics.gap
                            columnSpacing: root.metrics.gap

                            JobButton {
                                visible: !root.terminalJobState()
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.ultraWideActionButtonHeight()
                                text: root.primaryActionLabel()
                                iconName: root.effectivePrintState() === "paused" ? "resume" : "pause"
                                buttonRole: "primary"
                                enabled: !root.isTransitionalState(root.effectivePrintState())
                                ToolTip.visible: hovered
                                ToolTip.text: root.readonlyActionHint(text)
                                onClicked: root.stageImmediateJobAction(root.effectivePrintState() === "paused" ? "resume" : "pause")
                            }

                            JobButton {
                                visible: !root.terminalJobState()
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.ultraWideActionButtonHeight()
                                text: "Skip Object"
                                iconName: "object"
                                enabled: root.excludeObjectNames.length > 0
                                    && !root.isTransitionalState(root.effectivePrintState())
                                ToolTip.visible: hovered
                                ToolTip.text: enabled ? "Open object exclusion list" : "No object data"
                                onClicked: root.detailPage = "exclude"
                            }

                            JobButton {
                                visible: !root.terminalJobState()
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.ultraWideActionButtonHeight()
                                text: "Cancel"
                                iconName: "cancel"
                                buttonRole: "danger"
                                accent: root.mutedDangerAccent
                                enabled: !root.isTransitionalState(root.effectivePrintState())
                                ToolTip.visible: hovered
                                ToolTip.text: root.readonlyActionHint(text)
                                onClicked: root.requestJobAction("cancel", "")
                            }

                            JobButton {
                                visible: !root.terminalJobState()
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.ultraWideActionButtonHeight()
                                text: "Advanced"
                                iconName: "advanced"
                                enabled: !root.isTransitionalState(root.effectivePrintState())
                                onClicked: root.detailPage = "advanced"
                            }

                            JobButton {
                                visible: root.terminalJobState()
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.columnSpan: 2
                                Layout.rowSpan: 2
                                text: "Clear Status"
                                iconName: "clear"
                                buttonRole: "primary"
                                enabled: !root.isTransitionalState(root.effectivePrintState())
                                ToolTip.visible: hovered
                                ToolTip.text: root.readonlyActionHint(text)
                                onClicked: root.stageImmediateJobAction("clear")
                            }
                        }

                        JobActionPreview {
                            id: ultraWideJobActionPreview
                            visible: root.detailPage === "summary"
                                && root.metrics.ultraWide
                                && root.pendingJobAction.length > 0
                        }
                    }
                }
            }

            Flickable {
                id: summaryFlickable
                visible: root.detailPage === "summary" && !root.metrics.ultraWide
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                contentWidth: width
                contentHeight: summaryContent.implicitHeight + root.summaryBottomSafeArea()

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                ColumnLayout {
                    id: summaryContent
                    width: summaryFlickable.width
                    spacing: root.metrics.gap

                    StatusCard {
                        visible: root.detailPage === "summary"
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.jobHeroHeight()
                        accent: root.accentColor

                        GridLayout {
                            id: jobHeroLayout
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: root.compactHeroLayout() ? 2 : 1
                            rows: root.compactHeroLayout() ? 1 : 2
                            rowSpacing: root.metrics.gap
                            columnSpacing: root.metrics.gap

                            Rectangle {
                                id: thumbnailFrame
                                Layout.preferredWidth: root.metrics.portrait
                                    ? root.compactHeroLayout()
                                        ? Math.max(96, Math.round(root.metrics.fontSize * 6.6))
                                        : Math.min(parent.width, Math.max(180, Math.round(root.metrics.fontSize * 13.6)))
                                    : Math.max(126, Math.round(root.metrics.fontSize * 8.8))
                                Layout.preferredHeight: root.metrics.portrait
                                    ? root.compactHeroLayout()
                                        ? Math.max(96, Math.round(root.metrics.fontSize * 6.6))
                                        : Math.max(72, Math.round(root.metrics.fontSize * 4.2))
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
                                    asynchronous: source.toString().indexOf("file:") !== 0
                                    cache: true
                                    sourceSize.width: width
                                    sourceSize.height: height
                                    visible: source.toString().length > 0
                                        && jobThumbnail.status === Image.Ready
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
                                    id: portraitMetricStrip
                                    visible: root.metrics.portrait
                                    Layout.fillWidth: true
                                    spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.28))

                                    Repeater {
                                        model: [
                                            {"label": "Z", "value": root.zOffsetCompactLabel()},
                                            {"label": "S", "value": root.percentLabel(root.speedFactor)},
                                            {"label": "F", "value": root.percentLabel(root.extrudeFactor)}
                                        ]

                                        MetricPill {
                                            Layout.fillWidth: true
                                            label: modelData.label
                                            value: modelData.value
                                            accent: "#263233"
                                        }
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
                        Layout.alignment: root.terminalJobState() ? Qt.AlignRight : Qt.AlignHCenter
                        columns: root.metrics.portrait ? 2 : 4
                        rowSpacing: root.metrics.gap
                        columnSpacing: root.metrics.gap

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: root.primaryActionLabel()
                    iconName: root.effectivePrintState() === "paused" ? "resume" : "pause"
                    buttonRole: "primary"
                    enabled: !root.isTransitionalState(root.effectivePrintState())
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                    onClicked: root.stageImmediateJobAction(root.effectivePrintState() === "paused" ? "resume" : "pause")
                }

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Cancel"
                    iconName: "cancel"
                    buttonRole: "danger"
                    accent: root.mutedDangerAccent
                    enabled: !root.isTransitionalState(root.effectivePrintState())
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                    onClicked: root.requestJobAction("cancel", "")
                }

                JobButton {
                    visible: root.terminalJobState()
                    Layout.preferredWidth: root.clearActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Clear Status"
                    iconName: "clear"
                    buttonRole: "primary"
                    enabled: !root.isTransitionalState(root.effectivePrintState())
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                    onClicked: root.stageImmediateJobAction("clear")
                }

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Skip Object"
                    iconName: "object"
                    enabled: root.excludeObjectNames.length > 0
                        && !root.isTransitionalState(root.effectivePrintState())
                    ToolTip.visible: hovered
                    ToolTip.text: enabled ? "Open object exclusion list" : "No object data"
                    onClicked: root.detailPage = "exclude"
                }

                JobButton {
                    visible: !root.terminalJobState()
                    Layout.preferredWidth: root.jobActionButtonWidth()
                    Layout.preferredHeight: root.jobButtonHeight
                    text: "Advanced"
                    iconName: "advanced"
                    enabled: !root.isTransitionalState(root.effectivePrintState())
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
                id: summaryTemperatureStrip
                visible: root.summaryTemperatureStripVisible()
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
                Layout.fillHeight: false
                Layout.preferredHeight: root.summaryZoneGridHeight()
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

                    Item {
                        id: summaryBottomSafeAreaItem
                        Layout.fillWidth: true
                        Layout.preferredHeight: root.summaryBottomSafeArea()
                    }
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

                GridLayout {
                    id: advancedControlGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: false
                    columns: 1
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        id: advancedControlRepeater
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
                            Layout.preferredHeight: root.advancedCardHeight()
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
                                        iconName: modelData.delta < 0 ? "back" : "confirm"
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
                }

                Item {
                    id: advancedPageSpacer
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }

            }

            GridLayout {
                id: excludePage
                visible: root.detailPage === "exclude"
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.ultraWide ? 2 : 1
                rows: root.metrics.ultraWide ? 1 : 2
                columnSpacing: root.metrics.gap
                rowSpacing: root.metrics.gap
                flow: GridLayout.LeftToRight

                Item {
                    id: excludePageLayout
                    visible: false
                }

                Rectangle {
                    id: objectMapFrame
                    visible: root.objectMapHasPolygons()
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: root.metrics.ultraWide
                        ? Math.max(720, Math.round(root.width * 0.72))
                        : -1
                    Layout.preferredHeight: root.metrics.portrait
                        ? Math.max(320, Math.round(root.metrics.fontSize * 20.0))
                        : Math.max(260, Math.round(root.metrics.fontSize * 16.0))
                    color: "#081112"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)
                    clip: true

                    Canvas {
                        id: objectMapCanvas
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        antialiasing: true
                        renderStrategy: Canvas.Threaded
                        onPaint: root.drawExcludeObjectMap(getContext("2d"))
                        onWidthChanged: requestPaint()
                        onHeightChanged: requestPaint()
                        Component.onCompleted: requestPaint()
                    }

                    MouseArea {
                        anchors.fill: objectMapCanvas
                        enabled: root.objectMapHasPolygons()
                        onClicked: {
                            var objectName = root.objectAtPoint(mouse.x, mouse.y)
                            if (objectName.length > 0) {
                                root.selectExcludeObject(objectName)
                            }
                        }
                    }
                }

                Rectangle {
                    id: excludeControlPanel
                    Layout.fillWidth: true
                    Layout.fillHeight: root.metrics.ultraWide
                    Layout.preferredWidth: root.metrics.ultraWide
                        ? Math.max(220, Math.round(root.width * 0.22))
                        : -1
                    Layout.preferredHeight: root.metrics.portrait
                        ? Math.max(104, Math.round(root.metrics.fontSize * 7.1))
                        : root.metrics.ultraWide
                            ? -1
                            : Math.max(96, Math.round(root.metrics.fontSize * 6.2))
                    color: "#101617"
                    border.color: root.activeExcludeObjectName().length > 0 ? root.neutralAccent : "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#101a1d" }
                        GradientStop { position: 1.0; color: "#071011" }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.max(26, Math.round(root.metrics.fontSize * 1.8))
                            color: Theme.text
                            text: root.activeExcludeObjectName().length > 0
                                ? root.activeExcludeObjectName()
                                : "Select an object"
                            elide: Text.ElideMiddle
                            verticalAlignment: Text.AlignVCenter
                            font.bold: true
                            font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.12))
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: root.metrics.gap
                            visible: !root.metrics.ultraWide

                            JobButton {
                                id: selectedObjectSkipButton
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.jobButtonHeight
                                Layout.alignment: Qt.AlignVCenter
                                text: "Skip Selected"
                                iconName: "object"
                                enabled: root.activeExcludeObjectName().length > 0
                                onClicked: root.requestJobAction("skip", root.activeExcludeObjectName())
                            }

                            JobButton {
                                id: currentObjectSkipButton
                                Layout.fillWidth: true
                                Layout.preferredHeight: root.jobButtonHeight
                                Layout.alignment: Qt.AlignVCenter
                                text: "Skip Current"
                                iconName: "object"
                                enabled: root.currentObject.length > 0
                                    && root.excludedObjectNames.indexOf(root.currentObject) < 0
                                onClicked: root.requestJobAction("skip_current", "")
                            }
                        }

                        GridLayout {
                            visible: root.metrics.ultraWide
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: root.metrics.ultraWide ? 1 : 2
                            rows: 2
                            rowSpacing: root.metrics.gap
                            columnSpacing: root.metrics.gap

                            JobButton {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                text: "Skip Selected"
                                iconName: "object"
                                enabled: root.activeExcludeObjectName().length > 0
                                onClicked: root.requestJobAction("skip", root.activeExcludeObjectName())
                            }

                            JobButton {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                text: "Skip Current"
                                iconName: "object"
                                enabled: root.currentObject.length > 0
                                    && root.excludedObjectNames.indexOf(root.currentObject) < 0
                                onClicked: root.requestJobAction("skip_current", "")
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
