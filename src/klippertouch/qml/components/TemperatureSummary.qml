import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme
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

    Column {
        id: devices
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Math.round(parent.height * (root.metrics.portrait ? 0.55 : 0.52))
        spacing: root.metrics.gap
        clip: true

        Row {
            width: parent.width
            height: Math.max(18, Math.round(root.metrics.fontSize * 1.45))
            Label {
                color: Theme.mutedText
                text: ""
                width: parent.width * 0.68
            }
            Label {
                color: Theme.mutedText
                text: "Temp (°C)"
                width: parent.width * 0.32
                horizontalAlignment: Text.AlignRight
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.85))
            }
        }

        Repeater {
            model: root.activeTemperatureModel

            Row {
                property string resolvedIcon: typeof icon === "undefined" ? iconName : icon
                property string resolvedName: typeof displayName === "undefined" ? deviceName : displayName

                width: devices.width
                height: Math.max(22, Math.round(root.metrics.fontSize * 1.85))
                spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))

                TemperatureIcon {
                    iconName: parent.resolvedIcon
                    iconSize: Math.max(22, Math.round(root.metrics.fontSize * 1.55))
                    anchors.verticalCenter: parent.verticalCenter
                }

                Label {
                    color: Theme.text
                    text: parent.resolvedName
                    width: parent.width * 0.68 - parent.spacing - Math.max(22, Math.round(root.metrics.fontSize * 1.55))
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.95))
                }
                Label {
                    color: Theme.text
                    text: typeof temperature === "undefined" || temperature === null
                        ? "--"
                        : Math.round(temperature) + "°"
                    width: parent.width * 0.32
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.95))
                }
            }
        }
    }

    FakeTemperatureGraph {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: devices.bottom
        anchors.bottom: parent.bottom
        anchors.topMargin: root.metrics.gap
        fontSize: root.metrics.fontSize
    }
}
