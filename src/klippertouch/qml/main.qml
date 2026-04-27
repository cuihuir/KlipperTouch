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
    property var jobControlBridgeModel: typeof jobControlModel === "undefined" ? null : jobControlModel
    property var notificationBridgeModel: typeof notificationModel === "undefined" ? null : notificationModel
    property string requestedPrintState: jobControlBridgeModel ? jobControlBridgeModel.requestedPrintState : ""
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property string webhooksState: bridgeModel ? bridgeModel.webhooksState : ""
    property string webhooksMessage: bridgeModel ? bridgeModel.webhooksMessage : ""
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
    property bool systemFaultVisible: window.moonrakerFaultActive()
        || window.webhooksFaultActive()
        || window.klippyFaultActive()
    property var panelTitles: ({"main": "Home", "move": "Move", "temperature": "Temperature", "extrude": "Extrude", "more": "More", "system": "System", "network": "Network", "logs": "Logs", "language": "Language", "update": "Update", "print": "Print", "job_status": "Job Status", "notifications": "Notifications", "splash": "Printer Status"})
    property var panelIcons: ({"main": "main", "move": "move", "temperature": "heat-up", "extrude": "extrude", "more": "settings", "system": "settings", "network": "main", "logs": "printer", "language": "settings", "update": "printer", "print": "printer", "job_status": "printer", "notifications": "printer", "splash": "printer"})

    function shouldAutoEnterJobStatus() {
        return window.printState === "printing" || window.printState === "paused"
    }

    function shouldKeepJobStatusVisible() {
        return window.shouldAutoEnterJobStatus()
            || window.printState === "complete"
            || window.printState === "cancelled"
            || window.printState === "error"
    }

    function moonrakerFaultActive() {
        return !bridgeModel || window.moonrakerVersion.length <= 0 || window.moonrakerVersion === "unknown"
    }

    function klippyFaultActive() {
        if (window.webhooksState === "ready") {
            return false
        }
        return window.klippyState.length <= 0 || window.klippyState !== "ready"
    }

    function webhooksFaultActive() {
        if (window.webhooksState === "ready") {
            return false
        }
        return window.webhooksState === "shutdown"
            || window.webhooksMessage.indexOf("Shutdown due to webhooks") >= 0
    }

    function systemFaultActive() {
        return window.systemFaultVisible
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

    function syncRequestedPrintState() {
        if (window.requestedPrintState === "standby" && window.currentPanel === "job_status") {
            window.panelStack = ["main", "print"]
            window.currentPanel = "print"
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
        case "notifications":
            return notificationCenterComponent
        case "splash":
            return splashComponent
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

    function effectiveComponentForPanel(panelName) {
        if (window.systemFaultActive()) {
            return splashComponent
        }
        return window.componentForPanel(panelName)
    }

    function requestJobControl(action, objectName) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "pause") {
            jobControlBridgeModel.requestPause()
        } else if (action === "resume") {
            jobControlBridgeModel.requestResume()
        } else if (action === "cancel") {
            jobControlBridgeModel.requestCancel()
        } else if (action === "skip") {
            jobControlBridgeModel.requestSkipObject(objectName)
        } else if (action === "clear") {
            jobControlBridgeModel.requestClearJob()
        }
    }

    function requestRecoveryControl(action) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "firmware_restart") {
            jobControlBridgeModel.requestFirmwareRestart()
        } else if (action === "restart_klipper") {
            jobControlBridgeModel.requestKlipperRestart()
        } else if (action === "restart_moonraker") {
            jobControlBridgeModel.requestPlaceholderControl("Restart Moonraker")
        } else if (action === "emergency_stop") {
            jobControlBridgeModel.requestEmergencyStop()
        }
    }

    function requestEmergencyStop() {
        if (!jobControlBridgeModel) {
            return
        }
        jobControlBridgeModel.requestEmergencyStop()
    }

    function requestMoveControl(action, distance) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "disable_motors") {
            jobControlBridgeModel.requestDisableMotors()
        } else if (action === "home_xy") {
            jobControlBridgeModel.requestHome("xy")
        } else if (action === "home_z") {
            jobControlBridgeModel.requestHome("z")
        } else if (action === "x_minus" || action === "x_plus"
                   || action === "y_minus" || action === "y_plus"
                   || action === "z_minus" || action === "z_plus") {
            jobControlBridgeModel.requestMoveJog(action, distance)
        }
    }

    function requestFileControl(action, path) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "print") {
            jobControlBridgeModel.requestStartPrint(path)
            if (window.jobControlBridgeModel.lastError.length <= 0) {
                if (panelLoader.item
                        && typeof panelLoader.item.handleFilePrintStarted === "function") {
                    panelLoader.item.handleFilePrintStarted(path)
                }
                window.showPanel("job_status")
            }
        } else if (action === "delete") {
            jobControlBridgeModel.requestDeleteFile(path)
        }
    }

    function clampControlPercent(value) {
        return Math.max(1, Math.min(999, value))
    }

    function notify(level, title, message, source, sticky, actionPanel) {
        if (!notificationBridgeModel) {
            return
        }
        notificationBridgeModel.addNotification(level, title, message, source, sticky, actionPanel)
    }

    Metrics {
        id: appMetrics
        viewportWidth: window.width
        viewportHeight: window.height
    }

    onPrintStateChanged: window.syncJobStatusPanel()
    onRequestedPrintStateChanged: window.syncRequestedPrintState()
    onCurrentPanelChanged: {
        if (bridgeModel && typeof bridgeModel.setActivePanel === "function") {
            bridgeModel.setActivePanel(window.currentPanel)
        }
    }
    Component.onCompleted: window.syncJobStatusPanel()

    Connections {
        target: window.jobControlBridgeModel

        function onStatusChanged() {
            if (window.jobControlBridgeModel && window.jobControlBridgeModel.lastStatus.length > 0) {
                window.notify("info", "Command sent", window.jobControlBridgeModel.lastStatus, "job", false, window.currentPanel)
            }
        }

        function onErrorChanged() {
            if (window.jobControlBridgeModel && window.jobControlBridgeModel.lastError.length > 0) {
                window.notify("error", "Command failed", window.jobControlBridgeModel.lastError, "job", true, window.currentPanel)
            }
        }

        function onFileDeleted(path) {
            if (panelLoader.item && typeof panelLoader.item.handleFileDeleted === "function") {
                panelLoader.item.handleFileDeleted(path)
            }
            if (window.gcodeFileBridgeModel) {
                window.gcodeFileBridgeModel.removeFile(path)
            }
        }
    }

    BaseShell {
        anchors.fill: parent
        metrics: appMetrics
        hostname: window.hostname
        state: window.klippyState
        objectCount: window.objectCount
        temperatureModel: window.temperatureBridgeModel
        notificationUnreadCount: window.notificationBridgeModel
            ? window.notificationBridgeModel.unreadCount
            : 0
        panelTitle: window.panelTitles[window.currentPanel]
        onBackRequested: window.goBack()
        onHomeRequested: window.goHome()
        onMenuRequested: window.showPanel("more")
        onNotificationsRequested: window.showPanel("notifications")
        onStopRequested: window.requestEmergencyStop()

        Loader {
            id: panelLoader
            objectName: "panelLoader"
            anchors.fill: parent
            sourceComponent: window.systemFaultVisible
                ? splashComponent
                : window.componentForPanel(window.currentPanel)
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
            id: splashComponent

            SplashPanel {
                metrics: appMetrics
                hostname: window.hostname
                klippyState: window.klippyState
                moonrakerVersion: window.moonrakerVersion
                webhooksState: window.webhooksState
                webhooksMessage: window.webhooksMessage
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                onRecoveryActionRequested: function(action) {
                    window.requestRecoveryControl(action)
                }
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
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                onFileActionRequested: function(action, path) {
                    window.requestFileControl(action, path)
                }
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
                positionX: window.positionX
                positionY: window.positionY
                positionZ: window.positionZ
                positionE: window.positionE
                homedAxes: window.homedAxes
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
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                requestedPrintState: window.jobControlBridgeModel ? window.jobControlBridgeModel.requestedPrintState : ""
                onJobActionRequested: function(action, objectName) {
                    window.requestJobControl(action, objectName)
                }
                onZOffsetAdjustRequested: function(delta) {
                    if (window.jobControlBridgeModel) {
                        window.jobControlBridgeModel.requestZOffsetAdjust(delta)
                    }
                }
                onSpeedFactorAdjustRequested: function(delta) {
                    if (window.jobControlBridgeModel) {
                        window.jobControlBridgeModel.requestSpeedFactor(window.clampControlPercent(window.speedFactor + delta))
                    }
                }
                onExtrudeFactorAdjustRequested: function(delta) {
                    if (window.jobControlBridgeModel) {
                        window.jobControlBridgeModel.requestExtrudeFactor(window.clampControlPercent(window.extrudeFactor + delta))
                    }
                }
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
            id: notificationCenterComponent

            NotificationCenterPanel {
                metrics: appMetrics
                notificationModel: window.notificationBridgeModel
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
                onMoveActionRequested: function(action, distance) {
                    window.requestMoveControl(action, distance)
                }
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
