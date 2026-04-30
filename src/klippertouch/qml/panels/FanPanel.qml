import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    objectName: "fanPanel"
    required property var metrics
    property var fanDevices: []
    property string controlStatus: ""
    property string controlError: ""
    signal fanSpeedRequested(string deviceName, real percent)

    Rectangle {
        anchors.fill: parent
        color: "#071112"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        spacing: root.metrics.gap

        RowLayout {
            Layout.fillWidth: true
            spacing: root.metrics.gap

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Fans"
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
            }

            Label {
                color: root.controlError.length > 0 ? "#c7ced1" : Theme.mutedText
                text: root.controlError.length > 0
                    ? root.controlError
                    : root.controlStatus.length > 0 ? root.controlStatus : root.fanDevices.length + " devices"
                elide: Text.ElideRight
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
            }
        }

        Label {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.fanDevices.length <= 0
            color: Theme.mutedText
            text: "No fans detected"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: root.metrics.fontSize
        }

        ListView {
            id: fanList
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.fanDevices.length > 0
            clip: true
            spacing: root.metrics.gap
            boundsBehavior: Flickable.StopAtBounds
            model: root.fanDevices

            delegate: Rectangle {
                id: fanCard
                required property var modelData
                readonly property real speedValue: Number(modelData.speed || 0)
                readonly property string modeText: modelData.speed_settable ? "manual" : "auto"

                width: fanList.width
                height: Math.max(
                    modelData.speed_settable ? 136 : 92,
                    Math.round(root.metrics.fontSize * (modelData.speed_settable ? 8.6 : 5.9))
                )
                color: "#0d1415"
                border.color: modelData.speed_settable ? "#536165" : "#344346"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.38)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: Math.max(6, Math.round(root.metrics.gap * 0.65))

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: modelData.display_name
                                elide: Text.ElideRight
                                font.bold: true
                                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: modelData.name + " · " + fanCard.modeText
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                            }
                        }

                        Label {
                            color: Theme.text
                            text: Math.round(fanCard.speedValue) + "%"
                            horizontalAlignment: Text.AlignRight
                            font.bold: true
                            font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                        color: "#101819"
                        border.color: "#263233"
                        border.width: 1
                        radius: height / 2

                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: Math.max(parent.height, parent.width * Math.max(0, Math.min(100, fanCard.speedValue)) / 100)
                            color: "#7f9298"
                            radius: parent.radius
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 2.8))
                        visible: modelData.speed_settable
                        spacing: Math.max(6, Math.round(root.metrics.gap * 0.6))

                        Repeater {
                            model: [0, 25, 50, 75, 100]

                            Rectangle {
                                required property int modelData
                                readonly property int percent: modelData

                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: Math.round(fanCard.speedValue) === percent ? "#1b2b2e" : "#101819"
                                border.color: Math.round(fanCard.speedValue) === percent ? "#7f9298" : "#536165"
                                border.width: Math.round(fanCard.speedValue) === percent ? 2 : 1
                                radius: Math.round(root.metrics.fontSize * 0.28)

                                Label {
                                    anchors.centerIn: parent
                                    color: Theme.text
                                    text: percent === 0 ? "Off" : percent + "%"
                                    font.bold: true
                                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.fanSpeedRequested(fanCard.modelData.name, percent)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
