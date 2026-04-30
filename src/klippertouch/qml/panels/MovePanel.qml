import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../Theme.js" as Theme

Item {
    id: root
    objectName: "movePanel"
    required property var metrics
    property var moveButtons: [
        {"label": "Y+", "direction": "up", "action": "y_plus"},
        {"label": "X-", "direction": "left", "action": "x_minus"},
        {"label": "X+", "direction": "right", "action": "x_plus"},
        {"label": "Y-", "direction": "down", "action": "y_minus"},
        {"label": "Z+", "direction": "up", "action": "z_plus"},
        {"label": "Z-", "direction": "down", "action": "z_minus"}
    ]
    property var xyButtons: [
        {"label": "Y+", "direction": "up", "action": "y_plus"},
        {"label": "X-", "direction": "left", "action": "x_minus"},
        {"label": "X+", "direction": "right", "action": "x_plus"},
        {"label": "Y-", "direction": "down", "action": "y_minus"}
    ]
    property var zButtons: [
        {"label": "Z+", "direction": "up", "action": "z_plus"},
        {"label": "Z-", "direction": "down", "action": "z_minus"}
    ]
    property var bedTiltButtons: [
        {"label": "V", "actionPlus": "v_plus", "actionMinus": "v_minus", "position": "top"},
        {"label": "U", "actionPlus": "u_plus", "actionMinus": "u_minus", "position": "left"},
        {"label": "W", "actionPlus": "w_plus", "actionMinus": "w_minus", "position": "right"}
    ]
    property var actionButtons: [
        {"label": "Home All", "action": "home_all", "hint": "XYZ", "iconName": "home"},
        {"label": "Disable Motors", "action": "disable_motors", "hint": "M84", "iconName": "motor-off"},
        {"label": "Bed Tilt", "action": "bed_tilt", "hint": "UVW", "iconName": "tilt", "requires": "five_axis"},
        {"label": "More", "action": "more", "hint": "settings", "iconName": "settings"}
    ]
    property var moreActions: [
        {"label": "Home All", "action": "home_all", "hint": "XYZ", "iconName": "home"},
        {"label": "UVW Home", "action": "home_uvw", "hint": "UVW_HOME", "iconName": "tilt", "requires": "five_axis"},
        {"label": "Acc Level", "action": "accelerator_level", "hint": "MOVE=1", "iconName": "tilt", "requires": "accelerator_level"},
        {"label": "Z Tilt Adjust", "action": "z_tilt_adjust", "hint": "Z_TILT_ADJUST", "iconName": "tilt", "requires": "z_tilt"},
        {"label": "Disable Motors", "action": "disable_motors", "hint": "M84", "iconName": "motor-off"},
        {"label": "XY Speed", "action": "speed_xy", "hint": "50 mm/s", "iconName": "speed"},
        {"label": "Z Speed", "action": "speed_z", "hint": "10 mm/s", "iconName": "speed"}
    ]
    property var portraitPlaceholders: [
        {"placeholder": true},
        {"placeholder": true}
    ]
    property var distances: [".1", ".5", "1", "5", "10", "25", "50"]
    property var tiltDistances: [".01", ".05", ".1", ".5", "1"]
    property var xySpeeds: ["25", "50", "100", "150"]
    property var zSpeeds: ["2", "5", "10", "15"]
    property string selectedDistance: "10"
    property string selectedTiltDistance: ".1"
    property string selectedXYSpeed: "100"
    property string selectedZSpeed: "10"
    property string selectedTiltSpeed: "2"
    property bool moreVisible: false
    property string detailPage: "main"
    property bool confirmVisible: false
    property string pendingConfirmAction: ""
    property string pendingConfirmTitle: ""
    property string pendingConfirmHint: ""
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
    property real positionU: 0
    property real positionV: 0
    property real positionW: 0
    property bool fiveAxisAvailable: false
    property bool acceleratorLevelAvailable: false
    property bool zTiltAvailable: false
    property string homedAxes: ""
    property string klippyState: "disconnected"
    property string webhooksState: ""
    property string controlStatus: ""
    property string controlError: ""
    readonly property color selectedAccent: "#7f9298"
    readonly property int moveButtonSize: Math.max(
        72,
        Math.min(
            root.metrics.ultraWide ? 104 : 96,
            Math.round(Math.min(root.width, root.height) * (root.metrics.ultraWide ? 0.2 : 0.17))
        )
    )
    readonly property int moveHomeSize: Math.max(72, Math.round(root.moveButtonSize * 0.98))
    readonly property int moveActionIconSize: Math.max(30, Math.round(root.moveButtonSize * 0.42))
    readonly property real motionSectionGap: Math.max(root.metrics.gap, Math.round(root.metrics.fontSize * 0.85))
    signal moveActionRequested(string action, real distance, real speed)

    function selectDistance(distance) {
        root.selectedDistance = distance
    }

    function selectTiltDistance(distance) {
        root.selectedTiltDistance = distance
    }

    function fittedMoveButtonSize(padWidth, padHeight) {
        var sizeCap = Math.floor(padHeight / 3.08)
        var widthCap = Math.floor(padWidth * 0.46)
        return Math.max(44, Math.min(root.moveButtonSize, sizeCap, widthCap))
    }

    function fiveAxisActionVisible(action) {
        if (action.requires === "five_axis") {
            return root.fiveAxisAvailable
        }
        if (action.requires === "accelerator_level") {
            return root.acceleratorLevelAvailable
        }
        if (action.requires === "z_tilt") {
            return root.zTiltAvailable
        }
        return true
    }

    function visibleActionButtons() {
        var actions = []
        var moreAction = null
        for (var index = 0; index < root.actionButtons.length; index += 1) {
            var action = root.actionButtons[index]
            if (action.action === "more") {
                moreAction = action
                continue
            }
            if (root.fiveAxisActionVisible(action)) {
                actions.push(action)
            }
        }
        if (moreAction !== null) {
            var columns = root.actionButtonColumns()
            if (columns > 1 && actions.length % columns === 0) {
                actions.push({"placeholder": true})
            }
            actions.push(moreAction)
        }
        return actions
    }

    function actionButtonColumns() {
        return root.metrics.portrait || root.fiveAxisAvailable ? 2 : 1
    }

    function visibleMoreActions() {
        var actions = []
        for (var index = 0; index < root.moreActions.length; index += 1) {
            if (root.fiveAxisActionVisible(root.moreActions[index])) {
                actions.push(root.moreActions[index])
            }
        }
        return actions
    }

    function actionNeedsConfirmation(action) {
        return action === "accelerator_level" || action === "z_tilt_adjust"
    }

    function actionLabel(action) {
        var actions = root.moreActions.concat(root.actionButtons)
        for (var index = 0; index < actions.length; index += 1) {
            if (actions[index].action === action) {
                return actions[index].label
            }
        }
        return "Action"
    }

    function requestConfirmedAction(action) {
        if (root.actionNeedsConfirmation(action)) {
            root.pendingConfirmAction = action
            root.pendingConfirmTitle = root.actionLabel(action)
            root.pendingConfirmHint = action === "accelerator_level"
                ? "This will run accelerometer leveling with movement enabled."
                : "This will run Z tilt adjustment."
            root.confirmVisible = true
            return
        }
        root.moveActionRequested(action, 0, 0)
    }

    function confirmPendingAction() {
        if (root.pendingConfirmAction.length <= 0) {
            root.confirmVisible = false
            return
        }
        var action = root.pendingConfirmAction
        root.pendingConfirmAction = ""
        root.confirmVisible = false
        root.moveActionRequested(action, 0, 0)
    }

    function dismissConfirmAction() {
        root.pendingConfirmAction = ""
        root.confirmVisible = false
    }

    function positionItems() {
        var items = [
            {"label": "X", "value": root.positionX.toFixed(2)},
            {"label": "Y", "value": root.positionY.toFixed(2)},
            {"label": "Z", "value": root.positionZ.toFixed(2)},
            {"label": "E", "value": root.positionE.toFixed(2)}
        ]
        if (root.fiveAxisAvailable) {
            items.push({"label": "U", "value": root.positionU.toFixed(2)})
            items.push({"label": "V", "value": root.positionV.toFixed(2)})
            items.push({"label": "W", "value": root.positionW.toFixed(2)})
        }
        return items
    }

    function showMore() {
        if (root.metrics.ultraWide) {
            root.moreVisible = !root.moreVisible
            return
        }
        root.detailPage = "more"
    }

    function showBedTilt() {
        root.moreVisible = false
        root.detailPage = "bed_tilt"
    }

    function bedHeightOffset(value) {
        var average = (root.positionU + root.positionV + root.positionW) / 3
        return Math.max(-18, Math.min(18, (value - average) * 2.4))
    }

    function bedCornerPoints(previewWidth, previewHeight) {
        var marginX = Math.max(16, Math.round(previewWidth * 0.13))
        var nearY = Math.round(previewHeight * 0.76)
        var farY = Math.round(previewHeight * 0.25)
        var nearLeftX = marginX
        var nearRightX = previewWidth - marginX
        var farLeftX = Math.round(previewWidth * 0.29)
        var farRightX = Math.round(previewWidth * 0.71)
        var farMidX = Math.round((farLeftX + farRightX) / 2)
        var heights = {
            nearLeft: root.positionU,
            nearRight: root.positionW,
            farMid: root.positionV
        }
        return {
            nearLeft: {"x": nearLeftX, "y": nearY + root.bedHeightOffset(heights.nearLeft)},
            nearRight: {"x": nearRightX, "y": nearY + root.bedHeightOffset(heights.nearRight)},
            farMid: {"x": farMidX, "y": farY + root.bedHeightOffset(heights.farMid)},
            farLeft: {"x": farLeftX, "y": farY + root.bedHeightOffset(heights.farMid)},
            farRight: {"x": farRightX, "y": farY + root.bedHeightOffset(heights.farMid)},
            baselineNearLeft: {"x": nearLeftX, "y": nearY},
            baselineNearRight: {"x": nearRightX, "y": nearY},
            baselineFarLeft: {"x": farLeftX, "y": farY},
            baselineFarRight: {"x": farRightX, "y": farY},
            baselineFarMid: {"x": farMidX, "y": farY}
        }
    }

    function goBack() {
        if (root.detailPage !== "main") {
            root.detailPage = "main"
            return true
        }
        return false
    }

    function handleMoreAction(action) {
        if (!root.actionAllowed(action)) {
            return
        }
        if (action === "speed_xy") {
            root.cycleSpeed("xy")
            return
        }
        if (action === "speed_z") {
            root.cycleSpeed("z")
            return
        }
        if (action === "bed_tilt") {
            root.showBedTilt()
            return
        }
        if (action === "home_all" || action === "home_uvw"
                || action === "z_tilt_adjust" || action === "accelerator_level"
                || action === "disable_motors") {
            root.requestConfirmedAction(action)
            return
        }
        root.moveActionRequested("placeholder_" + action, 0, 0)
    }

    function speedForAction(action) {
        if (root.tiltAction(action)) {
            return parseFloat(root.selectedTiltSpeed)
        }
        if (root.actionAxis(action) === "z") {
            return parseFloat(root.selectedZSpeed)
        }
        return parseFloat(root.selectedXYSpeed)
    }

    function cycleSpeed(kind) {
        var values = kind === "z" ? root.zSpeeds : root.xySpeeds
        var selected = kind === "z" ? root.selectedZSpeed : root.selectedXYSpeed
        var index = values.indexOf(selected)
        var nextValue = values[(index + 1) % values.length]
        if (kind === "z") {
            root.selectedZSpeed = nextValue
            return
        }
        root.selectedXYSpeed = nextValue
    }

    function moreActionHint(action, fallback) {
        if (action === "speed_xy") {
            return root.selectedXYSpeed + " mm/s"
        }
        if (action === "speed_z") {
            return root.selectedZSpeed + " mm/s"
        }
        return fallback
    }

    function actionHint(action, fallback) {
        var reason = root.actionUnavailableReason(action)
        return reason.length > 0 ? reason : fallback
    }

    function printerReady() {
        return root.klippyState === "ready"
            && (root.webhooksState.length <= 0 || root.webhooksState === "ready")
    }

    function movementGuardText() {
        if (root.printerReady()) {
            return "Home axis first"
        }
        return "Printer not ready"
    }

    function actionAxis(action) {
        if (action === "x_minus" || action === "x_plus") {
            return "x"
        }
        if (action === "y_minus" || action === "y_plus") {
            return "y"
        }
        if (action === "z_minus" || action === "z_plus") {
            return "z"
        }
        if (action === "u_minus" || action === "u_plus") {
            return "u"
        }
        if (action === "v_minus" || action === "v_plus") {
            return "v"
        }
        if (action === "w_minus" || action === "w_plus") {
            return "w"
        }
        return ""
    }

    function tiltAction(action) {
        return action === "u_minus" || action === "u_plus"
            || action === "v_minus" || action === "v_plus"
            || action === "w_minus" || action === "w_plus"
    }

    function axisHomed(axis) {
        return axis.length <= 0 || root.homedAxes.indexOf(axis) >= 0
    }

    function unhomedMoveAxesText() {
        var axes = []
        if (!root.axisHomed("x")) {
            axes.push("X")
        }
        if (!root.axisHomed("y")) {
            axes.push("Y")
        }
        if (!root.axisHomed("z")) {
            axes.push("Z")
        }
        return axes.join("/")
    }

    function jogAction(action) {
        return root.actionAxis(action).length > 0 && !root.tiltAction(action)
    }

    function actionRequiresReady(action) {
        return action === "disable_motors"
            || action === "home_all"
            || action === "home_xy"
            || action === "home_z"
            || action === "home_uvw"
            || action === "z_tilt_adjust"
            || action === "accelerator_level"
            || action === "x_minus"
            || action === "x_plus"
            || action === "y_minus"
            || action === "y_plus"
            || action === "z_minus"
            || action === "z_plus"
            || action === "u_minus"
            || action === "u_plus"
            || action === "v_minus"
            || action === "v_plus"
            || action === "w_minus"
            || action === "w_plus"
    }

    function actionAllowed(action) {
        return root.actionUnavailableReason(action).length <= 0
    }

    function actionUnavailableReason(action) {
        if (!root.actionRequiresReady(action)) {
            return ""
        }
        if (!root.printerReady()) {
            return "Printer not ready"
        }
        if ((action === "home_uvw" || root.tiltAction(action)) && !root.fiveAxisAvailable) {
            return "Five-axis controls unavailable"
        }
        if (action === "accelerator_level" && !root.acceleratorLevelAvailable) {
            return "Accelerator leveling unavailable"
        }
        if (action === "z_tilt_adjust" && !root.zTiltAvailable) {
            return "Z tilt unavailable"
        }
        if (root.jogAction(action) && !root.axisHomed(root.actionAxis(action))) {
            var axis = root.actionAxis(action)
            return "Home " + axis.toUpperCase() + " first"
        }
        return ""
    }

    function controlFeedbackText() {
        if (root.controlError.length > 0) {
            return root.controlError
        }
        if (root.controlStatus.length > 0) {
            return root.controlStatus
        }
        if (!root.printerReady()) {
            return root.movementGuardText()
        }
        var axes = root.unhomedMoveAxesText()
        if (axes.length > 0) {
            return "Home " + axes + " first"
        }
        return "Controls ready"
    }

    function controlFeedbackColor() {
        if (root.controlError.length > 0) {
            return "#ff7777"
        }
        if (root.controlStatus.length > 0) {
            return "#d8dee0"
        }
        return Theme.mutedText
    }

    function arrowGlyph(direction) {
        if (direction === "up") {
            return "▲"
        }
        if (direction === "down") {
            return "▼"
        }
        if (direction === "left") {
            return "◀"
        }
        return "▶"
    }

    component LockedTile: Rectangle {
        id: tileRoot
        property string title: ""
        property string hint: "locked"
        property string iconName: ""
        property bool selected: false
        property bool pressed: false

        color: tileRoot.pressed && tileRoot.enabled ? "#182528" : selected ? "#1b2b2e" : "#101718"
        scale: tileRoot.pressed && tileRoot.enabled ? 0.97 : 1.0
        opacity: tileRoot.enabled ? selected ? 1.0 : 0.9 : 0.46
        border.color: tileRoot.pressed && tileRoot.enabled ? Theme.text : selected ? root.selectedAccent : "#48565a"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.18)
        Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
        Behavior on color { ColorAnimation { duration: 80 } }
        Behavior on border.color { ColorAnimation { duration: 80 } }

        Rectangle {
            id: tileDepth
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Math.max(2, Math.round(root.metrics.fontSize * 0.18))
            visible: !tileRoot.pressed && tileRoot.enabled
            color: "#050808"
            opacity: 0.8
            radius: parent.radius
        }

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(4, Math.round(root.metrics.fontSize * 0.22))
            color: "transparent"
            border.color: "#263235"
            border.width: 1
            radius: Math.round(parent.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Image {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: Math.max(19, Math.round(root.metrics.fontSize * 1.42))
                Layout.preferredHeight: tileRoot.iconName.length > 0
                    ? Math.max(19, Math.round(root.metrics.fontSize * 1.42))
                    : 0
                visible: tileRoot.iconName.length > 0
                source: tileRoot.iconName.length > 0 ? Theme.iconSource(tileRoot.iconName) : ""
                sourceSize.width: Layout.preferredWidth
                sourceSize.height: Layout.preferredHeight
                fillMode: Image.PreserveAspectFit
                opacity: tileRoot.enabled ? 1.0 : 0.55
            }

            Label {
                Layout.fillWidth: true
                color: tileRoot.selected ? Theme.text : Theme.text
                text: tileRoot.title
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.bold: tileRoot.selected
                font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.05))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: tileRoot.hint
                visible: tileRoot.hint.length > 0
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.58))
            }
        }
    }

    component DirectionButton: Rectangle {
        id: directionRoot
        property string title: ""
        property string direction: "up"
        property bool pressed: false

        color: directionRoot.pressed && directionRoot.enabled ? "#182528" : "#101718"
        scale: directionRoot.pressed && directionRoot.enabled ? 0.96 : 1.0
        opacity: directionRoot.enabled ? 1.0 : 0.46
        border.color: directionRoot.pressed && directionRoot.enabled ? Theme.text : "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.18)
        Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
        Behavior on color { ColorAnimation { duration: 80 } }
        Behavior on border.color { ColorAnimation { duration: 80 } }

        Rectangle {
            id: directionDepth
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Math.max(2, Math.round(root.metrics.fontSize * 0.18))
            visible: !directionRoot.pressed && directionRoot.enabled
            color: "#050808"
            opacity: 0.8
            radius: parent.radius
        }

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(4, Math.round(root.metrics.fontSize * 0.22))
            color: "transparent"
            border.color: "#263235"
            border.width: 1
            radius: Math.round(directionRoot.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                text: root.arrowGlyph(directionRoot.direction)
                color: "#d9e0e2"
                font.pixelSize: Math.max(22, Math.round(root.metrics.fontSize * 1.56))
                horizontalAlignment: Text.AlignHCenter
            }

            Label {
                Layout.fillWidth: true
                text: directionRoot.title
                color: Theme.text
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.7))
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                wrapMode: Text.NoWrap
            }
        }
    }

    component ActionIconButton: Rectangle {
        id: actionRoot
        property string title: ""
        property string hint: ""
        property string iconName: ""
        property bool selected: false
        property bool pressed: false

        color: actionRoot.pressed && actionRoot.enabled ? "#182528" : selected ? "#1b2b2e" : "#101718"
        scale: actionRoot.pressed && actionRoot.enabled ? 0.97 : 1.0
        opacity: actionRoot.enabled ? 1.0 : 0.46
        border.color: actionRoot.pressed && actionRoot.enabled ? Theme.text : selected ? root.selectedAccent : "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.18)
        Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
        Behavior on color { ColorAnimation { duration: 80 } }
        Behavior on border.color { ColorAnimation { duration: 80 } }

        Rectangle {
            id: actionDepth
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Math.max(2, Math.round(root.metrics.fontSize * 0.18))
            visible: !actionRoot.pressed && actionRoot.enabled
            color: "#050808"
            opacity: 0.8
            radius: parent.radius
        }

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(4, Math.round(root.metrics.fontSize * 0.22))
            color: "transparent"
            border.color: "#263235"
            border.width: 1
            radius: Math.round(parent.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Image {
                Layout.fillWidth: true
                Layout.preferredHeight: root.moveActionIconSize
                source: Theme.iconSource(actionRoot.iconName)
                sourceSize.width: root.moveActionIconSize
                sourceSize.height: root.moveActionIconSize
                fillMode: Image.PreserveAspectFit
                opacity: actionRoot.enabled ? 1.0 : 0.6
            }

            Label {
                Layout.fillWidth: true
                text: actionRoot.title
                color: Theme.text
                font.bold: true
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            Label {
                Layout.fillWidth: true
                text: actionRoot.hint
                color: Theme.mutedText
                font.pixelSize: Math.max(8, Math.round(root.metrics.fontSize * 0.5))
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
        }
    }

    component TiltPointControl: Rectangle {
        id: tiltRoot
        property string title: ""
        property string value: "0.00"
        property string plusAction: ""
        property string minusAction: ""
        property bool pressed: false

        color: tiltRoot.pressed && tiltRoot.enabled ? "#182528" : "#101718"
        scale: tiltRoot.pressed && tiltRoot.enabled ? 0.97 : 1.0
        opacity: tiltRoot.enabled ? 1.0 : 0.46
        border.color: tiltRoot.pressed && tiltRoot.enabled ? Theme.text : "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.14)
        Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
        Behavior on color { ColorAnimation { duration: 80 } }
        Behavior on border.color { ColorAnimation { duration: 80 } }

        Rectangle {
            id: tiltDepth
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Math.max(2, Math.round(root.metrics.fontSize * 0.18))
            visible: !tiltRoot.pressed && tiltRoot.enabled
            color: "#050808"
            opacity: 0.8
            radius: parent.radius
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.portrait
                ? Math.max(6, Math.round(root.metrics.gap * 0.7))
                : Math.max(3, Math.round(root.metrics.gap * 0.32))
            spacing: root.metrics.portrait
                ? Math.max(5, Math.round(root.metrics.gap * 0.55))
                : Math.max(2, Math.round(root.metrics.gap * 0.22))

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: root.metrics.portrait
                    ? Math.max(42, Math.round(root.metrics.fontSize * 2.4))
                    : Math.max(25, Math.round(root.metrics.fontSize * 1.42))
                color: "#172224"
                border.color: "#344044"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.22)

                Label {
                    anchors.centerIn: parent
                    text: tiltRoot.title + "+"
                    color: Theme.text
                    font.bold: true
                    font.pixelSize: root.metrics.portrait
                        ? Math.max(18, Math.round(root.metrics.fontSize * 1.25))
                        : Math.max(15, Math.round(root.metrics.fontSize * 0.9))
                }

                MouseArea {
                    anchors.fill: parent
                    enabled: root.actionAllowed(tiltRoot.plusAction)
                    onPressedChanged: tiltRoot.pressed = pressed
                    onClicked: root.moveActionRequested(
                        tiltRoot.plusAction,
                        parseFloat(root.selectedTiltDistance),
                        root.speedForAction(tiltRoot.plusAction)
                    )
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: root.metrics.portrait
                    ? Math.max(34, Math.round(root.metrics.fontSize * 2.1))
                    : Math.max(24, Math.round(root.metrics.fontSize * 1.42))
                color: "#0b1112"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.18)

                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - root.metrics.gap
                    spacing: 0

                    Label {
                        Layout.fillWidth: true
                        text: tiltRoot.title
                        color: Theme.text
                        horizontalAlignment: Text.AlignHCenter
                        font.bold: true
                        font.pixelSize: root.metrics.portrait
                            ? Math.max(15, Math.round(root.metrics.fontSize * 1.0))
                            : Math.max(13, Math.round(root.metrics.fontSize * 0.78))
                    }

                    Label {
                        Layout.fillWidth: true
                        text: tiltRoot.value
                        color: Theme.mutedText
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: root.metrics.portrait
                            ? Math.max(11, Math.round(root.metrics.fontSize * 0.72))
                            : Math.max(8, Math.round(root.metrics.fontSize * 0.52))
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: root.metrics.portrait
                    ? Math.max(42, Math.round(root.metrics.fontSize * 2.4))
                    : Math.max(25, Math.round(root.metrics.fontSize * 1.42))
                color: "#172224"
                border.color: "#344044"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.22)

                Label {
                    anchors.centerIn: parent
                    text: tiltRoot.title + "-"
                    color: Theme.text
                    font.bold: true
                    font.pixelSize: root.metrics.portrait
                        ? Math.max(18, Math.round(root.metrics.fontSize * 1.25))
                        : Math.max(15, Math.round(root.metrics.fontSize * 0.9))
                }

                MouseArea {
                    anchors.fill: parent
                    enabled: root.actionAllowed(tiltRoot.minusAction)
                    onPressedChanged: tiltRoot.pressed = pressed
                    onClicked: root.moveActionRequested(
                        tiltRoot.minusAction,
                        parseFloat(root.selectedTiltDistance),
                        root.speedForAction(tiltRoot.minusAction)
                    )
                }
            }
        }
    }

    GridLayout {
        visible: root.detailPage === "main" || root.metrics.ultraWide
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        columns: root.metrics.ultraWide ? 3 : 1
        rows: root.metrics.ultraWide ? 1 : 3
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap

        Rectangle {
            id: controlGroupGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.ultraWide ? Math.round(root.width * 0.48) : -1
            color: Theme.buttonsBg
            border.color: "#465456"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.45)

            Item {
                id: motionPad
                anchors.fill: parent
                anchors.margins: root.metrics.gap

                Item {
                    id: xyMovePad
                    width: root.metrics.portrait ? parent.width : Math.round(parent.width * 0.42)
                    height: root.metrics.portrait ? Math.round(parent.height * 0.48) : parent.height
                    anchors.left: parent.left
                    anchors.top: parent.top
                    property int padSize: Math.max(58, Math.min(width, height))
                    property int arrowSize: root.fittedMoveButtonSize(width, height)
                    property int homeSize: Math.min(root.moveHomeSize, arrowSize)

                    Repeater {
                        model: root.xyButtons

                        DirectionButton {
                            required property var modelData
                            width: xyMovePad.arrowSize
                            height: xyMovePad.arrowSize
                            title: modelData.label
                            direction: modelData.direction
                            enabled: root.actionAllowed(modelData.action)
                            anchors.horizontalCenter: modelData.direction === "up" || modelData.direction === "down" ? parent.horizontalCenter : undefined
                            anchors.verticalCenter: modelData.direction === "left" || modelData.direction === "right" ? parent.verticalCenter : undefined
                            anchors.top: modelData.direction === "up" ? parent.top : undefined
                            anchors.bottom: modelData.direction === "down" ? parent.bottom : undefined
                            anchors.left: modelData.direction === "left" ? parent.left : undefined
                            anchors.right: modelData.direction === "right" ? parent.right : undefined

                            MouseArea {
                                anchors.fill: parent
                                enabled: root.actionAllowed(modelData.action)
                                onPressedChanged: parent.pressed = pressed
                                onClicked: root.moveActionRequested(modelData.action, parseFloat(root.selectedDistance), root.speedForAction(modelData.action))
                            }
                        }
                    }

                    LockedTile {
                        width: xyMovePad.homeSize
                        height: xyMovePad.homeSize
                        anchors.centerIn: parent
                        title: "XY"
                        hint: "home"
                        iconName: "home"
                        enabled: root.actionAllowed("home_xy")

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.actionAllowed("home_xy")
                            onPressedChanged: parent.pressed = pressed
                            onClicked: root.moveActionRequested("home_xy", 0, 0)
                        }
                    }
                }

                Item {
                    id: zMovePad
                    width: root.metrics.portrait ? Math.round(parent.width * 0.46) : Math.round(parent.width * 0.22)
                    height: root.metrics.portrait ? Math.round(parent.height * 0.46) : parent.height
                    anchors.right: undefined
                    anchors.horizontalCenter: undefined
                    anchors.leftMargin: root.metrics.portrait ? 0 : root.metrics.gap
                    anchors.top: root.metrics.portrait ? xyMovePad.bottom : parent.top
                    anchors.topMargin: root.metrics.portrait ? root.metrics.gap : 0
                    anchors.left: root.metrics.portrait ? parent.left : xyMovePad.right
                    property int padSize: Math.max(58, Math.min(width, height))
                    property int arrowSize: root.fittedMoveButtonSize(width, height)
                    property int homeSize: Math.min(root.moveHomeSize, arrowSize)

                    DirectionButton {
                        width: zMovePad.arrowSize
                        height: zMovePad.arrowSize
                        title: "Z+"
                        direction: "up"
                        enabled: root.actionAllowed("z_plus")
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.actionAllowed("z_plus")
                            onPressedChanged: parent.pressed = pressed
                            onClicked: root.moveActionRequested(
                                "z_plus",
                                parseFloat(root.selectedDistance),
                                root.speedForAction("z_plus")
                            )
                        }
                    }

                    LockedTile {
                        width: zMovePad.homeSize
                        height: zMovePad.homeSize
                        anchors.centerIn: parent
                        title: "Z"
                        hint: "home"
                        iconName: "home"
                        enabled: root.actionAllowed("home_z")

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.actionAllowed("home_z")
                            onPressedChanged: parent.pressed = pressed
                            onClicked: root.moveActionRequested("home_z", 0, 0)
                        }
                    }

                    DirectionButton {
                        width: zMovePad.arrowSize
                        height: zMovePad.arrowSize
                        title: "Z-"
                        direction: "down"
                        enabled: root.actionAllowed("z_minus")
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.actionAllowed("z_minus")
                            onPressedChanged: parent.pressed = pressed
                            onClicked: root.moveActionRequested(
                                "z_minus",
                                parseFloat(root.selectedDistance),
                                root.speedForAction("z_minus")
                            )
                        }
                    }
                }

                GridLayout {
                    id: motionActions
                    width: root.metrics.portrait
                        ? Math.round(parent.width * 0.50)
                        : Math.max(
                            Math.round(parent.width * (root.fiveAxisAvailable ? 0.32 : 0.24)),
                            Math.round(root.moveButtonSize * (root.fiveAxisAvailable ? 3.2 : 2.2))
                        )
                    height: root.metrics.portrait
                        ? Math.max(root.moveButtonSize, Math.round(root.moveButtonSize * (root.fiveAxisAvailable ? 2.05 : 1.62)))
                        : Math.max(
                            Math.round(root.moveButtonSize * (root.fiveAxisAvailable ? 2.05 : 2.15)),
                            Math.round(parent.height * 0.58)
                        )
                    y: root.metrics.portrait ? zMovePad.y : Math.round((parent.height - height) / 2)
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    columns: root.actionButtonColumns()
                    rows: Math.ceil(root.visibleActionButtons().length / columns)
                    rowSpacing: root.motionSectionGap
                    columnSpacing: root.motionSectionGap

                    Repeater {
                        model: root.visibleActionButtons()

                        Item {
                            required property var modelData

                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            ActionIconButton {
                                anchors.fill: parent
                                visible: !modelData.placeholder
                                title: modelData.placeholder ? "" : modelData.label
                                hint: modelData.placeholder
                                    ? ""
                                    : root.actionHint(modelData.action, modelData.hint)
                                iconName: modelData.placeholder ? "" : modelData.iconName
                                enabled: !modelData.placeholder && root.actionAllowed(modelData.action)
                                selected: !modelData.placeholder
                                    && modelData.action === "more"
                                    && (root.moreVisible || root.detailPage === "more")

                                MouseArea {
                                    anchors.fill: parent
                                    enabled: !modelData.placeholder && root.actionAllowed(modelData.action)
                                    onPressedChanged: parent.pressed = pressed
                                    onClicked: {
                                        if (modelData.action === "bed_tilt") {
                                            root.showBedTilt()
                                        } else if (modelData.action === "more") {
                                            root.showMore()
                                        } else {
                                            root.requestConfirmedAction(modelData.action)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            id: positionPanel
            Layout.fillWidth: true
            Layout.fillHeight: root.metrics.ultraWide
            Layout.preferredWidth: root.metrics.ultraWide ? Math.round(root.width * 0.27) : -1
            Layout.preferredHeight: root.metrics.ultraWide
                ? -1
                : root.moreVisible
                    ? Math.max(118, Math.round(root.metrics.fontSize * 7.2))
                    : root.fiveAxisAvailable
                        ? Math.max(122, Math.round(root.metrics.fontSize * 7.4))
                        : Math.max(82, Math.round(root.metrics.fontSize * 5.1))
            color: "#0d1415"
            border.color: "#344044"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: Math.max(5, Math.round(root.metrics.gap * 0.55))

                RowLayout {
                    Layout.fillWidth: true
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Position"
                        font.bold: true
                        font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.02))
                    }

                    Label {
                        id: moveControlFeedbackLabel
                        Layout.maximumWidth: Math.max(120, Math.round(positionPanel.width * 0.52))
                        color: root.controlFeedbackColor()
                        text: root.controlFeedbackText()
                        elide: Text.ElideRight
                        maximumLineCount: 1
                        wrapMode: Text.NoWrap
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                    }
                }

                Rectangle {
                    id: moveMorePanel
                    Layout.fillWidth: true
                    Layout.preferredHeight: root.moreVisible
                        ? Math.max(46, Math.round(root.metrics.fontSize * 2.9))
                        : 0
                    visible: root.moreVisible && root.metrics.ultraWide
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.22)

                    GridLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(5, Math.round(root.metrics.gap * 0.5))
                        columns: root.metrics.ultraWide ? 1 : 5
                        columnSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                        rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))

                        Repeater {
                            model: root.visibleMoreActions()

                            Rectangle {
                                required property var modelData
                                property bool pressed: false
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: pressed && root.actionAllowed(modelData.action) ? "#182528" : "#0b1112"
                                scale: pressed && root.actionAllowed(modelData.action) ? 0.97 : 1.0
                                opacity: root.actionAllowed(modelData.action) ? 1.0 : 0.46
                                border.color: pressed && root.actionAllowed(modelData.action) ? Theme.text : "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.18)
                                Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
                                Behavior on color { ColorAnimation { duration: 80 } }
                                Behavior on border.color { ColorAnimation { duration: 80 } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    spacing: 4

                                    Image {
                                        Layout.preferredWidth: Math.max(14, Math.round(root.metrics.fontSize * 0.9))
                                        Layout.preferredHeight: Math.max(14, Math.round(root.metrics.fontSize * 0.9))
                                        source: Theme.iconSource(modelData.iconName)
                                        sourceSize.width: Layout.preferredWidth
                                        sourceSize.height: Layout.preferredHeight
                                        fillMode: Image.PreserveAspectFit
                                        opacity: root.actionAllowed(modelData.action) ? 0.9 : 0.5
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.mutedText
                                        text: modelData.label
                                        horizontalAlignment: Text.AlignLeft
                                        verticalAlignment: Text.AlignVCenter
                                        elide: Text.ElideRight
                                        font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.62))
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    enabled: root.actionAllowed(modelData.action)
                                    onPressedChanged: parent.pressed = pressed
                                    onClicked: root.handleMoreAction(modelData.action)
                                }
                            }
                        }
                    }
                }

                GridLayout {
                    id: positionGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: root.metrics.ultraWide
                    columns: root.metrics.ultraWide ? 1 : root.fiveAxisAvailable ? 4 : 4
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.fontSize * 0.35))

                    Repeater {
                        model: root.positionItems()

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: root.metrics.ultraWide
                            Layout.preferredHeight: Math.max(28, Math.round(root.metrics.fontSize * 1.85))
                            color: "#101617"
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.18)

                            Label {
                                anchors.centerIn: parent
                                color: Theme.text
                                text: modelData.label + " " + modelData.value
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                            }
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: root.homedAxes.length > 0 ? "Homed: " + root.homedAxes : "Homed: unknown"
                    elide: Text.ElideRight
                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                }
            }
        }

        Rectangle {
            id: distancePanel
            Layout.fillWidth: true
            Layout.fillHeight: root.metrics.ultraWide
            Layout.preferredWidth: root.metrics.ultraWide ? Math.round(root.width * 0.22) : -1
            Layout.preferredHeight: root.metrics.ultraWide ? -1 : Math.max(70, Math.round(root.metrics.fontSize * 4.2))
            color: "#0d1415"
            border.color: "#344044"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: Math.max(5, Math.round(root.metrics.gap * 0.55))

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Distance"
                    font.bold: true
                    font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.02))
                }

                GridLayout {
                    id: distanceGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: root.metrics.ultraWide
                    Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 1.9))
                    columns: root.metrics.ultraWide ? 1 : 7
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))

                    Repeater {
                        model: root.distances

                        LockedTile {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(30, Math.round(root.metrics.fontSize * 1.9))
                            title: modelData
                            hint: "mm"
                            selected: root.selectedDistance === modelData

                            MouseArea {
                                anchors.fill: parent
                                onPressedChanged: parent.pressed = pressed
                                onClicked: root.selectDistance(modelData)
                            }
                        }
                    }

                    Repeater {
                        model: root.metrics.portrait ? root.portraitPlaceholders : []

                        Rectangle {
                            required property var modelData
                            property bool placeholder: modelData.placeholder
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            visible: false
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: moveMorePage
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        visible: root.detailPage === "more" && !root.metrics.ultraWide
        color: "#0d1415"
        border.color: "#344044"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.36)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Move Settings"
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: root.visibleMoreActions()

                    Rectangle {
                        required property var modelData
                        property bool pressed: false
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.2))
                        color: pressed && root.actionAllowed(modelData.action) ? "#182528" : "#101617"
                        scale: pressed && root.actionAllowed(modelData.action) ? 0.97 : 1.0
                        opacity: root.actionAllowed(modelData.action) ? 1.0 : 0.46
                        border.color: pressed && root.actionAllowed(modelData.action) ? Theme.text : "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.28)
                        Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
                        Behavior on color { ColorAnimation { duration: 80 } }
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        ColumnLayout {
                            anchors.centerIn: parent
                            width: parent.width - root.metrics.gap
                            spacing: 0

                            Image {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: Math.max(28, Math.round(root.metrics.fontSize * 1.8))
                                Layout.preferredHeight: Math.max(28, Math.round(root.metrics.fontSize * 1.8))
                                source: Theme.iconSource(modelData.iconName)
                                sourceSize.width: Layout.preferredWidth
                                sourceSize.height: Layout.preferredHeight
                                fillMode: Image.PreserveAspectFit
                                opacity: root.actionAllowed(modelData.action) ? 1.0 : 0.55
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: modelData.label
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.9))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: root.actionHint(
                                    modelData.action,
                                    root.moreActionHint(modelData.action, modelData.hint)
                                )
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.62))
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.actionAllowed(modelData.action)
                            onPressedChanged: parent.pressed = pressed
                            onClicked: root.handleMoreAction(modelData.action)
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: bedTiltPage
        z: 20
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        visible: root.detailPage === "bed_tilt"
        color: "#0d1415"
        border.color: "#344044"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.36)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.portrait
                ? root.metrics.gap
                : Math.max(4, Math.round(root.metrics.gap * 0.42))

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: root.metrics.portrait
                    ? Math.max(24, Math.round(root.metrics.fontSize * 1.45))
                    : Math.max(22, Math.round(root.metrics.fontSize * 1.24))
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Bed Tilt"
                    font.bold: true
                    font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
                }

                Label {
                    color: Theme.mutedText
                    text: "UVW maps Z/Z1/Z2"
                    elide: Text.ElideRight
                    maximumLineCount: 1
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.72))
                }
            }

            Rectangle {
                id: bedTiltPreviewPanel
                Layout.fillWidth: true
                Layout.preferredHeight: root.metrics.portrait
                    ? Math.max(122, Math.round(root.metrics.fontSize * 7.2))
                    : Math.max(86, Math.round(root.metrics.fontSize * 5.1))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.2)

                Item {
                    anchors.fill: parent
                    anchors.margins: Math.max(5, Math.round(root.metrics.gap * 0.55))

                    Canvas {
                        id: bedRectCanvas
                        anchors.fill: parent
                        antialiasing: true

                        onWidthChanged: requestPaint()
                        onHeightChanged: requestPaint()
                        Component.onCompleted: requestPaint()

                        Connections {
                            target: root
                            function onPositionUChanged() { bedRectCanvas.requestPaint() }
                            function onPositionVChanged() { bedRectCanvas.requestPaint() }
                            function onPositionWChanged() { bedRectCanvas.requestPaint() }
                        }

                        function drawBaselineBed(ctx, points) {
                            ctx.save()
                            ctx.strokeStyle = "#324042"
                            ctx.lineWidth = 1
                            ctx.setLineDash([5, 5])
                            ctx.beginPath()
                            ctx.moveTo(points.baselineFarLeft.x, points.baselineFarLeft.y)
                            ctx.lineTo(points.baselineFarRight.x, points.baselineFarRight.y)
                            ctx.lineTo(points.baselineNearRight.x, points.baselineNearRight.y)
                            ctx.lineTo(points.baselineNearLeft.x, points.baselineNearLeft.y)
                            ctx.closePath()
                            ctx.stroke()
                            ctx.restore()
                        }

                        function drawCurrentBed(ctx, points) {
                            var gradient = ctx.createLinearGradient(0, points.farMid.y, 0, points.nearLeft.y)
                            gradient.addColorStop(0, "#263739")
                            gradient.addColorStop(1, "#172325")
                            ctx.save()
                            ctx.fillStyle = gradient
                            ctx.strokeStyle = "#8da0a4"
                            ctx.lineWidth = 2
                            ctx.setLineDash([])
                            ctx.beginPath()
                            ctx.moveTo(points.farLeft.x, points.farLeft.y)
                            ctx.lineTo(points.farRight.x, points.farRight.y)
                            ctx.lineTo(points.nearRight.x, points.nearRight.y)
                            ctx.lineTo(points.nearLeft.x, points.nearLeft.y)
                            ctx.closePath()
                            ctx.fill()
                            ctx.stroke()

                            ctx.strokeStyle = "#536568"
                            ctx.lineWidth = 1
                            ctx.beginPath()
                            ctx.moveTo(points.farMid.x, points.farMid.y)
                            ctx.lineTo(points.nearLeft.x, points.nearLeft.y)
                            ctx.moveTo(points.farMid.x, points.farMid.y)
                            ctx.lineTo(points.nearRight.x, points.nearRight.y)
                            ctx.stroke()
                            ctx.restore()
                        }

                        function drawBedPoint(ctx, point, label, value) {
                            var radius = Math.max(4, Math.round(root.metrics.fontSize * 0.34))
                            ctx.save()
                            ctx.fillStyle = "#d7dedf"
                            ctx.strokeStyle = "#111819"
                            ctx.lineWidth = 2
                            ctx.beginPath()
                            ctx.arc(point.x, point.y, radius, 0, Math.PI * 2)
                            ctx.fill()
                            ctx.stroke()

                            ctx.fillStyle = Theme.text
                            ctx.font = "700 " + Math.max(10, Math.round(root.metrics.fontSize * 0.72)) + "px sans-serif"
                            ctx.textAlign = "center"
                            ctx.textBaseline = "bottom"
                            ctx.fillText(label, point.x, point.y - radius - 2)

                            ctx.fillStyle = Theme.mutedText
                            ctx.font = Math.max(9, Math.round(root.metrics.fontSize * 0.58)) + "px sans-serif"
                            ctx.textBaseline = "top"
                            ctx.fillText(value.toFixed(2), point.x, point.y + radius + 2)
                            ctx.restore()
                        }

                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.reset()
                            var points = root.bedCornerPoints(width, height)
                            drawBaselineBed(ctx, points)
                            drawCurrentBed(ctx, points)
                            drawBedPoint(ctx, points.nearLeft, "U", root.positionU)
                            drawBedPoint(ctx, points.nearRight, "W", root.positionW)
                            drawBedPoint(ctx, points.farMid, "V", root.positionV)
                        }
                    }
                }
            }

            Rectangle {
                id: bedPositionStrip
                Layout.fillWidth: true
                Layout.preferredHeight: root.metrics.portrait
                    ? Math.max(30, Math.round(root.metrics.fontSize * 1.9))
                    : Math.max(24, Math.round(root.metrics.fontSize * 1.45))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.18)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Math.max(4, Math.round(root.metrics.gap * 0.4))
                    spacing: Math.max(4, Math.round(root.metrics.gap * 0.45))

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 4
                        columnSpacing: Math.max(4, Math.round(root.metrics.gap * 0.4))

                        Label {
                            Layout.fillWidth: true
                            text: "Z " + root.positionZ.toFixed(3)
                            color: Theme.text
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                        }

                        Label {
                            Layout.fillWidth: true
                            text: "U " + root.positionU.toFixed(3)
                            color: Theme.text
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                        }

                        Label {
                            Layout.fillWidth: true
                            text: "V " + root.positionV.toFixed(3)
                            color: Theme.text
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                        }

                        Label {
                            Layout.fillWidth: true
                            text: "W " + root.positionW.toFixed(3)
                            color: Theme.text
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                        }
                    }
                }
            }

            Item {
                id: uvwTiltPad
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: root.metrics.portrait
                    ? Math.max(190, Math.round(root.metrics.fontSize * 11.2))
                    : Math.max(124, Math.round(root.metrics.fontSize * 7.0))

                readonly property int cardWidth: Math.max(
                    root.metrics.portrait ? 112 : 100,
                    Math.min(
                        Math.round(width * (root.metrics.portrait ? 0.44 : 0.28)),
                        Math.round(root.metrics.fontSize * 8.5)
                    )
                )
                readonly property int cardHeight: Math.max(
                    root.metrics.portrait ? 142 : 96,
                    Math.min(
                        Math.round(height * (root.metrics.portrait ? 0.46 : 0.62)),
                        Math.round(root.metrics.fontSize * (root.metrics.portrait ? 9.4 : 5.85))
                    )
                )

                TiltPointControl {
                    width: uvwTiltPad.cardWidth
                    height: uvwTiltPad.cardHeight
                    title: "V"
                    value: root.positionV.toFixed(3)
                    plusAction: "v_plus"
                    minusAction: "v_minus"
                    enabled: root.fiveAxisAvailable
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                }

                TiltPointControl {
                    width: uvwTiltPad.cardWidth
                    height: uvwTiltPad.cardHeight
                    title: "U"
                    value: root.positionU.toFixed(3)
                    plusAction: "u_plus"
                    minusAction: "u_minus"
                    enabled: root.fiveAxisAvailable
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: root.metrics.portrait
                        ? root.metrics.gap
                        : root.metrics.gap
                }

                TiltPointControl {
                    width: uvwTiltPad.cardWidth
                    height: uvwTiltPad.cardHeight
                    title: "W"
                    value: root.positionW.toFixed(3)
                    plusAction: "w_plus"
                    minusAction: "w_minus"
                    enabled: root.fiveAxisAvailable
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: root.metrics.portrait
                        ? root.metrics.gap
                        : root.metrics.gap
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: root.metrics.portrait
                    ? Math.max(72, Math.round(root.metrics.fontSize * 4.6))
                    : Math.max(58, Math.round(root.metrics.fontSize * 3.55))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.26)

                GridLayout {
                    anchors.fill: parent
                    anchors.margins: Math.max(5, Math.round(root.metrics.gap * 0.55))
                    columns: root.metrics.portrait ? 3 : 6
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))

                    Repeater {
                        model: root.tiltDistances

                        LockedTile {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: root.metrics.portrait
                                ? Math.max(34, Math.round(root.metrics.fontSize * 2.05))
                                : Math.max(28, Math.round(root.metrics.fontSize * 1.65))
                            title: modelData
                            hint: "mm"
                            selected: root.selectedTiltDistance === modelData

                            MouseArea {
                                anchors.fill: parent
                                onPressedChanged: parent.pressed = pressed
                                onClicked: root.selectTiltDistance(modelData)
                            }
                        }
                    }

                    LockedTile {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: root.metrics.portrait
                            ? Math.max(34, Math.round(root.metrics.fontSize * 2.05))
                            : Math.max(28, Math.round(root.metrics.fontSize * 1.65))
                        title: root.selectedTiltSpeed
                        hint: "mm/s"
                        selected: false

                        MouseArea {
                            anchors.fill: parent
                            onPressedChanged: parent.pressed = pressed
                            onClicked: root.selectedTiltSpeed = root.selectedTiltSpeed === "2" ? "5" : "2"
                        }
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: root.metrics.portrait
                    ? Math.max(112, Math.round(root.metrics.fontSize * 6.9))
                    : Math.max(58, Math.round(root.metrics.fontSize * 3.55))
                Layout.minimumHeight: Layout.preferredHeight
                columns: 3
                columnSpacing: root.metrics.portrait
                    ? root.metrics.gap
                    : Math.max(5, Math.round(root.metrics.gap * 0.55))

                ActionIconButton {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: "UVW Home"
                    hint: root.actionHint("home_uvw", "UVW_HOME")
                    iconName: "tilt"
                    enabled: root.actionAllowed("home_uvw")

                    MouseArea {
                        anchors.fill: parent
                        enabled: root.actionAllowed("home_uvw")
                        onPressedChanged: parent.pressed = pressed
                        onClicked: root.requestConfirmedAction("home_uvw")
                    }
                }

                ActionIconButton {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: "Acc Level"
                    hint: root.actionHint("accelerator_level", "MOVE=1")
                    iconName: "tilt"
                    visible: root.acceleratorLevelAvailable
                    enabled: root.acceleratorLevelAvailable && root.actionAllowed("accelerator_level")

                    MouseArea {
                        anchors.fill: parent
                        enabled: root.actionAllowed("accelerator_level")
                        onPressedChanged: parent.pressed = pressed
                        onClicked: root.requestConfirmedAction("accelerator_level")
                    }
                }

                ActionIconButton {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: "Z Tilt"
                    hint: root.actionHint("z_tilt_adjust", "adjust")
                    iconName: "tilt"
                    visible: root.zTiltAvailable
                    enabled: root.zTiltAvailable && root.actionAllowed("z_tilt_adjust")

                    MouseArea {
                        anchors.fill: parent
                        enabled: root.actionAllowed("z_tilt_adjust")
                        onPressedChanged: parent.pressed = pressed
                        onClicked: root.requestConfirmedAction("z_tilt_adjust")
                    }
                }
            }
        }
    }

    Rectangle {
        id: moveConfirmOverlay
        visible: root.confirmVisible
        z: 50
        anchors.fill: parent
        color: "#99000000"

        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width - root.metrics.margin * 2, Math.max(320, Math.round(parent.width * 0.48)))
            height: Math.min(parent.height - root.metrics.margin * 2, Math.max(190, Math.round(root.metrics.fontSize * 12.0)))
            color: "#101718"
            border.color: "#536165"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.45)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: root.pendingConfirmTitle
                    horizontalAlignment: Text.AlignHCenter
                    font.bold: true
                    font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
                    elide: Text.ElideRight
                }

                Label {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Theme.mutedText
                    text: root.pendingConfirmHint
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.WordWrap
                    font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.88))
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(46, Math.round(root.metrics.fontSize * 3.0))
                    spacing: root.metrics.gap

                    TactileButton {
                        id: cancelConfirmButton
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        text: "Cancel"
                        iconName: "cancel"
                        fontSize: root.metrics.fontSize
                        baseColor: "#0b1112"
                        pressedColor: "#182528"
                        accentColor: "#536165"
                        font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.9))
                        onClicked: root.dismissConfirmAction()
                    }

                    TactileButton {
                        id: confirmActionButton
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        text: "Confirm"
                        iconName: "confirm"
                        fontSize: root.metrics.fontSize
                        baseColor: "#1b2b2e"
                        pressedColor: "#24383c"
                        accentColor: root.selectedAccent
                        font.bold: true
                        font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.9))
                        onClicked: root.confirmPendingAction()
                    }
                }
            }
        }
    }
}
