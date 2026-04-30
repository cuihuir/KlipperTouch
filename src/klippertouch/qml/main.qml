import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "Theme.js" as Theme
import "components"
import "panels"

ApplicationWindow {
    id: window
    width: window.startFullScreen ? Screen.width : 1024
    height: window.startFullScreen ? Screen.height : 600
    visible: true
    title: "KlipperTouch"
    visibility: window.startFullScreen ? Window.FullScreen : Window.Windowed

    property var bridgeModel: typeof statusModel === "undefined" ? null : statusModel
    property var temperatureBridgeModel: typeof temperatureDeviceModel === "undefined" ? null : temperatureDeviceModel
    property var gcodeFileBridgeModel: typeof gcodeFileModel === "undefined" ? null : gcodeFileModel
    property var fileRefreshBridgeModel: typeof gcodeFileRefresh === "undefined" ? null : gcodeFileRefresh
    property var jobControlBridgeModel: typeof jobControlModel === "undefined" ? null : jobControlModel
    property var notificationBridgeModel: typeof notificationModel === "undefined" ? null : notificationModel
    property bool startFullScreen: typeof configuredFullScreen === "undefined" ? false : configuredFullScreen
    property string displayRotation: typeof configuredDisplayRotation === "undefined" ? "" : configuredDisplayRotation
    property bool displayRotated: window.displayRotation === "right" || window.displayRotation === "left"
    property int sceneWidth: window.displayRotated ? window.height : window.width
    property int sceneHeight: window.displayRotated ? window.width : window.height
    property bool materialSystemEnabled: typeof configuredMaterialSystemEnabled === "undefined" ? false : configuredMaterialSystemEnabled
    property string requestedPrintState: jobControlBridgeModel ? jobControlBridgeModel.requestedPrintState : ""
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property string webhooksState: bridgeModel ? bridgeModel.webhooksState : ""
    property string webhooksMessage: bridgeModel ? bridgeModel.webhooksMessage : ""
    property bool bootstrapComplete: bridgeModel ? bridgeModel.bootstrapComplete : false
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
    property real positionU: bridgeModel ? bridgeModel.positionU : 0
    property real positionV: bridgeModel ? bridgeModel.positionV : 0
    property real positionW: bridgeModel ? bridgeModel.positionW : 0
    property bool fiveAxisAvailable: bridgeModel ? bridgeModel.fiveAxisAvailable : false
    property bool acceleratorLevelAvailable: bridgeModel ? bridgeModel.acceleratorLevelAvailable : false
    property bool zTiltAvailable: bridgeModel ? bridgeModel.zTiltAvailable : false
    property string homedAxes: bridgeModel ? bridgeModel.homedAxes : ""
    property real requestedSpeed: bridgeModel ? bridgeModel.requestedSpeed : 0
    property real speedFactor: bridgeModel ? bridgeModel.speedFactor : 100
    property real extrudeFactor: bridgeModel ? bridgeModel.extrudeFactor : 100
    property real zOffset: bridgeModel ? bridgeModel.zOffset : 0
    property real maxAccel: bridgeModel ? bridgeModel.maxAccel : 0
    property real maxVelocity: bridgeModel ? bridgeModel.maxVelocity : 0
    property real extruderTemperature: bridgeModel ? bridgeModel.extruderTemperature : 0
    property real extruderTarget: bridgeModel ? bridgeModel.extruderTarget : 0
    property bool extruderCanExtrude: bridgeModel ? bridgeModel.extruderCanExtrude : false
    property real extruderPressureAdvance: bridgeModel ? bridgeModel.extruderPressureAdvance : 0
    property real extruderSmoothTime: bridgeModel ? bridgeModel.extruderSmoothTime : 0
    property var filamentSensors: bridgeModel ? bridgeModel.filamentSensors : []
    property var fanDevices: bridgeModel ? bridgeModel.fanDevices : []
    property var excludeObjectNames: bridgeModel ? bridgeModel.excludeObjectNames : []
    property var excludedObjectNames: bridgeModel ? bridgeModel.excludedObjectNames : []
    property string currentObject: bridgeModel ? bridgeModel.currentObject : ""
    property bool toastVisible: false
    property string toastLevel: "info"
    property string toastTitle: ""
    property string toastMessage: ""
    property string currentPanel: "main"
    property var panelStack: ["main"]
    property bool startupSplashHoldComplete: false
    property bool startupSplashVisible: !window.startupSplashHoldComplete
        || (!window.printerReadyForUi() && !window.systemFaultVisible)
    property bool systemFaultVisible: window.bootstrapComplete && !window.printerReadyForUi() && (
        window.moonrakerFaultActive()
        || window.webhooksFaultActive()
        || window.klippyFaultActive()
    )
    property var panelTitles: ({"main": "Home", "move": "Move", "temperature": "Temperature", "extrude": "Extrude", "more": "More", "system": "System", "fans": "Fans", "network": "Network", "logs": "Logs", "language": "Language", "update": "Update", "print": "Print", "job_status": "Job Status", "notifications": "Notifications", "splash": "Printer Status"})
    property var panelIcons: ({"main": "main", "move": "move", "temperature": "heat-up", "extrude": "extrude", "more": "settings", "system": "settings", "fans": "fan", "network": "network", "logs": "logs", "language": "language", "update": "update", "print": "printer", "job_status": "printer", "notifications": "notification", "splash": "printer"})

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

    function moonrakerConnected() {
        return !window.moonrakerFaultActive()
    }

    function printerReadyForUi() {
        return window.moonrakerConnected()
            && window.klippyState === "ready"
            && (window.webhooksState === "ready" || window.webhooksState.length <= 0)
    }

    function klippyFaultActive() {
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
            if (window.requestedPrintState === "standby" && window.printState === "standby") {
                window.panelStack = ["main", "print"]
                window.currentPanel = "print"
                return
            }
            window.goHome()
        }
    }

    function syncRequestedPrintState() {
        if (window.requestedPrintState === "standby"
                && window.printState === "standby"
                && window.currentPanel === "job_status") {
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
        case "fans":
            return fanComponent
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
        if (action === "retry" && bridgeModel) {
            window.startupSplashHoldComplete = false
            startupSplashHoldTimer.restart()
            bridgeModel.requestStatusRetry()
            return
        }
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "firmware_restart") {
            jobControlBridgeModel.requestFirmwareRestart()
        } else if (action === "restart_klipper") {
            jobControlBridgeModel.requestKlipperRestart()
        }
    }

    function requestEmergencyStop() {
        if (!jobControlBridgeModel) {
            return
        }
        jobControlBridgeModel.requestEmergencyStop()
    }

    function requestMoveControl(action, distance, speed) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "disable_motors") {
            jobControlBridgeModel.requestDisableMotors()
        } else if (action === "home_all") {
            jobControlBridgeModel.requestHome("all")
        } else if (action === "home_xy") {
            jobControlBridgeModel.requestHome("xy")
        } else if (action === "home_z") {
            jobControlBridgeModel.requestHome("z")
        } else if (action === "home_uvw") {
            jobControlBridgeModel.requestHome("uvw")
        } else if (action === "z_tilt_adjust") {
            jobControlBridgeModel.requestZTiltAdjust()
        } else if (action === "accelerator_level") {
            jobControlBridgeModel.requestAcceleratorLevel()
        } else if (action.indexOf("placeholder_") === 0) {
            jobControlBridgeModel.requestPlaceholderControl("Move " + action.slice(12))
        } else if (action === "x_minus" || action === "x_plus"
                   || action === "y_minus" || action === "y_plus"
                   || action === "z_minus" || action === "z_plus"
                   || action === "u_minus" || action === "u_plus"
                   || action === "v_minus" || action === "v_plus"
                   || action === "w_minus" || action === "w_plus") {
            jobControlBridgeModel.requestMoveJog(action, distance, speed)
        }
    }

    function requestExtrudeControl(action, distance, speed) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "extrude" || action === "retract") {
            jobControlBridgeModel.requestExtrudeFilament(action, distance, speed)
        } else if (action === "load") {
            jobControlBridgeModel.requestLoadFilament(speed)
        } else if (action === "unload") {
            jobControlBridgeModel.requestUnloadFilament(speed)
        }
    }

    function requestTemperatureTarget(deviceName, target) {
        if (!jobControlBridgeModel) {
            return
        }
        jobControlBridgeModel.requestTemperatureTarget(deviceName, target)
        if (jobControlBridgeModel.lastError.length > 0
                && temperatureBridgeModel
                && typeof temperatureBridgeModel.setFailedTarget === "function") {
            temperatureBridgeModel.setFailedTarget(deviceName, target)
        }
    }

    function requestFanSpeed(deviceName, percent) {
        if (!jobControlBridgeModel) {
            return
        }
        jobControlBridgeModel.requestFanSpeed(deviceName, percent)
    }

    function requestFileControl(action, path) {
        if (!jobControlBridgeModel) {
            return
        }
        if (action === "print") {
            if (panelLoader.item
                    && typeof panelLoader.item.handleFilePrintStarted === "function") {
                panelLoader.item.handleFilePrintStarted(path)
            }
            window.showPanel("job_status")
            Qt.callLater(function() { jobControlBridgeModel.requestStartPrint(path) })
        } else if (action === "delete") {
            jobControlBridgeModel.requestDeleteFile(path)
        }
    }

    function clampControlPercent(value) {
        return Math.max(1, Math.min(999, value))
    }

    function showToast(level, title, message) {
        window.toastLevel = level || "info"
        window.toastTitle = title || ""
        window.toastMessage = message || ""
        window.toastVisible = true
        toastTimer.restart()
    }

    function shouldStoreNotification(level, sticky) {
        var normalizedLevel = (level || "info").toLowerCase()
        return sticky || normalizedLevel === "warning" || normalizedLevel === "error"
    }

    function notify(level, title, message, source, sticky, actionPanel) {
        window.showToast(level, title, message)
        if (!notificationBridgeModel || !window.shouldStoreNotification(level, sticky)) {
            return
        }
        notificationBridgeModel.addNotification(level, title, message, source, sticky, actionPanel)
    }

    Metrics {
        id: appMetrics
        viewportWidth: window.sceneWidth
        viewportHeight: window.sceneHeight
    }

    onPrintStateChanged: window.syncJobStatusPanel()
    onRequestedPrintStateChanged: window.syncRequestedPrintState()
    onCurrentPanelChanged: {
        if (bridgeModel && typeof bridgeModel.setActivePanel === "function") {
            bridgeModel.setActivePanel(window.currentPanel)
        }
    }
    Component.onCompleted: window.syncJobStatusPanel()

    Timer {
        id: startupSplashHoldTimer
        interval: 2000
        running: true
        repeat: false
        onTriggered: window.startupSplashHoldComplete = true
    }

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

    Connections {
        target: window.notificationBridgeModel

        function onToastRequested(level, title, message) {
            window.showToast(level, title, message)
        }
    }

    Item {
        id: sceneRoot
        width: window.sceneWidth
        height: window.sceneHeight
        anchors.centerIn: parent
        rotation: window.displayRotation === "right" ? 90 : window.displayRotation === "left" ? -90 : 0
        transformOrigin: Item.Center

        BaseShell {
            anchors.fill: parent
        metrics: appMetrics
        hostname: window.hostname
        state: window.klippyState
        objectCount: window.objectCount
        temperatureModel: window.temperatureBridgeModel
        navigationEnabled: !(window.startupSplashVisible || window.systemFaultVisible)
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
            sourceComponent: window.startupSplashVisible || window.systemFaultVisible
                ? splashComponent
                : window.componentForPanel(window.currentPanel)
        }

        Component {
            id: mainMenuComponent

            MainMenuPanel {
                metrics: appMetrics
                popupParent: scenePopupLayer
                temperatureModel: window.temperatureBridgeModel
                onPanelRequested: function(panelName) { window.showPanel(panelName) }
                onTargetTemperatureRequested: function(deviceName, target) {
                    window.requestTemperatureTarget(deviceName, target)
                }
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
                connecting: window.startupSplashVisible && !window.systemFaultVisible
                ready: window.printerReadyForUi()
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
                popupParent: scenePopupLayer
                temperatureModel: window.temperatureBridgeModel
                onTargetTemperatureRequested: function(deviceName, target) {
                    window.requestTemperatureTarget(deviceName, target)
                }
            }
        }

        Component {
            id: filesComponent

            FilesPanel {
                metrics: appMetrics
                fileModel: window.gcodeFileBridgeModel
                loading: window.fileRefreshBridgeModel ? window.fileRefreshBridgeModel.loading : false
                loadError: window.fileRefreshBridgeModel ? window.fileRefreshBridgeModel.lastError : ""
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                onFileActionRequested: function(action, path) {
                    window.requestFileControl(action, path)
                }
                onRefreshRequested: function() {
                    if (window.fileRefreshBridgeModel) {
                        window.fileRefreshBridgeModel.refresh_once()
                    }
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
            id: fanComponent

            FanPanel {
                metrics: appMetrics
                fanDevices: window.fanDevices
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                onFanSpeedRequested: function(deviceName, percent) {
                    if (window.jobControlBridgeModel) {
                        jobControlBridgeModel.requestFanSpeed(deviceName, percent)
                    }
                }
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
                positionU: window.positionU
                positionV: window.positionV
                positionW: window.positionW
                fiveAxisAvailable: window.fiveAxisAvailable
                acceleratorLevelAvailable: window.acceleratorLevelAvailable
                zTiltAvailable: window.zTiltAvailable
                homedAxes: window.homedAxes
                klippyState: window.klippyState
                webhooksState: window.webhooksState
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                onMoveActionRequested: function(action, distance, speed) {
                    window.requestMoveControl(action, distance, speed)
                }
            }
        }

        Component {
            id: extrudeComponent

            ExtrudePanel {
                metrics: appMetrics
                popupParent: scenePopupLayer
                extruderTemperature: window.extruderTemperature
                extruderTarget: window.extruderTarget
                extruderCanExtrude: window.extruderCanExtrude
                extruderPressureAdvance: window.extruderPressureAdvance
                extruderSmoothTime: window.extruderSmoothTime
                filamentSensors: window.filamentSensors
                materialSystemEnabled: window.materialSystemEnabled
                positionE: window.positionE
                klippyState: window.klippyState
                webhooksState: window.webhooksState
                controlStatus: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastStatus : ""
                controlError: window.jobControlBridgeModel ? window.jobControlBridgeModel.lastError : ""
                onExtrudeActionRequested: function(action, distance, speed) {
                    window.requestExtrudeControl(action, distance, speed)
                }
                onTemperatureTargetRequested: function(deviceName, target) {
                    window.requestTemperatureTarget(deviceName, target)
                }
                onPressureAdvanceRequested: function(advance, smoothTime) {
                    if (window.jobControlBridgeModel) {
                        jobControlBridgeModel.requestPressureAdvance(advance, smoothTime)
                    }
                }
            }
            }
        }

        Item {
            id: scenePopupLayer
            anchors.fill: parent
            z: 200
        }

    Timer {
        id: toastTimer
        interval: 3200
        repeat: false
        onTriggered: window.toastVisible = false
    }

    Rectangle {
        id: toastCard
        visible: window.toastVisible
        z: 100
        height: Math.max(Math.round(appMetrics.fontSize * 4.8), toastContent.implicitHeight + appMetrics.gap * 2)
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: appMetrics.titlebarHeight + appMetrics.margin
        anchors.leftMargin: appMetrics.portrait ? appMetrics.margin : appMetrics.actionBarWidth + appMetrics.margin
        anchors.rightMargin: appMetrics.margin
        radius: Math.round(appMetrics.fontSize * 0.55)
        color: window.toastLevel === "error" ? "#182023" : "#101819"
        border.color: window.toastLevel === "info" ? "#536165" : "#8b9496"
        border.width: 2
        opacity: 0.97

        ColumnLayout {
            id: toastContent
            anchors.fill: parent
            anchors.margins: appMetrics.gap
            spacing: Math.max(3, Math.round(appMetrics.gap * 0.45))

            Label {
                Layout.fillWidth: true
                text: window.toastTitle
                color: Theme.text
                font.bold: true
                font.pixelSize: Math.max(13, Math.round(appMetrics.fontSize * 0.9))
                elide: Text.ElideRight
            }

            Label {
                Layout.fillWidth: true
                text: window.toastMessage
                color: Theme.mutedText
                font.pixelSize: Math.max(11, Math.round(appMetrics.fontSize * 0.75))
                elide: Text.ElideRight
                visible: window.toastMessage.length > 0
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                window.toastVisible = false
                toastTimer.stop()
            }
        }
    }
    }
}
