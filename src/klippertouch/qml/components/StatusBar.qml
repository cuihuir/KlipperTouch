import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    required property string hostname
    required property string state
    required property int objectCount

    color: "#1f252b"
    height: 56

    Row {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 18

        Label {
            color: "white"
            text: "KlipperTouch"
            font.pixelSize: 22
            font.bold: true
        }

        Label {
            color: "#d8dee9"
            text: root.hostname + " | " + root.state + " | objects: " + root.objectCount
            font.pixelSize: 16
        }
    }
}
