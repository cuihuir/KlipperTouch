import QtQuick
import "../Theme.js" as Theme

Rectangle {
    id: root
    required property var metrics
    required property string hostname
    required property string state
    required property int objectCount
    property var temperatureModel: null
    property string panelTitle: "Home"
    property int notificationUnreadCount: 0
    default property alias panelContent: contentLayer.data
    signal backRequested()
    signal homeRequested()
    signal menuRequested()
    signal notificationsRequested()
    signal stopRequested()

    color: Theme.bg

    ActionBar {
        id: actionBar
        vertical: !root.metrics.portrait
        width: root.metrics.portrait ? parent.width : root.metrics.actionBarWidth
        height: root.metrics.portrait ? root.metrics.actionBarHeight : parent.height
        anchors.left: parent.left
        anchors.top: root.metrics.portrait ? undefined : parent.top
        anchors.bottom: root.metrics.portrait ? parent.bottom : undefined
        onActionRequested: function(actionName) {
            switch (actionName) {
            case "back":
                root.backRequested()
                break
            case "home":
                root.homeRequested()
                break
            case "menu":
                root.menuRequested()
                break
            case "stop":
                root.stopRequested()
                break
            }
        }
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
        printerName: root.hostname
        panelTitle: root.panelTitle
        temperatureModel: root.temperatureModel
        notificationUnreadCount: root.notificationUnreadCount
        onNotificationRequested: root.notificationsRequested()
    }

    Item {
        id: contentLayer
        anchors.top: titlebar.bottom
        anchors.left: root.metrics.portrait ? parent.left : actionBar.right
        anchors.right: parent.right
        anchors.bottom: root.metrics.portrait ? actionBar.top : parent.bottom
    }
}
