import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property string hostname: "unknown"
    property string klippyState: "unknown"
    property string klipperVersion: "unknown"
    property string moonrakerVersion: "unknown"
    property int objectCount: 0
    property var objectNames: []

    property var rows: [
        {"label": "Hostname", "value": root.hostname},
        {"label": "Klippy state", "value": root.klippyState},
        {"label": "Klipper", "value": root.klipperVersion},
        {"label": "Moonraker", "value": root.moonrakerVersion},
        {"label": "Objects", "value": String(root.objectCount)}
    ]

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
                    text: "Printer information"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    color: Theme.mutedText
                    text: "readonly"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(160, Math.round(root.metrics.fontSize * 11))
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: root.rows

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(58, Math.round(root.metrics.fontSize * 4.1))
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
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: modelData.value
                                elide: Text.ElideMiddle
                                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.02))
                            }
                        }
                    }
                }
            }

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Moonraker objects"
                font.bold: true
                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
            }

            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.28))
                model: root.objectNames

                delegate: Rectangle {
                    width: ListView.view.width
                    height: Math.max(34, Math.round(root.metrics.fontSize * 2.45))
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.26)

                    Label {
                        anchors.fill: parent
                        anchors.leftMargin: root.metrics.gap
                        anchors.rightMargin: root.metrics.gap
                        color: Theme.mutedText
                        text: modelData
                        elide: Text.ElideMiddle
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }
                }
            }
        }
    }
}
