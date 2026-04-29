import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

Rectangle {
    id: root
    required property string label
    required property string iconText
    required property color accent
    property real fontSize: 16
    signal activated()

    color: tilePressArea.pressed ? "#182124" : Theme.buttonsBg
    scale: tilePressArea.pressed ? 0.97 : 1.0
    border.color: tilePressArea.pressed ? Theme.text : root.accent
    border.width: Math.max(2, Math.round(root.fontSize * 0.12))
    radius: Math.round(root.fontSize)
    Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
    Behavior on color { ColorAnimation { duration: 80 } }
    Behavior on border.color { ColorAnimation { duration: 80 } }

    MouseArea {
        id: tilePressArea
        anchors.fill: parent
        onClicked: root.activated()
    }

    Column {
        anchors.fill: parent
        anchors.margins: Math.max(8, Math.round(root.fontSize * 0.55))
        spacing: Math.max(2, Math.round(root.fontSize * 0.2))

        Image {
            property int tileIconSize: Math.round(root.fontSize * 4.2)

            width: parent.width
            height: parent.height - labelText.height - accentBar.height - parent.spacing * 2
            source: Theme.iconSource(root.iconText)
            fillMode: Image.PreserveAspectFit
            sourceSize.width: tileIconSize
            sourceSize.height: tileIconSize
        }

        Label {
            id: labelText
            width: parent.width
            color: Theme.text
            text: root.label
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            font.pixelSize: Math.max(12, Math.round(root.fontSize * 0.95))
        }

        Rectangle {
            id: accentBar
            width: parent.width
            height: Math.max(4, Math.round(root.fontSize * 0.35))
            color: root.accent
            radius: height / 2
        }
    }
}
