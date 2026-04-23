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
                            text: root.durationLabel(root.printDuration) + " elapsed"
                            horizontalAlignment: Text.AlignRight
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                        }
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: [
                        {"label": "Elapsed", "value": root.durationLabel(root.printDuration)},
                        {"label": "Total", "value": root.durationLabel(root.totalDuration)},
                        {"label": "Layer", "value": root.layerLabel()},
                        {"label": "Filament used", "value": root.filamentLabel()},
                        {"label": "State", "value": root.printState},
                        {"label": "Mode", "value": "readonly"}
                    ]

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.8))
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
}
