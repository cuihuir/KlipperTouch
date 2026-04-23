import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
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

    Rectangle {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        color: Theme.buttonsBg
        border.color: "#465456"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.45)

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
                    text: root.printFilename.length > 0 ? root.printFilename : "Job Status"
                    elide: Text.ElideMiddle
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    color: Theme.mutedText
                    text: root.printState
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.86))
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(118, Math.round(root.metrics.fontSize * 8.2))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: root.printMessage.length > 0 ? root.printMessage : "Read-only job status"
                        elide: Text.ElideRight
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                    }

                    ProgressBar {
                        Layout.fillWidth: true
                        value: Math.max(0, Math.min(1, root.printProgress / 100))
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: Math.round(root.printProgress) + "%"
                            font.pixelSize: Math.max(20, Math.round(root.metrics.fontSize * 1.5))
                        }

                        Label {
                            color: Theme.mutedText
                            text: root.remainingLabel() + " remaining"
                            horizontalAlignment: Text.AlignRight
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                        }
                    }
                }
            }

            GridView {
                id: cardGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                cellWidth: width / (root.metrics.portrait ? 1 : 2)
                cellHeight: Math.max(60, Math.round(root.metrics.fontSize * 4.25))
                model: [
                    {"label": "Elapsed", "value": root.durationLabel(root.printDuration)},
                    {"label": "Remaining", "value": root.remainingLabel()},
                    {"label": "Total", "value": root.durationLabel(root.totalDuration)},
                    {"label": "Layer", "value": root.layerLabel()},
                    {"label": "Filament used", "value": root.filamentLabel()},
                    {"label": "Speed", "value": root.speedLabel(root.requestedSpeed)},
                    {"label": "Speed factor", "value": root.percentLabel(root.speedFactor)},
                    {"label": "Flow", "value": root.percentLabel(root.extrudeFactor)},
                    {"label": "Z offset", "value": root.zOffsetLabel()},
                    {"label": "Accel", "value": root.accelLabel()},
                    {"label": "Max velocity", "value": root.speedLabel(root.maxVelocity)},
                    {"label": "State", "value": root.printState},
                    {"label": "Mode", "value": "readonly"}
                ]

                delegate: Rectangle {
                    required property var modelData

                    width: cardGrid.cellWidth - root.metrics.gap
                    height: cardGrid.cellHeight - root.metrics.gap
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: modelData.label
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: modelData.value
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                        }
                    }
                }
            }
        }
    }
}
