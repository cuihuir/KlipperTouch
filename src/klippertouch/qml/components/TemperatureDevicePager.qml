import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme
import "../models"

Item {
    id: root
    property var temperatureModel: null
    property int deviceColumns: 1
    property int pageIndex: 0
    property bool showTargets: true
    property bool compact: false
    property bool hasExternalTemperatureModel: typeof temperatureModel !== "undefined"
        && temperatureModel !== null
    property var activeTemperatureModel: root.hasExternalTemperatureModel
        ? temperatureModel
        : fallbackTemperatureModel
    property real fontSize: 16
    property int touchTargetSize: Math.max(44, Math.round(root.fontSize * 2.8))
    property int targetEditorMargin: Math.max(8, Math.round(root.fontSize * 0.7))
    property bool targetEditorFullscreen: false
    property int rowHeight: compact
        ? root.touchTargetSize
        : Math.max(root.touchTargetSize * 2, Math.round(root.fontSize * 7.9))
    property int pageControlSpacing: Math.max(6, Math.round(root.fontSize * 0.4))
    property int rawAvailableRows: Math.max(1, Math.floor(root.height / rowHeight))
    property bool needsPageControls: root.modelCount() > root.deviceColumns * root.rawAvailableRows
    property int pageControlReservedHeight: root.needsPageControls
        ? root.touchTargetSize + root.pageControlSpacing
        : 0
    property int availableRows: Math.max(1, Math.floor(deviceGrid.height / rowHeight))
    property int pageSize: Math.max(1, root.deviceColumns * root.availableRows)
    property int currentItemCount: Math.max(0, Math.min(root.pageSize, root.modelCount() - root.pageIndex * root.pageSize))
    property int modelRevision: 0
    property real targetColumnWidth: root.showTargets ? 0.27 : 0
    property real compactValueColumnWidth: root.showTargets ? 0.46 : 0.32
    property string targetEditorDeviceName: ""
    property string targetEditorDisplayName: ""
    property string targetEditorValue: ""
    property var targetEditorActual: null
    signal targetTemperatureRequested(string deviceName, real target)

    component KeypadButton: Button {
        id: keyRoot
        property bool primary: false

        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumWidth: root.touchTargetSize
        Layout.minimumHeight: root.touchTargetSize
        font.pixelSize: Math.max(16, Math.round(root.fontSize * 1.1))

        contentItem: Label {
            text: keyRoot.text
            color: keyRoot.enabled ? Theme.text : Theme.mutedText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font: keyRoot.font
        }

        background: Rectangle {
            color: keyRoot.primary ? "#1b2b2e" : "#101819"
            border.color: keyRoot.primary ? Theme.color4 : "#536165"
            border.width: 1
            radius: Math.round(root.fontSize * 0.32)
            opacity: keyRoot.enabled ? 1 : 0.45
        }
    }

    function modelCount() {
        if (!root.activeTemperatureModel) {
            return 0
        }
        if (typeof root.activeTemperatureModel.rowCount === "function") {
            return root.activeTemperatureModel.rowCount()
        }
        if (typeof root.activeTemperatureModel.count !== "undefined") {
            return root.activeTemperatureModel.count
        }
        return 0
    }

    function pageCount() {
        var total = root.modelCount()
        return Math.max(1, Math.ceil(total / root.pageSize))
    }

    function pagedModel() {
        var items = []
        var source = root.activeTemperatureModel
        if (!source) {
            return items
        }
        for (var row = 0; row < root.currentItemCount; row += 1) {
            items.push(root.itemAt(row))
        }
        return items
    }

    function itemAt(pageRow, revision) {
        revision
        var source = root.activeTemperatureModel
        var row = root.pageIndex * root.pageSize + pageRow
        if (!source || row < 0 || row >= root.modelCount()) {
            return {}
        }
        if (typeof source.rowData === "function") {
            return source.rowData(row)
        }
        if (typeof source.get === "function") {
            var entry = source.get(row)
            return {
                "name": entry.name,
                "displayName": entry.displayName || entry.deviceName,
                "icon": entry.icon || entry.iconName,
                "temperature": entry.temperature,
                "target": entry.target,
                "graphVisible": entry.graphVisible === undefined ? false : entry.graphVisible,
            }
        }
        return {}
    }

    function clampPageIndex() {
        pageIndex = Math.max(0, Math.min(pageIndex, pageCount() - 1))
    }

    function refreshVisibleItems() {
        root.modelRevision += 1
    }

    function goToPreviousPage() {
        if (root.pageIndex > 0) {
            root.pageIndex -= 1
        }
    }

    function goToNextPage() {
        if (root.pageIndex < root.pageCount() - 1) {
            root.pageIndex += 1
        }
    }

    function editorMinimumWidth() {
        return root.touchTargetSize * 3
            + Math.max(6, Math.round(root.fontSize * 0.4)) * 2
            + root.targetEditorMargin * 2
    }

    function editorMinimumHeight() {
        if (!root.targetEditorPortrait()) {
            return root.touchTargetSize * 5
                + Math.max(6, Math.round(root.fontSize * 0.4)) * 3
                + root.targetEditorMargin * 2
        }
        return root.touchTargetSize * 6
            + Math.max(8, Math.round(root.fontSize * 0.55)) * 5
            + root.targetEditorMargin * 2
    }

    function editorParentWidth() {
        return targetEditorPopup.parent ? targetEditorPopup.parent.width : root.width
    }

    function editorParentHeight() {
        return targetEditorPopup.parent ? targetEditorPopup.parent.height : root.height
    }

    function targetEditorPortrait() {
        return root.editorParentHeight() > root.editorParentWidth()
    }

    function rootRectInEditorParent() {
        var parentItem = targetEditorPopup.parent
        if (!parentItem || !root.mapToItem) {
            return {"x": 0, "y": 0, "width": root.width, "height": root.height}
        }
        var point = root.mapToItem(parentItem, 0, 0)
        return {"x": point.x, "y": point.y, "width": root.width, "height": root.height}
    }

    function bestExternalEditorRegion(minWidth, minHeight) {
        var margin = root.targetEditorMargin
        var parentWidth = root.editorParentWidth()
        var parentHeight = root.editorParentHeight()
        var rect = root.rootRectInEditorParent()
        var regions = [
            {"x": margin, "y": margin, "width": Math.max(0, rect.x - margin * 2), "height": parentHeight - margin * 2},
            {"x": rect.x + rect.width + margin, "y": margin, "width": Math.max(0, parentWidth - rect.x - rect.width - margin * 2), "height": parentHeight - margin * 2},
            {"x": margin, "y": margin, "width": parentWidth - margin * 2, "height": Math.max(0, rect.y - margin * 2)},
            {"x": margin, "y": rect.y + rect.height + margin, "width": parentWidth - margin * 2, "height": Math.max(0, parentHeight - rect.y - rect.height - margin * 2)}
        ]
        var best = null
        for (var i = 0; i < regions.length; i += 1) {
            var region = regions[i]
            if (region.width < minWidth || region.height < minHeight) {
                continue
            }
            if (best === null || region.width * region.height > best.width * best.height) {
                best = region
            }
        }
        return best
    }

    function positionTargetEditor() {
        var margin = root.targetEditorMargin
        var minWidth = root.editorMinimumWidth()
        var minHeight = root.editorMinimumHeight()
        var parentWidth = root.editorParentWidth()
        var parentHeight = root.editorParentHeight()
        var region = root.bestExternalEditorRegion(minWidth, minHeight)
        if (region !== null) {
            root.targetEditorFullscreen = false
            targetEditorPopup.width = Math.min(region.width, Math.max(minWidth, Math.round(parentWidth * 0.5)))
            targetEditorPopup.height = Math.min(region.height, Math.max(minHeight, Math.round(parentHeight * 0.82)))
            targetEditorPopup.x = Math.round(region.x + (region.width - targetEditorPopup.width) / 2)
            targetEditorPopup.y = Math.round(region.y + (region.height - targetEditorPopup.height) / 2)
            return
        }

        root.targetEditorFullscreen = true
        targetEditorPopup.width = Math.max(minWidth, parentWidth - margin * 2)
        targetEditorPopup.height = Math.max(minHeight, parentHeight - margin * 2)
        targetEditorPopup.x = Math.round((parentWidth - targetEditorPopup.width) / 2)
        targetEditorPopup.y = Math.round((parentHeight - targetEditorPopup.height) / 2)
    }

    function openTargetEditor(deviceName, displayName, actual, target) {
        root.targetEditorDeviceName = deviceName
        root.targetEditorDisplayName = displayName
        root.targetEditorActual = actual
        root.targetEditorValue = target === null || typeof target === "undefined"
            ? ""
            : String(Math.round(target))
        root.positionTargetEditor()
        targetEditorPopup.open()
    }

    function appendTargetDigit(digit) {
        if (root.targetEditorValue.length >= 3) {
            return
        }
        if (root.targetEditorValue === "0") {
            root.targetEditorValue = digit
            return
        }
        root.targetEditorValue += digit
    }

    function deleteTargetDigit() {
        root.targetEditorValue = root.targetEditorValue.slice(0, -1)
    }

    function clearTargetEditor() {
        root.targetEditorValue = ""
    }

    function confirmTargetEditor() {
        var value = Number(root.targetEditorValue)
        if (!isFinite(value)) {
            return
        }
        value = Math.max(0, Math.min(350, Math.round(value)))
        root.targetEditorValue = String(value)
        if (typeof root.activeTemperatureModel.setPendingTarget === "function") {
            root.activeTemperatureModel.setPendingTarget(root.targetEditorDeviceName, value)
        }
        root.targetTemperatureRequested(root.targetEditorDeviceName, value)
        targetEditorPopup.close()
    }

    onPageSizeChanged: clampPageIndex()

    TemperatureDeviceModel {
        id: fallbackTemperatureModel
    }

    Connections {
        target: root.activeTemperatureModel
        ignoreUnknownSignals: true

        function onModelReset() {
            root.clampPageIndex()
            root.refreshVisibleItems()
        }

        function onDataChanged() {
            root.refreshVisibleItems()
        }

        function onRowsInserted() {
            root.clampPageIndex()
            root.refreshVisibleItems()
        }

        function onRowsRemoved() {
            root.clampPageIndex()
            root.refreshVisibleItems()
        }

        function onGraphSelectionChanged() {
            root.refreshVisibleItems()
        }
    }

    WheelHandler {
        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
        onWheel: function(event) {
            if (event.angleDelta.y < 0) {
                root.goToNextPage()
            } else if (event.angleDelta.y > 0) {
                root.goToPreviousPage()
            }
            event.accepted = true
        }
    }

    GridView {
        id: deviceGrid
        anchors.fill: parent
        anchors.bottomMargin: root.pageControlReservedHeight
        clip: true
        interactive: false
        cellWidth: Math.floor(deviceGrid.width / root.deviceColumns)
        cellHeight: root.rowHeight
        model: root.currentItemCount

        delegate: Item {
            property var entry: root.itemAt(index, root.modelRevision)
            property string deviceKey: entry.name || ""
            property bool deviceGraphVisible: entry.graphVisible === undefined ? false : entry.graphVisible
            property string resolvedIcon: typeof entry.icon === "undefined" || entry.icon === null
                ? "heat-up"
                : entry.icon
            property string resolvedName: typeof entry.displayName === "undefined" || entry.displayName === null
                ? "Temperature"
                : entry.displayName
            property var targetValue: typeof entry.target === "undefined" ? null : entry.target
            property string targetState: entry.targetState === undefined ? "actual" : entry.targetState
            property var temperatureValue: typeof entry.temperature === "undefined" ? null : entry.temperature

            function targetColor() {
                if (targetState === "failed") {
                    return "#ff5d5d"
                }
                if (targetState === "pending") {
                    return Theme.color4
                }
                return Theme.mutedText
            }

            width: Math.max(0, deviceGrid.cellWidth)
            height: deviceGrid.cellHeight

            Rectangle {
                anchors.fill: parent
                anchors.margins: compact ? 0 : Math.max(3, Math.round(root.fontSize * 0.12))
                color: compact ? "transparent" : "#101617"
                border.color: compact
                    ? "transparent"
                    : deviceGraphVisible ? Theme.color4 : "#263233"
                border.width: compact ? 0 : deviceGraphVisible ? 2 : 1
                radius: compact ? 0 : Math.round(root.fontSize * 0.32)

                Loader {
                    anchors.fill: parent
                    sourceComponent: compact ? compactDelegate : cardDelegate
                }
            }

            Component {
                id: compactDelegate

                Row {
                    anchors.fill: parent
                    spacing: Math.max(4, Math.round(root.fontSize * 0.35))

                    Item {
                        id: graphToggleArea
                        width: parent.width * (1 - root.compactValueColumnWidth)
                            - parent.spacing * (root.showTargets ? 3 : 2)
                        height: Math.max(root.touchTargetSize, parent.height)

                        Rectangle {
                            id: compactGraphStateBorder
                            anchors.fill: parent
                            anchors.rightMargin: Math.max(4, Math.round(root.fontSize * 0.35))
                            color: deviceGraphVisible ? "#101617" : "transparent"
                            border.color: deviceGraphVisible ? Theme.color4 : "#465456"
                            border.width: 1
                            radius: Math.round(root.fontSize * 0.25)
                            opacity: deviceGraphVisible ? 1.0 : 0.55
                        }

                        TemperatureIcon {
                            id: compactGraphIcon
                            iconName: resolvedIcon
                            iconSize: Math.max(22, Math.round(root.fontSize * 1.55))
                            anchors.left: parent.left
                            anchors.leftMargin: Math.max(6, Math.round(root.fontSize * 0.45))
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Label {
                            anchors.left: compactGraphIcon.right
                            anchors.right: compactGraphStateBorder.right
                            anchors.leftMargin: Math.max(4, Math.round(root.fontSize * 0.35))
                            anchors.rightMargin: Math.max(4, Math.round(root.fontSize * 0.35))
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            color: deviceGraphVisible ? Theme.text : Theme.mutedText
                            text: resolvedName
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.95))
                        }

                        Rectangle {
                            id: compactGraphStateBar
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.rightMargin: compactGraphStateBorder.anchors.rightMargin
                            anchors.bottom: parent.bottom
                            height: Math.max(2, Math.round(root.fontSize * 0.18))
                            color: deviceGraphVisible ? Theme.color4 : "#465456"
                            opacity: deviceGraphVisible ? 1.0 : 0.35
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (typeof root.activeTemperatureModel.toggleGraphDevice === "function") {
                                    root.activeTemperatureModel.toggleGraphDevice(deviceKey)
                                }
                            }
                        }
                    }

                    Item {
                        id: compactValueArea
                        width: parent.width * root.compactValueColumnWidth
                        height: Math.max(root.touchTargetSize, parent.height)

                        Row {
                            anchors.fill: parent
                            spacing: Math.max(4, Math.round(root.fontSize * 0.35))

                            Label {
                                color: Theme.text
                                text: temperatureValue === null
                                    ? "--"
                                    : Math.round(temperatureValue) + "°"
                                width: root.showTargets ? parent.width * 0.5 - parent.spacing / 2 : parent.width
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.95))
                            }

                            Label {
                                color: targetColor()
                                visible: root.showTargets
                                text: targetValue === null
                                    ? "--"
                                    : Math.round(targetValue) + "°"
                                width: parent.width * 0.5 - parent.spacing / 2
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.95))
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.openTargetEditor(
                                deviceKey,
                                resolvedName,
                                temperatureValue,
                                targetValue
                            )
                        }
                    }
                }
            }

            Component {
                id: cardDelegate

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Math.max(6, Math.round(root.fontSize * 0.45))
                    spacing: Math.max(6, Math.round(root.fontSize * 0.4))

                    Item {
                        id: graphToggleArea
                        Layout.fillWidth: true
                        Layout.minimumHeight: root.touchTargetSize
                        Layout.preferredHeight: Math.max(root.touchTargetSize, Math.round(root.fontSize * 3.2))

                        RowLayout {
                            anchors.fill: parent
                            spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                            TemperatureIcon {
                                iconName: resolvedIcon
                                iconSize: Math.max(28, Math.round(root.fontSize * 1.9))
                                Layout.preferredWidth: iconSize
                                Layout.preferredHeight: iconSize
                            }

                            Label {
                                id: cardTitleLabel
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: Theme.text
                                text: resolvedName
                                elide: Text.ElideRight
                                wrapMode: Text.NoWrap
                                maximumLineCount: 1
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.9))
                                font.bold: true
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (typeof root.activeTemperatureModel.toggleGraphDevice === "function") {
                                    root.activeTemperatureModel.toggleGraphDevice(deviceKey)
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "#263233"
                    }

                    Item {
                        id: cardValueArea
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: root.touchTargetSize

                        GridLayout {
                            id: actualTargetGrid
                            anchors.fill: parent
                            columns: root.showTargets ? 2 : 1
                            columnSpacing: Math.max(8, Math.round(root.fontSize * 0.5))
                            rowSpacing: Math.max(2, Math.round(root.fontSize * 0.16))

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: "Actual"
                                font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: "Target"
                                visible: root.showTargets
                                font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: temperatureValue === null ? "--" : Math.round(temperatureValue) + "°"
                                font.pixelSize: Math.max(20, Math.round(root.fontSize * 1.42))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: targetColor()
                                visible: root.showTargets
                                text: targetValue === null ? "--" : Math.round(targetValue) + "°"
                                font.pixelSize: Math.max(20, Math.round(root.fontSize * 1.42))
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.openTargetEditor(
                                deviceKey,
                                resolvedName,
                                temperatureValue,
                                targetValue
                            )
                        }
                    }
                }
            }
        }
    }

    Row {
        id: pageControls
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: root.pageControlSpacing
        spacing: root.pageControlSpacing
        visible: root.pageCount() > 1

        Button {
            id: previousPageButton
            width: root.touchTargetSize
            height: root.touchTargetSize
            enabled: root.pageIndex > 0
            text: "<"
            font.pixelSize: Math.max(14, Math.round(root.fontSize))
            onClicked: root.goToPreviousPage()
        }

        Label {
            color: Theme.mutedText
            text: (root.pageIndex + 1) + " / " + root.pageCount()
            height: root.touchTargetSize
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
        }

        Button {
            id: nextPageButton
            width: root.touchTargetSize
            height: root.touchTargetSize
            enabled: root.pageIndex < root.pageCount() - 1
            text: ">"
            font.pixelSize: Math.max(14, Math.round(root.fontSize))
            onClicked: root.goToNextPage()
        }
    }

    Popup {
        id: targetEditorPopup
        parent: Overlay.overlay
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        padding: root.targetEditorMargin

        background: Rectangle {
            color: "#101617"
            border.color: Theme.color4
            border.width: 2
            radius: Math.round(root.fontSize * 0.45)
        }

        ColumnLayout {
            id: landscapeTargetEditor
            visible: !root.targetEditorPortrait()
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: implicitHeight
            spacing: Math.max(6, Math.round(root.fontSize * 0.4))

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: false
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: root.targetEditorDisplayName
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Math.max(18, Math.round(root.fontSize * 1.2))
                }

                Label {
                    color: Theme.mutedText
                    text: (root.targetEditorActual === null
                        ? "--"
                        : Math.round(root.targetEditorActual) + "°") + " / 350°"
                    font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.82))
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: root.touchTargetSize
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: root.touchTargetSize
                    color: "#050808"
                    border.color: "#465456"
                    border.width: 1
                    radius: Math.round(root.fontSize * 0.3)

                    Label {
                        anchors.fill: parent
                        anchors.margins: Math.max(8, Math.round(root.fontSize * 0.5))
                        color: Theme.text
                        text: root.targetEditorValue === "" ? "--" : root.targetEditorValue + "°"
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: Math.max(26, Math.round(root.fontSize * 1.8))
                    }
                }

                KeypadButton {
                    id: landscapeBackspaceButton
                    Layout.preferredWidth: Math.max(root.touchTargetSize, Math.round(root.fontSize * 4.6))
                    Layout.fillWidth: false
                    text: "←"
                    onClicked: root.deleteTargetDigit()
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: root.touchTargetSize * 3
                    + Math.max(6, Math.round(root.fontSize * 0.4)) * 2
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                GridLayout {
                    id: landscapeTargetKeypadGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 3
                    columnSpacing: Math.max(6, Math.round(root.fontSize * 0.4))
                    rowSpacing: columnSpacing

                    Repeater {
                        model: ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

                        KeypadButton {
                            required property string modelData
                            text: modelData
                            onClicked: root.appendTargetDigit(modelData)
                        }
                    }
                }

                KeypadButton {
                    id: landscapeCancelButton
                    Layout.preferredWidth: Math.max(root.touchTargetSize, Math.round(root.fontSize * 5.0))
                    Layout.fillWidth: false
                    text: "Cancel"
                    onClicked: targetEditorPopup.close()
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: root.touchTargetSize
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                KeypadButton {
                    text: "."
                    onClicked: root.appendTargetDecimal()
                }

                KeypadButton {
                    text: "0"
                    onClicked: root.appendTargetDigit("0")
                }

                KeypadButton {
                    id: landscapeSetButton
                    text: "Set"
                    enabled: root.targetEditorValue !== ""
                    primary: true
                    onClicked: root.confirmTargetEditor()
                }
            }
        }

        ColumnLayout {
            visible: root.targetEditorPortrait()
            anchors.fill: parent
            spacing: Math.max(8, Math.round(root.fontSize * 0.55))

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: root.targetEditorDisplayName
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.fontSize * 1.2))
            }

            RowLayout {
                Layout.fillWidth: true

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: root.targetEditorActual === null
                        ? "Actual --"
                        : "Actual " + Math.round(root.targetEditorActual) + "°"
                    font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.85))
                }

                Label {
                    color: Theme.mutedText
                    text: "Max 350°"
                    font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.85))
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.minimumHeight: root.touchTargetSize
                Layout.preferredHeight: Math.max(root.touchTargetSize, Math.round(root.fontSize * 3.0))
                color: "#050808"
                border.color: "#465456"
                border.width: 1
                radius: Math.round(root.fontSize * 0.3)

                Label {
                    anchors.fill: parent
                    anchors.margins: Math.max(8, Math.round(root.fontSize * 0.5))
                    color: Theme.text
                    text: root.targetEditorValue === "" ? "--" : root.targetEditorValue + "°"
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(26, Math.round(root.fontSize * 1.8))
                }
            }

            GridLayout {
                id: targetKeypadGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: 3
                columnSpacing: Math.max(6, Math.round(root.fontSize * 0.4))
                rowSpacing: columnSpacing

                Repeater {
                    model: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "Clear", "0", "Del"]

                    KeypadButton {
                        required property string modelData
                        text: modelData
                        onClicked: {
                            if (modelData === "Clear") {
                                root.clearTargetEditor()
                            } else if (modelData === "Del") {
                                root.deleteTargetDigit()
                            } else {
                                root.appendTargetDigit(modelData)
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                KeypadButton {
                    text: "Cancel"
                    onClicked: targetEditorPopup.close()
                }

                KeypadButton {
                    text: "Set"
                    enabled: root.targetEditorValue !== ""
                    primary: true
                    onClicked: root.confirmTargetEditor()
                }
            }
        }
    }
}
