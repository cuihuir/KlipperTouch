import QtQuick
import QtQuick.Controls
import "components"

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
    title: "KlipperTouch"

    property var bridgeModel: typeof statusModel === "undefined" ? null : statusModel
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property int objectCount: bridgeModel ? bridgeModel.objectCount : 0
    property bool isPortrait: height > width
    property int shortSide: Math.min(width, height)
    property int barThickness: Math.max(56, Math.round(shortSide * 0.12))
    property int titleHeight: Math.max(32, Math.round(shortSide * 0.07))
    property int contentMargin: Math.max(8, Math.round(shortSide * 0.03))

    Rectangle {
        anchors.fill: parent
        color: "#11161a"

        ActionBar {
            id: actionBar
            vertical: !window.isPortrait
            width: window.isPortrait ? parent.width : window.barThickness
            height: window.isPortrait ? window.barThickness : parent.height
            anchors.left: parent.left
            anchors.top: window.isPortrait ? undefined : parent.top
            anchors.bottom: window.isPortrait ? parent.bottom : undefined
        }

        StatusBar {
            id: statusBar
            height: window.titleHeight
            anchors.top: parent.top
            anchors.left: window.isPortrait ? parent.left : actionBar.right
            anchors.right: parent.right
            hostname: window.hostname
            state: window.klippyState
            objectCount: window.objectCount
        }

        Rectangle {
            anchors.top: statusBar.bottom
            anchors.left: window.isPortrait ? parent.left : actionBar.right
            anchors.right: parent.right
            anchors.bottom: window.isPortrait ? actionBar.top : parent.bottom
            anchors.margins: window.contentMargin
            radius: 18
            color: "#202830"

            Label {
                anchors.centerIn: parent
                color: "#d8dee9"
                text: "Read-only skeleton. Printer controls are disabled."
                font.pixelSize: Math.max(16, Math.round(window.shortSide * 0.04))
            }
        }
    }
}
