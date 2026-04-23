import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 92
    color: "#2b3138"

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Repeater {
            model: ["Back", "Home", "Status", "Files", "Temp", "Move"]

            Button {
                enabled: false
                text: modelData
                height: 52
                width: parent.width
            }
        }
    }
}
