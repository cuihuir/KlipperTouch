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
    property var gcodeFileBridgeModel: typeof gcodeFileModel === "undefined" ? null : gcodeFileModel
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property string klipperVersion: bridgeModel ? bridgeModel.klipperVersion : "unknown"
    property string moonrakerVersion: bridgeModel ? bridgeModel.moonrakerVersion : "unknown"
    property int objectCount: bridgeModel ? bridgeModel.objectCount : 0
    property string printState: bridgeModel ? bridgeModel.printState : "standby"
    property string printFilename: bridgeModel ? bridgeModel.printFilename : ""
    property real printProgress: bridgeModel ? bridgeModel.printProgress : 0
    property string printMessage: bridgeModel ? bridgeModel.printMessage : ""
    property real printDuration: bridgeModel ? bridgeModel.printDuration : 0
    property real totalDuration: bridgeModel ? bridgeModel.totalDuration : 0
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
        case "print":
            return printComponent
        case "more":
            return infoComponent
        case "move":
            return moveComponent
        case "extrude":
            return extrudeComponent
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

        Component {
            id: printComponent

            PrintPanel {
                metrics: appMetrics
                fileModel: window.gcodeFileBridgeModel
                printState: window.printState
                printFilename: window.printFilename
                printProgress: window.printProgress
                printMessage: window.printMessage
                printDuration: window.printDuration
                totalDuration: window.totalDuration
            }
        }

        Component {
            id: infoComponent

            InfoPanel {
                metrics: appMetrics
                hostname: window.hostname
                klippyState: window.klippyState
                klipperVersion: window.klipperVersion
                moonrakerVersion: window.moonrakerVersion
                objectCount: window.objectCount
            }
        }

        Component {
            id: moveComponent

            MovePanel {
                metrics: appMetrics
            }
        }

        Component {
            id: extrudeComponent

            ExtrudePanel {
                metrics: appMetrics
            }
        }
    }
}
