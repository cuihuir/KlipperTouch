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
    property int rowHeight: compact
        ? Math.max(22, Math.round(root.fontSize * 1.85))
        : Math.max(112, Math.round(root.fontSize * 7.9))
    property int availableRows: Math.max(1, Math.floor(deviceGrid.height / rowHeight))
    property int pageSize: Math.max(1, root.deviceColumns * root.availableRows)
    property int currentItemCount: Math.max(0, Math.min(root.pageSize, root.modelCount() - root.pageIndex * root.pageSize))

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

    function itemAt(pageRow) {
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

    onPageSizeChanged: clampPageIndex()

    TemperatureDeviceModel {
        id: fallbackTemperatureModel
    }

    Connections {
        target: root.activeTemperatureModel
        ignoreUnknownSignals: true

        function onModelReset() {
            root.clampPageIndex()
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
        clip: true
        interactive: false
        cellWidth: Math.floor(deviceGrid.width / root.deviceColumns)
        cellHeight: root.rowHeight
        model: root.currentItemCount

        delegate: Item {
            property var entry: root.itemAt(index)
            property string deviceKey: entry.name || ""
            property bool deviceGraphVisible: entry.graphVisible === undefined ? false : entry.graphVisible
            property string resolvedIcon: typeof entry.icon === "undefined" || entry.icon === null
                ? "heat-up"
                : entry.icon
            property string resolvedName: typeof entry.displayName === "undefined" || entry.displayName === null
                ? "Temperature"
                : entry.displayName
            property var targetValue: typeof entry.target === "undefined" ? null : entry.target
            property var temperatureValue: typeof entry.temperature === "undefined" ? null : entry.temperature

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

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        if (typeof root.activeTemperatureModel.toggleGraphDevice === "function") {
                            root.activeTemperatureModel.toggleGraphDevice(deviceKey)
                        }
                    }
                }

                Loader {
                    anchors.fill: parent
                    sourceComponent: compact ? compactDelegate : cardDelegate
                }
            }

            Component {
                id: compactDelegate

                Row {
                    spacing: Math.max(4, Math.round(root.fontSize * 0.35))

                    TemperatureIcon {
                        iconName: resolvedIcon
                        iconSize: Math.max(22, Math.round(root.fontSize * 1.55))
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Label {
                        color: Theme.text
                        text: resolvedName
                        width: parent.width * 0.68 - parent.spacing - Math.max(22, Math.round(root.fontSize * 1.55))
                        elide: Text.ElideRight
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.95))
                    }

                    Label {
                        color: Theme.text
                        text: temperatureValue === null
                            ? "--"
                            : Math.round(temperatureValue) + "°"
                        width: parent.width * 0.32
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.95))
                    }
                }
            }

            Component {
                id: cardDelegate

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Math.max(6, Math.round(root.fontSize * 0.45))
                    spacing: Math.max(6, Math.round(root.fontSize * 0.4))

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                        TemperatureIcon {
                            iconName: resolvedIcon
                            iconSize: Math.max(28, Math.round(root.fontSize * 1.9))
                            Layout.preferredWidth: iconSize
                            Layout.preferredHeight: iconSize
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: resolvedName
                            elide: Text.ElideRight
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                            font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.9))
                            font.bold: true
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "#263233"
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: "Actual"
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
                        color: Theme.mutedText
                        text: "Target"
                        visible: root.showTargets
                        font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        visible: root.showTargets
                        text: targetValue === null ? "--" : Math.round(targetValue) + "°"
                        font.pixelSize: Math.max(16, Math.round(root.fontSize * 1.08))
                    }
                }
            }
        }
    }

    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Math.max(6, Math.round(root.fontSize * 0.4))
        spacing: Math.max(6, Math.round(root.fontSize * 0.4))
        visible: root.pageCount() > 1

        Label {
            color: Theme.mutedText
            text: (root.pageIndex + 1) + " / " + root.pageCount()
            font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
        }
    }
}
