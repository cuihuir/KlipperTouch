import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    required property string title
    required property string iconName

    Column {
        anchors.centerIn: parent
        width: Math.min(parent.width * 0.72, Math.round(root.metrics.fontSize * 28))
        spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.9))

        Image {
            source: Theme.iconSource(root.iconName)
            width: Math.max(56, Math.round(root.metrics.fontSize * 4.2))
            height: width
            anchors.horizontalCenter: parent.horizontalCenter
            fillMode: Image.PreserveAspectFit
            sourceSize.width: width
            sourceSize.height: height
        }

        Label {
            width: parent.width
            color: Theme.text
            text: root.title
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.5))
            font.bold: true
        }

        Label {
            width: parent.width
            color: Theme.mutedText
            text: "No printer commands are enabled on this screen yet."
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.95))
        }
    }
}
