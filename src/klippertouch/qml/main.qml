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

    Rectangle {
        anchors.fill: parent
        color: "#11161a"

        StatusBar {
            id: statusBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            hostname: window.hostname
            state: window.klippyState
            objectCount: window.objectCount
        }

        ActionBar {
            id: actionBar
            anchors.top: statusBar.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
        }

        Rectangle {
            anchors.top: statusBar.bottom
            anchors.left: actionBar.right
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 18
            radius: 18
            color: "#202830"

            Label {
                anchors.centerIn: parent
                color: "#d8dee9"
                text: "Read-only skeleton. Printer controls are disabled."
                font.pixelSize: 24
            }
        }
    }
}
