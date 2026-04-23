import QtQuick
import QtQuick.Controls

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
                color: "#edf4f4"
                text: ""
                width: parent.width * 0.68
            }
            Label {
                color: "#edf4f4"
                text: "Temp (°C)"
                width: parent.width * 0.32
                horizontalAlignment: Text.AlignRight
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.85))
            }
        }

        Repeater {
            model: ListModel {
                ListElement { deviceName: "▣ Extruder"; temperature: "21" }
                ListElement { deviceName: "▥ Heater bed"; temperature: "25" }
                ListElement { deviceName: "▯ Pi"; temperature: "44" }
            }

            Row {
                width: devices.width
                height: Math.max(22, Math.round(root.metrics.fontSize * 1.85))
                Label {
                    color: "#edf4f4"
                    text: deviceName
                    width: parent.width * 0.68
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.95))
                }
                Label {
                    color: "#edf4f4"
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
