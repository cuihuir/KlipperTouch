import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    required property string label
    required property string iconText
    required property color accent
    property real fontSize: 16

    color: "#090909"
    border.color: root.accent
    border.width: Math.max(2, Math.round(root.fontSize * 0.12))
    radius: Math.round(root.fontSize)

    Column {
        anchors.fill: parent
        anchors.margins: Math.max(8, Math.round(root.fontSize * 0.55))
        spacing: Math.max(2, Math.round(root.fontSize * 0.2))

        Image {
            property int tileIconSize: Math.round(root.fontSize * 4.2)

            width: parent.width
            height: parent.height - labelText.height - accentBar.height - parent.spacing * 2
            source: "../assets/material-dark/images/" + root.iconText + ".svg"
            fillMode: Image.PreserveAspectFit
            sourceSize.width: tileIconSize
            sourceSize.height: tileIconSize
        }

        Label {
            id: labelText
            width: parent.width
            color: "#edf4f4"
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
