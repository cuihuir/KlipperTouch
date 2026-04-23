import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var distances: ["5", "10", "15", "25"]
    property var speeds: ["1", "2", "5", "25"]
    property real actionFraction: 0.42
    property real settingsFraction: 0.58

    GridLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        columns: root.metrics.portrait ? 1 : 2
        rows: root.metrics.portrait ? 2 : 1
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * root.actionFraction
            Layout.minimumWidth: 0
            color: Theme.buttonsBg
            border.color: "#465456"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.45)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Extrude"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "Extrusion locked"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }

                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: ["Retract", "Extrude"]

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#101617"
                            opacity: 0.55
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.32)

                            Label {
                                anchors.centerIn: parent
                                color: Theme.mutedText
                                text: modelData
                                font.bold: true
                                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.25))
                            }
                        }
                    }
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * root.settingsFraction
            Layout.minimumWidth: 0
            columns: 2
            rowSpacing: root.metrics.gap
            columnSpacing: root.metrics.gap

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 0
                color: Theme.buttonsBg
                border.color: "#465456"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.45)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Distance"
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    Repeater {
                        model: root.distances

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: modelData + " mm"
                            horizontalAlignment: Text.AlignHCenter
                            font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.92))
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 0
                color: Theme.buttonsBg
                border.color: "#465456"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.45)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Speed"
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    Repeater {
                        model: root.speeds

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: modelData + " mm/s"
                            horizontalAlignment: Text.AlignHCenter
                            font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.92))
                        }
                    }
                }
            }
        }
    }
}
