import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    required property string label
    required property string iconText
    required property color accent
    property real fontSize: 16

    color: "transparent"
    border.width: 0

    Column {
        anchors.fill: parent
        anchors.margins: Math.max(2, Math.round(root.fontSize * 0.25))
        spacing: Math.max(2, Math.round(root.fontSize * 0.2))

        Label {
            width: parent.width
            height: parent.height - labelText.height - accentBar.height - parent.spacing * 2
            color: "#edf4f4"
            text: root.iconText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: Math.max(28, Math.round(root.fontSize * 3.1))
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
        }
    }
}
