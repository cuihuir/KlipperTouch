import QtQuick

Rectangle {
    id: root
    required property var metrics
    required property string hostname
    required property string state
    required property int objectCount
    default property alias panelContent: contentLayer.data

    color: "#071112"

    ActionBar {
        id: actionBar
        vertical: !root.metrics.portrait
        width: root.metrics.portrait ? parent.width : root.metrics.actionBarWidth
        height: root.metrics.portrait ? root.metrics.actionBarHeight : parent.height
        anchors.left: parent.left
        anchors.top: root.metrics.portrait ? undefined : parent.top
        anchors.bottom: root.metrics.portrait ? parent.bottom : undefined
    }

    StatusBar {
        id: titlebar
        height: root.metrics.titlebarHeight
        anchors.top: parent.top
        anchors.left: root.metrics.portrait ? parent.left : actionBar.right
        anchors.right: parent.right
        fontSize: root.metrics.fontSize
        hostname: root.hostname
        state: root.state
        objectCount: root.objectCount
    }

    Item {
        id: contentLayer
        anchors.top: titlebar.bottom
        anchors.left: root.metrics.portrait ? parent.left : actionBar.right
        anchors.right: parent.right
        anchors.bottom: root.metrics.portrait ? actionBar.top : parent.bottom
    }
}
