import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics

    Column {
        id: devices
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Math.round(parent.height * (root.metrics.portrait ? 0.55 : 0.52))
        spacing: root.metrics.gap

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
            model: ListModel {
                ListElement { deviceName: "Extruder"; iconName: "extruder"; temperature: "21" }
                ListElement { deviceName: "Heater bed"; iconName: "bed"; temperature: "25" }
                ListElement { deviceName: "Pi"; iconName: "heat-up"; temperature: "44" }
            }

            Row {
                width: devices.width
                height: Math.max(22, Math.round(root.metrics.fontSize * 1.85))
                spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))

                Image {
                    source: Theme.iconSource(iconName)
                    width: Math.max(18, Math.round(root.metrics.fontSize * 1.35))
                    height: width
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    sourceSize.width: width
                    sourceSize.height: height
                }

                Label {
                    color: Theme.text
                    text: deviceName
                    width: parent.width * 0.68 - parent.spacing - Math.max(18, Math.round(root.metrics.fontSize * 1.35))
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.95))
                }
                Label {
                    color: Theme.text
                    text: temperature
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
