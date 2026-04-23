import QtQuick
import QtQuick.Controls
import "components"
import "panels"

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
    title: "KlipperTouch"

    property var bridgeModel: typeof statusModel === "undefined" ? null : statusModel
    property var temperatureBridgeModel: typeof temperatureDeviceModel === "undefined" ? null : temperatureDeviceModel
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property int objectCount: bridgeModel ? bridgeModel.objectCount : 0
    property string currentPanel: "main"
    property var panelTitles: ({"main": "Home", "move": "Move", "temperature": "Temperature", "extrude": "Extrude", "more": "More", "print": "Print"})
    property var panelIcons: ({"main": "main", "move": "move", "temperature": "heat-up", "extrude": "extrude", "more": "settings", "print": "printer"})

    function showPanel(panelName) {
        if (panelTitles[panelName] !== undefined) {
            currentPanel = panelName
        }
    }

    function goHome() {
        currentPanel = "main"
    }

    function goBack() {
        currentPanel = "main"
    }

    Metrics {
        id: appMetrics
        viewportWidth: window.width
        viewportHeight: window.height
    }

    BaseShell {
        anchors.fill: parent
        metrics: appMetrics
        hostname: window.hostname
        state: window.klippyState
        objectCount: window.objectCount
        temperatureModel: window.temperatureBridgeModel
        panelTitle: window.panelTitles[window.currentPanel]
        onBackRequested: window.goBack()
        onHomeRequested: window.goHome()
        onMenuRequested: window.showPanel("more")

        Loader {
            anchors.fill: parent
            sourceComponent: window.currentPanel === "main" ? mainMenuComponent : placeholderComponent
        }

        Component {
            id: mainMenuComponent

            MainMenuPanel {
                metrics: appMetrics
                temperatureModel: window.temperatureBridgeModel
                onPanelRequested: function(panelName) { window.showPanel(panelName) }
            }
        }

        Component {
            id: placeholderComponent

            PlaceholderPanel {
                metrics: appMetrics
                title: window.panelTitles[window.currentPanel]
                iconName: window.panelIcons[window.currentPanel]
            }
        }
    }
}
