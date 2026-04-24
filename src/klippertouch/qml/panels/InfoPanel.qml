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
    property var mcuInfos: []
    property var serviceVersions: []

    property var summaryRows: [
        {"label": "Host", "value": root.hostname},
        {"label": "Klippy state", "value": root.klippyState},
        {"label": "Klipper", "value": root.klipperVersion},
        {"label": "Moonraker", "value": root.moonrakerVersion}
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
                    text: "System information"
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
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: root.summaryRows

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(52, Math.round(root.metrics.fontSize * 3.6))
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

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.42))

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: "MCU information"
                            font.bold: true
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                        }

                        ListView {
                            id: mcuList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.42))
                            model: root.mcuInfos

                            delegate: Rectangle {
                                required property var modelData

                                width: mcuList.width
                                height: Math.max(68, Math.round(root.metrics.fontSize * 4.8))
                                color: "#0b1112"
                                border.color: "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.26)

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: root.metrics.gap
                                    spacing: Math.max(2, Math.round(root.metrics.fontSize * 0.15))

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.text
                                        text: modelData.name
                                        elide: Text.ElideRight
                                        font.bold: true
                                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.mutedText
                                        text: modelData.version
                                        elide: Text.ElideMiddle
                                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.mutedText
                                        text: modelData.build_versions
                                        elide: Text.ElideMiddle
                                        visible: text.length > 0
                                        font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                    }
                                }
                            }
                        }

                        Label {
                            Layout.fillWidth: true
                            visible: root.mcuInfos.length === 0
                            color: Theme.mutedText
                            text: "No MCU version data"
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.42))

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: "Service versions"
                            font.bold: true
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                        }

                        ListView {
                            id: serviceList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.42))
                            model: root.serviceVersions

                            delegate: Rectangle {
                                required property var modelData

                                width: serviceList.width
                                height: Math.max(56, Math.round(root.metrics.fontSize * 4.0))
                                color: "#0b1112"
                                border.color: "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.26)

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: root.metrics.gap
                                    spacing: Math.max(2, Math.round(root.metrics.fontSize * 0.15))

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: root.metrics.gap

                                        Label {
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            text: modelData.name
                                            elide: Text.ElideRight
                                            font.bold: true
                                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                                        }

                                        Label {
                                            color: Theme.mutedText
                                            text: modelData.configured_type
                                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                        }
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.mutedText
                                        text: modelData.version
                                        elide: Text.ElideMiddle
                                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                                    }
                                }
                            }
                        }

                        Label {
                            Layout.fillWidth: true
                            visible: root.serviceVersions.length === 0
                            color: Theme.mutedText
                            text: "No service version data"
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                        }
                    }
                }
            }
        }
    }
}
