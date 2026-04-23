import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    required property string hostname
    required property string state
    required property int objectCount
    property string printerName: hostname
    property string panelTitle: "Home"
    property string clockText: Qt.formatTime(new Date(), "hh:mm")
    property real fontSize: 16

    color: "#1f252b"

    Row {
        anchors.fill: parent
        anchors.margins: Math.max(4, Math.round(root.fontSize * 0.45))
        spacing: Math.max(8, Math.round(root.fontSize * 0.9))

        Label {
            id: heaterStrip
            color: "white"
            text: "♨ 21°   ▥ 25°   Pi: " + root.objectCount
            font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.8))
            verticalAlignment: Text.AlignVCenter
            width: parent.width * 0.35
            height: parent.height
            elide: Text.ElideRight
        }

        Label {
            id: titleLabel
            color: "white"
            text: root.printerName + " | " + root.panelTitle
            font.pixelSize: Math.max(11, Math.round(root.fontSize * 0.9))
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            width: parent.width * 0.32
            height: parent.height
            elide: Text.ElideRight
        }

        Label {
            id: clockLabel
            color: "#d8dee9"
            text: root.clockText
            font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.8))
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            width: parent.width * 0.22
            height: parent.height
            elide: Text.ElideRight
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: root.clockText = Qt.formatTime(new Date(), "hh:mm")
    }
}
