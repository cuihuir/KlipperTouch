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
    property var mcuInfos: bridgeModel ? bridgeModel.mcuInfos : []
    property var serviceVersions: bridgeModel ? bridgeModel.serviceVersions : []
    property int objectCount: bridgeModel ? bridgeModel.objectCount : 0
    property var objectNames: bridgeModel ? bridgeModel.objectNames : []
    property string printState: bridgeModel ? bridgeModel.printState : "standby"
    property string printFilename: bridgeModel ? bridgeModel.printFilename : ""
    property real printProgress: bridgeModel ? bridgeModel.printProgress : 0
    property string printMessage: bridgeModel ? bridgeModel.printMessage : ""
    property real printDuration: bridgeModel ? bridgeModel.printDuration : 0
    property real totalDuration: bridgeModel ? bridgeModel.totalDuration : 0
    property real filamentUsed: bridgeModel ? bridgeModel.filamentUsed : 0
    property int currentLayer: bridgeModel ? bridgeModel.currentLayer : 0
    property int totalLayers: bridgeModel ? bridgeModel.totalLayers : 0
    property real positionX: bridgeModel ? bridgeModel.positionX : 0
    property real positionY: bridgeModel ? bridgeModel.positionY : 0
    property real positionZ: bridgeModel ? bridgeModel.positionZ : 0
    property real positionE: bridgeModel ? bridgeModel.positionE : 0
    property string homedAxes: bridgeModel ? bridgeModel.homedAxes : ""
    property real requestedSpeed: bridgeModel ? bridgeModel.requestedSpeed : 0
    property real speedFactor: bridgeModel ? bridgeModel.speedFactor : 100
    property real extrudeFactor: bridgeModel ? bridgeModel.extrudeFactor : 100
    property real zOffset: bridgeModel ? bridgeModel.zOffset : 0
    property real maxAccel: bridgeModel ? bridgeModel.maxAccel : 0
    property real maxVelocity: bridgeModel ? bridgeModel.maxVelocity : 0
    property real extruderTemperature: bridgeModel ? bridgeModel.extruderTemperature : 0
    property real extruderTarget: bridgeModel ? bridgeModel.extruderTarget : 0
    property var excludeObjectNames: bridgeModel ? bridgeModel.excludeObjectNames : []
    property var excludedObjectNames: bridgeModel ? bridgeModel.excludedObjectNames : []
    property string currentObject: bridgeModel ? bridgeModel.currentObject : ""
    property string currentPanel: "main"
    property var panelStack: ["main"]
    property var panelTitles: ({"main": "Home", "move": "Move", "temperature": "Temperature", "extrude": "Extrude", "more": "More", "system": "System", "network": "Network", "logs": "Logs", "language": "Language", "update": "Update", "print": "Print", "job_status": "Job Status"})
    property var panelIcons: ({"main": "main", "move": "move", "temperature": "heat-up", "extrude": "extrude", "more": "settings", "system": "settings", "network": "main", "logs": "printer", "language": "settings", "update": "printer", "print": "printer", "job_status": "printer"})

    function shouldAutoEnterJobStatus() {
        return window.printState === "printing" || window.printState === "paused"
    }

    function shouldKeepJobStatusVisible() {
        return window.shouldAutoEnterJobStatus()
            || window.printState === "complete"
            || window.printState === "cancelled"
            || window.printState === "error"
    }

    function syncJobStatusPanel() {
        if (window.shouldAutoEnterJobStatus()) {
            if (window.currentPanel !== "job_status") {
                window.panelStack = ["job_status"]
                window.currentPanel = "job_status"
            }
        } else if (!window.shouldKeepJobStatusVisible() && window.currentPanel === "job_status") {
            window.goHome()
        }
    }

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
        if (panelLoader.item && typeof panelLoader.item.goBack === "function") {
            if (panelLoader.item.goBack()) {
                return
            }
        }
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
            return filesComponent
        case "job_status":
            return jobStatusComponent
        case "more":
            return moreMenuComponent
        case "system":
            return infoComponent
        case "network":
            return placeholderComponent
        case "logs":
            return placeholderComponent
        case "language":
            return placeholderComponent
        case "update":
            return placeholderComponent
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

    onPrintStateChanged: window.syncJobStatusPanel()
    onCurrentPanelChanged: {
        if (bridgeModel && typeof bridgeModel.setActivePanel === "function") {
            bridgeModel.setActivePanel(window.currentPanel)
        }
    }
    Component.onCompleted: window.syncJobStatusPanel()

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
            id: panelLoader
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
            id: filesComponent

            FilesPanel {
                metrics: appMetrics
                fileModel: window.gcodeFileBridgeModel
            }
        }

        Component {
            id: jobStatusComponent

            JobStatusPanel {
                metrics: appMetrics
                printState: window.printState
                printFilename: window.printFilename
                printProgress: window.printProgress
                printMessage: window.printMessage
                printDuration: window.printDuration
                totalDuration: window.totalDuration
                filamentUsed: window.filamentUsed
                currentLayer: window.currentLayer
                totalLayers: window.totalLayers
                requestedSpeed: window.requestedSpeed
                speedFactor: window.speedFactor
                extrudeFactor: window.extrudeFactor
                zOffset: window.zOffset
                maxAccel: window.maxAccel
                maxVelocity: window.maxVelocity
                excludeObjectNames: window.excludeObjectNames
                excludedObjectNames: window.excludedObjectNames
                currentObject: window.currentObject
                temperatureModel: window.temperatureBridgeModel
                fileModel: window.gcodeFileBridgeModel
            }
        }

        Component {
            id: moreMenuComponent

            MoreMenuPanel {
                metrics: appMetrics
                onPanelRequested: function(panelName) { window.showPanel(panelName) }
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
                mcuInfos: window.mcuInfos
                serviceVersions: window.serviceVersions
            }
        }

        Component {
            id: moveComponent

            MovePanel {
                metrics: appMetrics
                positionX: window.positionX
                positionY: window.positionY
                positionZ: window.positionZ
                positionE: window.positionE
                homedAxes: window.homedAxes
            }
        }

        Component {
            id: extrudeComponent

            ExtrudePanel {
                metrics: appMetrics
                extruderTemperature: window.extruderTemperature
                extruderTarget: window.extruderTarget
                positionE: window.positionE
            }
        }
    }
}
