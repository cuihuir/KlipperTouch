import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
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
    property var actionButtons: [
        {"label": "Disable Motors", "action": "disable_motors", "hint": "M84", "iconName": "motor-off"},
        {"label": "More", "action": "more", "hint": "settings", "iconName": "settings"}
    ]
    property var moreActions: [
        {"label": "Home All", "action": "home_all", "hint": "XYZ", "iconName": "home"},
        {"label": "Disable Motors", "action": "disable_motors", "hint": "M84", "iconName": "motor-off"},
        {"label": "XY Speed", "action": "speed_xy", "hint": "50 mm/s", "iconName": "speed"},
        {"label": "Z Speed", "action": "speed_z", "hint": "10 mm/s", "iconName": "speed"}
    ]
    property var portraitPlaceholders: [
        {"placeholder": true},
        {"placeholder": true}
    ]
    property var distances: [".1", ".5", "1", "5", "10", "25", "50"]
    property var xySpeeds: ["25", "50", "100", "150"]
    property var zSpeeds: ["2", "5", "10", "15"]
    property string selectedDistance: "10"
    property string selectedXYSpeed: "100"
    property string selectedZSpeed: "10"
    property bool moreVisible: false
    property string detailPage: "main"
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
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

    function fittedMoveButtonSize(padWidth, padHeight) {
        var sizeCap = Math.floor(padHeight / 3.08)
        var widthCap = Math.floor(padWidth * 0.46)
        return Math.max(44, Math.min(root.moveButtonSize, sizeCap, widthCap))
    }

    function showMore() {
        if (root.metrics.ultraWide) {
            root.moreVisible = !root.moreVisible
            return
        }
        root.detailPage = "more"
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
        if (action === "home_all" || action === "disable_motors") {
            root.moveActionRequested(action, 0, 0)
            return
        }
        root.moveActionRequested("placeholder_" + action, 0, 0)
    }

    function speedForAction(action) {
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
        return ""
    }

    function axisHomed(axis) {
        return axis.length <= 0 || root.homedAxes.indexOf(axis) >= 0
    }

    function jogAction(action) {
        return root.actionAxis(action).length > 0
    }

    function actionRequiresReady(action) {
        return action === "disable_motors"
            || action === "home_all"
            || action === "home_xy"
            || action === "home_z"
            || action === "x_minus"
            || action === "x_plus"
            || action === "y_minus"
            || action === "y_plus"
            || action === "z_minus"
            || action === "z_plus"
    }

    function actionAllowed(action) {
        if (!root.actionRequiresReady(action)) {
            return true
        }
        if (!root.printerReady()) {
            return false
        }
        if (root.jogAction(action)) {
            return root.axisHomed(root.actionAxis(action))
        }
        return true
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
        if (root.homedAxes.length <= 0) {
            return root.movementGuardText()
        }
        return "Controls ready"
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

        color: selected ? "#1b2b2e" : "#101718"
        opacity: tileRoot.enabled ? selected ? 1.0 : 0.9 : 0.46
        border.color: selected ? root.selectedAccent : "#48565a"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.18)

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

        color: "#101718"
        opacity: directionRoot.enabled ? 1.0 : 0.46
        border.color: "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.18)

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

        color: selected ? "#1b2b2e" : "#101718"
        opacity: actionRoot.enabled ? 1.0 : 0.46
        border.color: selected ? root.selectedAccent : "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.18)

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
                        : Math.max(Math.round(parent.width * 0.24), Math.round(root.moveButtonSize * 2.2))
                    height: root.metrics.portrait
                        ? Math.max(root.moveButtonSize, Math.round(root.moveButtonSize * 1.62))
                        : Math.max(Math.round(root.moveButtonSize * 2.15), Math.round(parent.height * 0.58))
                    y: root.metrics.portrait ? zMovePad.y : Math.round((parent.height - height) / 2)
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    columns: root.metrics.portrait ? 2 : 1
                    rows: root.metrics.portrait ? 1 : 2
                    rowSpacing: root.motionSectionGap
                    columnSpacing: root.motionSectionGap

                    Repeater {
                        model: root.actionButtons

                        ActionIconButton {
                            required property var modelData

                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            title: modelData.label
                            hint: modelData.hint
                            iconName: modelData.iconName
                            enabled: root.actionAllowed(modelData.action)
                            selected: modelData.action === "more"
                                && (root.moreVisible || root.detailPage === "more")

                            MouseArea {
                                anchors.fill: parent
                                enabled: root.actionAllowed(modelData.action)
                                onClicked: {
                                    if (modelData.action === "more") {
                                        root.showMore()
                                    } else {
                                        root.moveActionRequested(modelData.action, 0, 0)
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
                        color: Theme.mutedText
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
                            model: root.moreActions

                            Rectangle {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "#0b1112"
                                opacity: root.actionAllowed(modelData.action) ? 1.0 : 0.46
                                border.color: "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.18)

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
                    columns: root.metrics.ultraWide ? 1 : 4
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.fontSize * 0.35))

                    Repeater {
                        model: [
                            {"label": "X", "value": root.positionX.toFixed(2)},
                            {"label": "Y", "value": root.positionY.toFixed(2)},
                            {"label": "Z", "value": root.positionZ.toFixed(2)},
                            {"label": "E", "value": root.positionE.toFixed(2)}
                        ]

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
                    model: root.moreActions

                    Rectangle {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.2))
                        color: "#101617"
                        opacity: root.actionAllowed(modelData.action) ? 1.0 : 0.46
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.28)

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
                                text: root.moreActionHint(modelData.action, modelData.hint)
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.62))
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.actionAllowed(modelData.action)
                            onClicked: root.handleMoreAction(modelData.action)
                        }
                    }
                }
            }
        }
    }
}
