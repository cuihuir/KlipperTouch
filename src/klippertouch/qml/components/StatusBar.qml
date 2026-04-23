import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme
import "../models"

Rectangle {
    id: root
    required property string hostname
    required property string state
    required property int objectCount
    property string printerName: hostname
    property string panelTitle: "Home"
    property string clockText: Qt.formatTime(new Date(), "hh:mm")
    property real fontSize: 16

    color: Theme.titleBarBg

    TemperatureDeviceModel {
        id: titlebarHeaters
    }

    Row {
        anchors.fill: parent
        anchors.margins: Math.max(4, Math.round(root.fontSize * 0.45))
        spacing: Math.max(8, Math.round(root.fontSize * 0.9))

        Row {
            id: heaterStrip
            width: parent.width * 0.35
            height: parent.height
            spacing: Math.max(6, Math.round(root.fontSize * 0.5))
            clip: true

            Repeater {
                model: titlebarHeaters

                Row {
                    height: heaterStrip.height
                    spacing: Math.max(2, Math.round(root.fontSize * 0.25))

                    Image {
                        source: Theme.iconSource(iconName)
                        width: Math.max(12, Math.round(root.fontSize * 0.95))
                        height: width
                        anchors.verticalCenter: parent.verticalCenter
                        fillMode: Image.PreserveAspectFit
                        sourceSize.width: width
                        sourceSize.height: height
                    }

                    Label {
                        color: Theme.text
                        text: temperature + "°"
                        font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.8))
                        verticalAlignment: Text.AlignVCenter
                        height: parent.height
                    }
                }
            }
        }

        Label {
            id: titleLabel
            color: Theme.text
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
            color: Theme.mutedText
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
