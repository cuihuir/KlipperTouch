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
    property var temperatureModel: null
    property var activeTemperatureModel: temperatureModel && temperatureModel.rowCount() > 0
        ? temperatureModel
        : fallbackTemperatureModel

    color: Theme.titleBarBg

    TemperatureDeviceModel {
        id: fallbackTemperatureModel
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
                model: root.activeTemperatureModel

                Row {
                    property string resolvedIcon: typeof icon === "undefined" ? iconName : icon

                    height: heaterStrip.height
                    spacing: Math.max(2, Math.round(root.fontSize * 0.25))

                    TemperatureIcon {
                        iconName: parent.resolvedIcon
                        iconSize: Math.max(14, Math.round(root.fontSize * 1.05))
                        compact: true
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Label {
                        color: Theme.text
                        text: typeof temperature === "undefined" || temperature === null
                            ? "--"
                            : Math.round(temperature) + "°"
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
