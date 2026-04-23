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
    property var panelStack: ["main"]
    property var panelTitles: ({"main": "Home", "move": "Move", "temperature": "Temperature", "extrude": "Extrude", "more": "More", "print": "Print"})
    property var panelIcons: ({"main": "main", "move": "move", "temperature": "heat-up", "extrude": "extrude", "more": "settings", "print": "printer"})

    function showPanel(panelName) {
        if (panelTitles[panelName] !== undefined && panelStack[panelStack.length - 1] !== panelName) {
            var nextStack = panelStack.slice()
            nextStack.push(panelName)
            panelStack = nextStack
            currentPanel = panelName
        }
    }

    function goHome() {
        panelStack = ["main"]
        currentPanel = "main"
    }

    function goBack() {
        if (panelStack.length > 1) {
            var nextStack = panelStack.slice(0, panelStack.length - 1)
            panelStack = nextStack
        }
        currentPanel = panelStack[panelStack.length - 1]
    }

    function componentForPanel(panelName) {
        switch (panelName) {
        case "main":
            return mainMenuComponent
        case "temperature":
            return temperatureComponent
        default:
            return placeholderComponent
        }
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
            sourceComponent: window.componentForPanel(window.currentPanel)
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

        Component {
            id: temperatureComponent

            TemperaturePanel {
                metrics: appMetrics
                temperatureModel: window.temperatureBridgeModel
            }
        }
    }
}
