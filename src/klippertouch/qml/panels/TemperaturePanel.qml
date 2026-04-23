import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme
import "../components"
import "../models"

Item {
    id: root
    required property var metrics
    property var temperatureModel: null
    property var activeTemperatureModel: temperatureModel && temperatureModel.rowCount() > 0
        ? temperatureModel
        : fallbackTemperatureModel

    TemperatureDeviceModel {
        id: fallbackTemperatureModel
    }

    GridLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap
        columns: root.metrics.portrait ? 1 : 2
        rows: root.metrics.portrait ? 2 : 1

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * 0.45
            Layout.preferredHeight: root.metrics.portrait ? parent.height * 0.45 : parent.height
            Layout.minimumWidth: 0
            Layout.minimumHeight: 0
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
                    color: Theme.mutedText
                    text: "Temperature status (readonly)"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: "Heater"
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }

                    Label {
                        Layout.preferredWidth: Math.max(62, Math.round(root.metrics.fontSize * 4.4))
                        color: Theme.mutedText
                        text: "Actual"
                        horizontalAlignment: Text.AlignRight
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }

                    Label {
                        Layout.preferredWidth: Math.max(62, Math.round(root.metrics.fontSize * 4.4))
                        color: Theme.mutedText
                        text: "Target"
                        horizontalAlignment: Text.AlignRight
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }
                }

                ListView {
                    id: deviceList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))
                    model: root.activeTemperatureModel

                    delegate: Rectangle {
                        property string resolvedIcon: typeof icon === "undefined" ? iconName : icon
                        property string resolvedName: typeof displayName === "undefined" ? deviceName : displayName

                        width: deviceList.width
                        height: Math.max(44, Math.round(root.metrics.fontSize * 3.2))
                        color: "#101617"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: root.metrics.gap
                            anchors.rightMargin: root.metrics.gap
                            spacing: root.metrics.gap

                            TemperatureIcon {
                                iconName: resolvedIcon
                                iconSize: Math.max(28, Math.round(root.metrics.fontSize * 1.9))
                                Layout.preferredWidth: iconSize
                                Layout.preferredHeight: iconSize
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: resolvedName
                                elide: Text.ElideRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                            }

                            Label {
                                Layout.preferredWidth: Math.max(62, Math.round(root.metrics.fontSize * 4.4))
                                color: Theme.text
                                text: typeof temperature === "undefined" || temperature === null ? "--" : Math.round(temperature) + "°"
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                            }

                            Label {
                                Layout.preferredWidth: Math.max(62, Math.round(root.metrics.fontSize * 4.4))
                                color: Theme.mutedText
                                text: typeof target === "undefined" || target === null ? "--" : Math.round(target) + "°"
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                            }
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * 0.55
            Layout.preferredHeight: root.metrics.portrait ? parent.height * 0.55 : parent.height
            Layout.minimumWidth: 0
            Layout.minimumHeight: 0

            FakeTemperatureGraph {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                fontSize: root.metrics.fontSize
                extruderSeries: root.activeTemperatureModel.extruderSeries
                bedSeries: root.activeTemperatureModel.bedSeries
            }
        }
    }
}
