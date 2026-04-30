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
    property int notificationUnreadCount: 0
    property bool interactionEnabled: true
    property bool hasExternalTemperatureModel: typeof temperatureModel !== "undefined"
        && temperatureModel !== null
    property var activeTemperatureModel: root.hasExternalTemperatureModel
        ? temperatureModel
        : fallbackTemperatureModel
    property int maxVisibleTemperatureItems: Math.max(
        2,
        Math.floor(heaterStrip.width / Math.max(42, root.fontSize * 2.8))
    )
    signal notificationRequested()

    function updateClock() {
        var nextText = Qt.formatTime(new Date(), "hh:mm")
        if (nextText !== root.clockText) {
            root.clockText = nextText
        }
    }

    function scheduleNextClockTick() {
        var now = new Date()
        var nextMinuteDelay = 60000 - (now.getSeconds() * 1000 + now.getMilliseconds())
        clockTimer.interval = Math.max(250, nextMinuteDelay)
        clockTimer.restart()
    }

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
            width: parent.width * (root.width < 520 ? 0.25 : 0.35)
            height: parent.height
            spacing: Math.max(6, Math.round(root.fontSize * 0.5))
            clip: true

            Repeater {
                model: root.activeTemperatureModel

                Row {
                    property string resolvedIcon: typeof icon === "undefined" ? iconName : icon

                    visible: index < root.maxVisibleTemperatureItems
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
            width: parent.width * (root.width < 520 ? 0.45 : 0.32)
            height: parent.height
            elide: Text.ElideRight
        }

        Item {
            id: notificationArea
            width: parent.width * 0.22
            height: parent.height
            scale: notificationPressArea.pressed && root.interactionEnabled ? 0.97 : 1.0
            transformOrigin: Item.Center
            Behavior on scale {
                NumberAnimation { duration: 70; easing.type: Easing.OutQuad }
            }

            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: Math.max(6, Math.round(root.fontSize * 0.35))

                Rectangle {
                    id: notificationBadge
                    width: Math.max(26, Math.round(root.fontSize * 1.6))
                    height: Math.max(22, Math.round(root.fontSize * 1.25))
                    radius: Math.round(height * 0.45)
                    color: root.notificationUnreadCount > 0 ? "#5f6b70" : "#30383d"
                    border.color: root.notificationUnreadCount > 0 ? "#9aa7ad" : "#4c565b"
                    border.width: 1

                    Label {
                        anchors.centerIn: parent
                        color: Theme.text
                        text: root.notificationUnreadCount > 0
                            ? (root.notificationUnreadCount > 99 ? "99+" : root.notificationUnreadCount)
                            : "!"
                        font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.68))
                        font.bold: root.notificationUnreadCount > 0
                    }
                }

                Label {
                    id: clockLabel
                    color: Theme.mutedText
                    text: root.clockText
                    font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.8))
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    height: notificationArea.height
                    elide: Text.ElideRight
                }
            }

            MouseArea {
                id: notificationPressArea
                anchors.fill: parent
                enabled: root.interactionEnabled
                onClicked: root.notificationRequested()
            }
        }
    }

    Timer {
        id: clockTimer
        repeat: false
        running: false
        onTriggered: {
            root.updateClock()
            root.scheduleNextClockTick()
        }
    }

    Component.onCompleted: root.scheduleNextClockTick()
}
