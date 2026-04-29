import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    objectName: "extrudePanel"
    required property var metrics
    property var distances: ["5", "10", "15", "25"]
    property var speeds: ["1", "2", "5", "25"]
    property var actionButtons: [
        {"label": "Extrude", "action": "extrude", "hint": "forward"},
        {"label": "Retract", "action": "retract", "hint": "reverse"},
        {"label": "Load", "action": "load", "hint": "macro"},
        {"label": "Unload", "action": "unload", "hint": "macro"}
    ]
    property var filamentActionButtons: [
        {"label": "Load", "action": "load", "hint": "macro"},
        {"label": "Unload", "action": "unload", "hint": "macro"}
    ]
    property var settingsButtons: [
        {"label": "Retraction", "shortLabel": "Retract", "action": "retraction", "hint": "placeholder"},
        {"label": "Materials", "shortLabel": "Materials", "action": "materials", "hint": "AFC / AMS"}
    ]
    property var materialSlots: [
        {"label": "Slot 1", "state": "reserved"},
        {"label": "Slot 2", "state": "reserved"},
        {"label": "Slot 3", "state": "reserved"},
        {"label": "Slot 4", "state": "reserved"}
    ]
    property string selectedDistance: "10"
    property string selectedSpeed: "5"
    property string detailPage: "main"
    property real actionFraction: 0.42
    property real settingsFraction: 0.58
    property real extruderTemperature: 0
    property real extruderTarget: 0
    property real extruderPressureAdvance: 0
    property real extruderSmoothTime: 0
    property real positionE: 0
    property string controlStatus: ""
    property string controlError: ""
    readonly property color selectedAccent: "#7f9298"
    readonly property int touchTargetSize: Math.max(44, Math.round(root.metrics.fontSize * 2.8))
    property string targetEditorValue: ""
    property string pressureAdvanceEditorField: "advance"
    property string pressureAdvanceEditorAdvanceValue: ""
    property string pressureAdvanceEditorSmoothValue: ""
    signal extrudeActionRequested(string action, real distance, real speed)
    signal temperatureTargetRequested(string deviceName, real target)
    signal pressureAdvanceRequested(real advance, real smoothTime)

    component ActionTile: Rectangle {
        id: tileRoot
        property string title: ""
        property string hint: ""
        property bool selected: false

        color: tileRoot.selected ? "#1b2b2e" : "#101819"
        border.color: tileRoot.selected ? root.selectedAccent : "#536165"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.38)

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(3, Math.round(root.metrics.fontSize * 0.2))
            color: "transparent"
            border.color: "#1f2a2c"
            border.width: 1
            radius: Math.round(parent.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: Math.max(2, Math.round(root.metrics.fontSize * 0.12))

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: tileRoot.title
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: tileRoot.hint
                visible: tileRoot.hint.length > 0
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.7))
            }
        }
    }

    component PlaceholderTile: Rectangle {
        id: placeholderRoot
        property string title: ""
        property string hint: ""

        color: "#0d1415"
        border.color: "#344346"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.34)

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: placeholderRoot.title
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.9))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: placeholderRoot.hint
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
            }
        }
    }

    component KeypadButton: Button {
        id: keyRoot
        property bool primary: false

        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumWidth: root.touchTargetSize
        Layout.minimumHeight: root.touchTargetSize

        contentItem: Label {
            color: keyRoot.enabled ? Theme.text : Theme.mutedText
            text: keyRoot.text
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.1))
        }

        background: Rectangle {
            color: keyRoot.primary && keyRoot.enabled ? "#1b2b2e" : "#101819"
            border.color: keyRoot.primary && keyRoot.enabled ? root.selectedAccent : "#536165"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.28)
        }
    }

    component NozzleStage: Rectangle {
        id: stageRoot

        color: Theme.buttonsBg
        border.color: "#465456"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.45)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap

            ActionTile {
                id: retractButton
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: Math.max(root.metrics.portrait ? 44 : 58, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 3.0 : 4.2)))
                title: "Retract"
                hint: "pull back"

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.extrudeActionRequested("retract", parseFloat(root.selectedDistance), parseFloat(root.selectedSpeed))
                }
            }

            Rectangle {
                id: nozzleIcon
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: Math.max(root.metrics.portrait ? 64 : 86, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 4.6 : 6.4)))
                color: "#0b1112"
                border.color: "#536165"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.48)

                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - root.metrics.gap * 2
                    spacing: Math.max(3, Math.round(root.metrics.fontSize * 0.2))

                    Label {
                        Layout.fillWidth: true
                        color: "#d9e0e2"
                        text: "⬟"
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: Math.max(42, Math.round(root.metrics.fontSize * 3.6))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Nozzle"
                        horizontalAlignment: Text.AlignHCenter
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.95))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: root.positionE.toFixed(2) + " mm"
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.72))
                    }
                }
            }

            ActionTile {
                id: extrudeButton
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: Math.max(root.metrics.portrait ? 44 : 58, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 3.0 : 4.2)))
                title: "Extrude"
                hint: "push filament"

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.extrudeActionRequested("extrude", parseFloat(root.selectedDistance), parseFloat(root.selectedSpeed))
                }
            }
        }
    }

    function selectDistance(distance) {
        root.selectedDistance = distance
    }

    function selectSpeed(speed) {
        root.selectedSpeed = speed
    }

    function openSettingsAction(action) {
        if (action === "materials") {
            root.detailPage = "materials"
            return
        }
        root.controlStatus = action + " settings are reserved"
        root.controlError = ""
    }

    function positionTargetEditor() {
        var parentWidth = targetEditorPopup.parent ? targetEditorPopup.parent.width : root.width
        var parentHeight = targetEditorPopup.parent ? targetEditorPopup.parent.height : root.height
        var margin = root.metrics.margin
        if (root.metrics.portrait) {
            targetEditorPopup.width = Math.min(parentWidth - margin * 2, Math.max(300, Math.round(parentWidth * 0.72)))
            targetEditorPopup.height = Math.min(parentHeight - margin * 2, Math.max(360, Math.round(parentHeight * 0.82)))
            targetEditorPopup.x = Math.round((parentWidth - targetEditorPopup.width) / 2)
            targetEditorPopup.y = Math.round((parentHeight - targetEditorPopup.height) / 2)
            return
        }

        var safeTop = Math.max(margin, Math.round(parentHeight * 0.22))
        targetEditorPopup.width = Math.min(parentWidth - margin * 2, Math.max(560, Math.round(parentWidth * 0.54)))
        targetEditorPopup.height = Math.min(parentHeight - safeTop - margin, Math.max(360, Math.round(parentHeight * 0.72)))
        targetEditorPopup.x = Math.max(margin, parentWidth - targetEditorPopup.width - margin)
        targetEditorPopup.y = Math.max(safeTop, parentHeight - targetEditorPopup.height - margin)
    }

    function openTargetEditor() {
        root.targetEditorValue = root.extruderTarget > 0 ? String(Math.round(root.extruderTarget)) : ""
        root.positionTargetEditor()
        targetEditorPopup.open()
    }

    function appendTargetDigit(digit) {
        if (root.targetEditorValue.length >= 3) {
            return
        }
        if (root.targetEditorValue === "0") {
            root.targetEditorValue = digit
            return
        }
        root.targetEditorValue += digit
    }

    function appendTargetDecimal() {
        if (root.targetEditorValue.indexOf(".") >= 0 || root.targetEditorValue.length >= 4) {
            return
        }
        root.targetEditorValue = root.targetEditorValue.length > 0
            ? root.targetEditorValue + "."
            : "0."
    }

    function deleteTargetDigit() {
        root.targetEditorValue = root.targetEditorValue.slice(0, -1)
    }

    function clearTargetEditor() {
        root.targetEditorValue = ""
    }

    function confirmTargetEditor() {
        if (root.targetEditorValue.length <= 0) {
            return
        }
        if (root.targetEditorValue === "." || root.targetEditorValue === "0.") {
            return
        }
        var value = Math.max(0, Math.min(350, Number(root.targetEditorValue)))
        root.targetEditorValue = String(value)
        root.temperatureTargetRequested("extruder", value)
        targetEditorPopup.close()
    }

    function positionPressureAdvanceEditor() {
        var parentWidth = pressureAdvancePopup.parent ? pressureAdvancePopup.parent.width : root.width
        var parentHeight = pressureAdvancePopup.parent ? pressureAdvancePopup.parent.height : root.height
        var margin = root.metrics.margin
        if (root.metrics.portrait) {
            pressureAdvancePopup.width = Math.min(parentWidth - margin * 2, Math.max(320, Math.round(parentWidth * 0.78)))
            pressureAdvancePopup.height = Math.min(parentHeight - margin * 2, Math.max(420, Math.round(parentHeight * 0.86)))
            pressureAdvancePopup.x = Math.round((parentWidth - pressureAdvancePopup.width) / 2)
            pressureAdvancePopup.y = Math.round((parentHeight - pressureAdvancePopup.height) / 2)
            return
        }

        var safeTop = Math.max(margin, Math.round(parentHeight * 0.18))
        pressureAdvancePopup.width = Math.min(parentWidth - margin * 2, Math.max(620, Math.round(parentWidth * 0.58)))
        pressureAdvancePopup.height = Math.min(parentHeight - safeTop - margin, Math.max(420, Math.round(parentHeight * 0.78)))
        pressureAdvancePopup.x = Math.max(margin, parentWidth - pressureAdvancePopup.width - margin)
        pressureAdvancePopup.y = Math.max(safeTop, parentHeight - pressureAdvancePopup.height - margin)
    }

    function openPressureAdvanceEditor() {
        root.pressureAdvanceEditorField = "advance"
        root.pressureAdvanceEditorAdvanceValue = root.extruderPressureAdvance.toFixed(3)
        root.pressureAdvanceEditorSmoothValue = root.extruderSmoothTime.toFixed(3)
        root.positionPressureAdvanceEditor()
        pressureAdvancePopup.open()
    }

    function activePressureAdvanceValue() {
        return root.pressureAdvanceEditorField === "smooth"
            ? root.pressureAdvanceEditorSmoothValue
            : root.pressureAdvanceEditorAdvanceValue
    }

    function setActivePressureAdvanceValue(value) {
        if (root.pressureAdvanceEditorField === "smooth") {
            root.pressureAdvanceEditorSmoothValue = value
            return
        }
        root.pressureAdvanceEditorAdvanceValue = value
    }

    function appendPressureAdvanceDigit(digit) {
        var value = root.activePressureAdvanceValue()
        if (value.length >= 6) {
            return
        }
        if (value === "0") {
            root.setActivePressureAdvanceValue(digit)
            return
        }
        root.setActivePressureAdvanceValue(value + digit)
    }

    function appendPressureAdvanceDecimal() {
        var value = root.activePressureAdvanceValue()
        if (value.indexOf(".") >= 0 || value.length >= 6) {
            return
        }
        root.setActivePressureAdvanceValue(value.length > 0 ? value + "." : "0.")
    }

    function deletePressureAdvanceDigit() {
        var value = root.activePressureAdvanceValue()
        root.setActivePressureAdvanceValue(value.slice(0, -1))
    }

    function clearPressureAdvanceEditor() {
        root.setActivePressureAdvanceValue("")
    }

    function confirmPressureAdvanceEditor() {
        if (root.pressureAdvanceEditorAdvanceValue.length <= 0
                || root.pressureAdvanceEditorSmoothValue.length <= 0) {
            return
        }
        var advance = Math.max(0, Math.min(5, Number(root.pressureAdvanceEditorAdvanceValue)))
        var smoothTime = Math.max(0, Math.min(1, Number(root.pressureAdvanceEditorSmoothValue)))
        if (isNaN(advance) || isNaN(smoothTime)) {
            return
        }
        root.pressureAdvanceEditorAdvanceValue = advance.toFixed(3)
        root.pressureAdvanceEditorSmoothValue = smoothTime.toFixed(3)
        root.pressureAdvanceRequested(advance, smoothTime)
        pressureAdvancePopup.close()
    }

    function openFeedSetup() {
        root.detailPage = "feed"
    }

    function goBack() {
        if (root.detailPage !== "main") {
            root.detailPage = "main"
            return true
        }
        return false
    }

    function controlFeedbackText() {
        if (root.controlError.length > 0) {
            return root.controlError
        }
        if (root.controlStatus.length > 0) {
            return root.controlStatus
        }
        return "Extrusion ready"
    }

    ColumnLayout {
        visible: root.detailPage === "main" && !root.metrics.portrait
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        spacing: root.metrics.gap

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(58, Math.round(root.metrics.fontSize * 3.7))
            color: "#0d1415"
            border.color: "#344346"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            RowLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: root.metrics.gap

                Rectangle {
                    id: nozzleTemperatureArea
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#101819"
                    border.color: "#536165"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.28)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(6, Math.round(root.metrics.fontSize * 0.38))
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Nozzle"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.extruderTemperature.toFixed(1) + "° / " + root.extruderTarget.toFixed(1) + "°"
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.05))
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.openTargetEditor()
                    }
                }

                Rectangle {
                    id: pressureAdvanceArea
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#101819"
                    border.color: "#536165"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.28)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(6, Math.round(root.metrics.fontSize * 0.38))
                        spacing: 0

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.3))

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: "Pressure Advance"
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                            }

                            Label {
                                color: Theme.mutedText
                                text: root.controlFeedbackText()
                                elide: Text.ElideRight
                                maximumLineCount: 1
                                visible: root.metrics.ultraWide
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                            }
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: "ADV " + root.extruderPressureAdvance.toFixed(3)
                                + " / SMT " + root.extruderSmoothTime.toFixed(3)
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.05))
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.openPressureAdvanceEditor()
                    }
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: root.metrics.portrait ? 1 : 3
            rows: root.metrics.portrait ? 3 : 1
            rowSpacing: root.metrics.gap
            columnSpacing: root.metrics.gap

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: root.metrics.portrait ? parent.width : -1
                Layout.minimumWidth: 0
                color: Theme.buttonsBg
                border.color: "#465456"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.45)

                GridLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    columns: 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Label {
                        Layout.columnSpan: 2
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Feed setup"
                        font.bold: true
                        font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize))
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Length"
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                        }

                        Repeater {
                            model: root.distances

                            ActionTile {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: Math.max(root.metrics.portrait ? 32 : 38, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 2.0 : 2.6)))
                                title: modelData + " mm"
                                selected: root.selectedDistance === modelData

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.selectDistance(modelData)
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Speed"
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                        }

                        Repeater {
                            model: root.speeds

                            ActionTile {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: Math.max(root.metrics.portrait ? 32 : 38, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 2.0 : 2.6)))
                                title: root.metrics.ultraWide ? modelData + " mm/s" : modelData
                                selected: root.selectedSpeed === modelData

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.selectSpeed(modelData)
                                }
                            }
                        }
                    }
                }
            }

            NozzleStage {
                id: nozzleStage
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 0
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 0
                color: Theme.buttonsBg
                border.color: "#465456"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.45)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Filament"
                        font.bold: true
                        font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize))
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 2
                        rowSpacing: root.metrics.gap
                        columnSpacing: root.metrics.gap

                        Repeater {
                            model: root.filamentActionButtons

                            ActionTile {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.4))
                                title: modelData.label
                                hint: modelData.hint

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.extrudeActionRequested(modelData.action, parseFloat(root.selectedDistance), parseFloat(root.selectedSpeed))
                                }
                            }
                        }
                    }

                    ActionTile {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.4))
                        title: "Materials"
                        hint: "AFC / AMS"

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.openSettingsAction("materials")
                        }
                    }
                }
            }
        }
    }

    ColumnLayout {
        visible: root.detailPage === "main" && root.metrics.portrait
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        spacing: root.metrics.gap

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(58, Math.round(root.metrics.fontSize * 3.7))
            color: "#0d1415"
            border.color: "#344346"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            RowLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: root.metrics.gap

                Rectangle {
                    id: nozzleTemperatureAreaPortrait
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#101819"
                    border.color: "#536165"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.28)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(6, Math.round(root.metrics.fontSize * 0.38))
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Nozzle"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.extruderTemperature.toFixed(1) + "° / " + root.extruderTarget.toFixed(1) + "°"
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize))
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.openTargetEditor()
                    }
                }

                Rectangle {
                    id: pressureAdvanceAreaPortrait
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#101819"
                    border.color: "#536165"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.28)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(6, Math.round(root.metrics.fontSize * 0.38))
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Pressure Advance"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: "ADV " + root.extruderPressureAdvance.toFixed(3)
                                + " / SMT " + root.extruderSmoothTime.toFixed(3)
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize))
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.openPressureAdvanceEditor()
                    }
                }
            }
        }

        NozzleStage {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: Math.max(246, Math.round(root.metrics.fontSize * 15.5))
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(210, Math.round(root.metrics.fontSize * 13.4))
            columns: 2
            rowSpacing: root.metrics.gap
            columnSpacing: root.metrics.gap

            ActionTile {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Length " + root.selectedDistance + " mm"
                hint: "tap to change"

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.openFeedSetup()
                }
            }

            ActionTile {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Speed " + root.selectedSpeed
                hint: "tap to change"

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.openFeedSetup()
                }
            }

            Repeater {
                model: root.filamentActionButtons

                ActionTile {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: modelData.label
                    hint: modelData.hint

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.extrudeActionRequested(modelData.action, parseFloat(root.selectedDistance), parseFloat(root.selectedSpeed))
                    }
                }
            }

            ActionTile {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Materials"
                hint: "AFC / AMS"

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.openSettingsAction("materials")
                }
            }

        }
    }

    Rectangle {
        visible: root.detailPage === "feed"
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        color: Theme.buttonsBg
        border.color: "#465456"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.45)

        GridLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            columns: 2
            rowSpacing: root.metrics.gap
            columnSpacing: root.metrics.gap

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Length"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.05))
                }

                Repeater {
                    model: root.distances

                    ActionTile {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        title: modelData + " mm"
                        selected: root.selectedDistance === modelData

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.selectDistance(modelData)
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Speed"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.05))
                }

                Repeater {
                    model: root.speeds

                    ActionTile {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        title: modelData + " mm/s"
                        selected: root.selectedSpeed === modelData

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.selectSpeed(modelData)
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        visible: root.detailPage === "materials"
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        color: Theme.buttonsBg
        border.color: "#465456"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.45)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Material slots"
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.25))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: "AFC / AMS entry frame. Hardware protocol adapters will populate these slots."
                wrapMode: Text.WordWrap
                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.82))
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 2 : 4
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: root.materialSlots

                    PlaceholderTile {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: Math.max(88, Math.round(root.metrics.fontSize * 5.8))
                        title: modelData.label
                        hint: modelData.state
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(74, Math.round(root.metrics.fontSize * 4.8))
                color: "#0d1415"
                border.color: "#344346"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.34)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: root.metrics.ultraWide ? "Selected: Slot 1" : "Slot 1"
                        elide: Text.ElideRight
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    ActionTile {
                        Layout.preferredWidth: Math.max(128, Math.round(root.metrics.fontSize * 8.4))
                        Layout.fillHeight: true
                        title: root.metrics.ultraWide ? "Load Selected" : "Load"
                        hint: "reserved"
                    }

                    ActionTile {
                        Layout.preferredWidth: Math.max(136, Math.round(root.metrics.fontSize * 8.8))
                        Layout.fillHeight: true
                        title: root.metrics.ultraWide ? "Unload Selected" : "Unload"
                        hint: "reserved"
                    }
                }
            }
        }
    }

    Popup {
        id: pressureAdvancePopup
        parent: Overlay.overlay
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        width: 620
        height: 440
        x: 0
        y: 0
        padding: Math.max(8, Math.round(root.metrics.fontSize * 0.7))

        background: Rectangle {
            color: "#101617"
            border.color: Theme.color4
            border.width: 2
            radius: Math.round(root.metrics.fontSize * 0.45)
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.4))

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Pressure advance"
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(root.touchTargetSize, Math.round(root.metrics.fontSize * 3.4))
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: root.pressureAdvanceEditorField === "advance" ? "#1b2b2e" : "#050808"
                    border.color: root.pressureAdvanceEditorField === "advance" ? root.selectedAccent : "#465456"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.3)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(8, Math.round(root.metrics.fontSize * 0.5))
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "ADVANCE"
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.pressureAdvanceEditorAdvanceValue === ""
                                ? "--"
                                : root.pressureAdvanceEditorAdvanceValue
                            horizontalAlignment: Text.AlignRight
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(22, Math.round(root.metrics.fontSize * 1.5))
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.pressureAdvanceEditorField = "advance"
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: root.pressureAdvanceEditorField === "smooth" ? "#1b2b2e" : "#050808"
                    border.color: root.pressureAdvanceEditorField === "smooth" ? root.selectedAccent : "#465456"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.3)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(8, Math.round(root.metrics.fontSize * 0.5))
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "SMOOTH_TIME"
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.pressureAdvanceEditorSmoothValue === ""
                                ? "--"
                                : root.pressureAdvanceEditorSmoothValue
                            horizontalAlignment: Text.AlignRight
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(22, Math.round(root.metrics.fontSize * 1.5))
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.pressureAdvanceEditorField = "smooth"
                    }
                }

                KeypadButton {
                    Layout.preferredWidth: Math.max(root.touchTargetSize, Math.round(root.metrics.fontSize * 4.6))
                    Layout.fillWidth: false
                    text: "←"
                    onClicked: root.deletePressureAdvanceDigit()
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 3
                    columnSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.4))
                    rowSpacing: columnSpacing

                    Repeater {
                        model: [
                            "1", "2", "3",
                            "4", "5", "6",
                            "7", "8", "9",
                            ".", "0", "Clear"
                        ]

                        KeypadButton {
                            required property string modelData
                            text: modelData
                            onClicked: {
                                if (modelData === ".") {
                                    root.appendPressureAdvanceDecimal()
                                } else if (modelData === "Clear") {
                                    root.clearPressureAdvanceEditor()
                                } else {
                                    root.appendPressureAdvanceDigit(modelData)
                                }
                            }
                        }
                    }
                }

                ColumnLayout {
                    Layout.preferredWidth: Math.max(root.touchTargetSize, Math.round(root.metrics.fontSize * 5.4))
                    Layout.fillHeight: true
                    spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                    KeypadButton {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        text: "Cancel"
                        onClicked: pressureAdvancePopup.close()
                    }

                    KeypadButton {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        text: "Set"
                        enabled: root.pressureAdvanceEditorAdvanceValue !== ""
                            && root.pressureAdvanceEditorSmoothValue !== ""
                        primary: true
                        onClicked: root.confirmPressureAdvanceEditor()
                    }
                }
            }
        }
    }

    Popup {
        id: targetEditorPopup
        parent: Overlay.overlay
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        width: 560
        height: 432
        x: 0
        y: 0
        padding: Math.max(8, Math.round(root.metrics.fontSize * 0.7))

        background: Rectangle {
            color: "#101617"
            border.color: Theme.color4
            border.width: 2
            radius: Math.round(root.metrics.fontSize * 0.45)
        }

        ColumnLayout {
            id: landscapeTargetEditor
            visible: !root.metrics.portrait
            anchors.fill: parent
            spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.4))

            RowLayout {
                id: landscapeHeaderRow
                Layout.fillWidth: true
                Layout.fillHeight: false
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Nozzle target"
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
                }

                Label {
                    color: Theme.mutedText
                    text: Math.round(root.extruderTemperature) + "° / 350°"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.82))
                }
            }

            RowLayout {
                id: landscapeInputRow
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: root.touchTargetSize
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: root.touchTargetSize
                    color: "#050808"
                    border.color: "#465456"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.3)

                    Label {
                        anchors.fill: parent
                        anchors.margins: Math.max(8, Math.round(root.metrics.fontSize * 0.5))
                        color: Theme.text
                        text: root.targetEditorValue === "" ? "--" : root.targetEditorValue + "°"
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: Math.max(26, Math.round(root.metrics.fontSize * 1.8))
                    }
                }

                KeypadButton {
                    id: landscapeBackspaceButton
                    Layout.preferredWidth: Math.max(root.touchTargetSize, Math.round(root.metrics.fontSize * 4.6))
                    Layout.fillWidth: false
                    text: "←"
                    onClicked: root.deleteTargetDigit()
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: root.touchTargetSize * 3
                    + Math.max(6, Math.round(root.metrics.fontSize * 0.4)) * 2
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                GridLayout {
                    id: targetKeypadGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 3
                    columnSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.4))
                    rowSpacing: columnSpacing

                    Repeater {
                        model: ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

                        KeypadButton {
                            required property string modelData
                            text: modelData
                            onClicked: {
                                root.appendTargetDigit(modelData)
                            }
                        }
                    }
                }

                KeypadButton {
                    id: landscapeCancelButton
                    Layout.preferredWidth: Math.max(root.touchTargetSize, Math.round(root.metrics.fontSize * 5.0))
                    Layout.fillWidth: false
                    text: "Cancel"
                    onClicked: targetEditorPopup.close()
                }
            }

            RowLayout {
                id: landscapeBottomRow
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: root.touchTargetSize
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                KeypadButton {
                    Layout.fillWidth: true
                    text: "."
                    onClicked: root.appendTargetDecimal()
                }

                KeypadButton {
                    Layout.fillWidth: true
                    text: "0"
                    onClicked: root.appendTargetDigit("0")
                }

                KeypadButton {
                    id: landscapeSetButton
                    Layout.fillWidth: true
                    text: "Set"
                    enabled: root.targetEditorValue !== ""
                    primary: true
                    onClicked: root.confirmTargetEditor()
                }
            }
        }

        ColumnLayout {
            visible: root.metrics.portrait
            anchors.fill: parent
            spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.55))

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Nozzle target"
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
            }

            RowLayout {
                Layout.fillWidth: true

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "Actual " + Math.round(root.extruderTemperature) + "°"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }

                Label {
                    color: Theme.mutedText
                    text: "Max 350°"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.minimumHeight: root.touchTargetSize
                Layout.preferredHeight: Math.max(root.touchTargetSize, Math.round(root.metrics.fontSize * 3.0))
                color: "#050808"
                border.color: "#465456"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.3)

                Label {
                    anchors.fill: parent
                    anchors.margins: Math.max(8, Math.round(root.metrics.fontSize * 0.5))
                    color: Theme.text
                    text: root.targetEditorValue === "" ? "--" : root.targetEditorValue + "°"
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: Math.max(26, Math.round(root.metrics.fontSize * 1.8))
                }
            }

            GridLayout {
                id: targetPortraitKeypadGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: 3
                columnSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.4))
                rowSpacing: columnSpacing

                Repeater {
                    model: [
                        "1", "2", "3",
                        "4", "5", "6",
                        "7", "8", "9",
                        "Clear", "0", "Del"
                    ]

                    KeypadButton {
                        required property string modelData
                        text: modelData
                        onClicked: {
                            if (modelData === "Clear") {
                                root.clearTargetEditor()
                            } else if (modelData === "Del") {
                                root.deleteTargetDigit()
                            } else {
                                root.appendTargetDigit(modelData)
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: Math.max(8, Math.round(root.metrics.fontSize * 0.5))

                KeypadButton {
                    Layout.fillWidth: true
                    text: "Cancel"
                    onClicked: targetEditorPopup.close()
                }

                KeypadButton {
                    Layout.fillWidth: true
                    text: "Set"
                    enabled: root.targetEditorValue !== ""
                    primary: true
                    onClicked: root.confirmTargetEditor()
                }
            }
        }
    }
}
