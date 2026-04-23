import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var axes: ["X-", "X+", "Y-", "Y+", "Z-", "Z+"]
    property var distances: ["0.1", "1", "10", "100"]
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
    property string homedAxes: ""

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
                    text: "Move"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "Controls locked"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(78, Math.round(root.metrics.fontSize * 5.4))
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(3, Math.round(root.metrics.fontSize * 0.25))

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 4
                            columnSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: "X " + root.positionX.toFixed(2)
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: "Y " + root.positionY.toFixed(2)
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: "Z " + root.positionZ.toFixed(2)
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: "E " + root.positionE.toFixed(2)
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                            }
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.homedAxes.length > 0 ? "Homed: " + root.homedAxes : "Homed: unknown"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }
                    }
                }

                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: root.axes

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
                                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.35))
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
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
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Repeater {
                    model: root.distances

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(42, Math.round(root.metrics.fontSize * 3.1))
                        color: "#101617"
                        opacity: 0.55
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        Label {
                            anchors.centerIn: parent
                            color: Theme.mutedText
                            text: modelData + " mm"
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                        }
                    }
                }

                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}
