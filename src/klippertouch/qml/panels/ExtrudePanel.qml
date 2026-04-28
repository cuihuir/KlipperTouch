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
        {"label": "Temperature", "shortLabel": "Temp", "action": "temperature", "hint": "set target"},
        {"label": "Pressure Advance", "shortLabel": "Advance", "action": "pressure_advance", "hint": "placeholder"},
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
    property real positionE: 0
    property string controlStatus: ""
    property string controlError: ""
    readonly property color selectedAccent: "#7f9298"
    signal extrudeActionRequested(string action, real distance, real speed)
    signal temperaturePanelRequested()

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
        if (action === "temperature") {
            root.temperaturePanelRequested()
            return
        }
        root.controlStatus = action + " settings are reserved"
        root.controlError = ""
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

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Nozzle " + root.extruderTemperature.toFixed(1) + "° / " + root.extruderTarget.toFixed(1) + "°"
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.05))
                }

                Label {
                    Layout.maximumWidth: Math.max(96, Math.round(parent.width * 0.34))
                    color: Theme.mutedText
                    text: root.controlFeedbackText()
                    elide: Text.ElideRight
                    maximumLineCount: 1
                    wrapMode: Text.NoWrap
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.74))
                }

                ActionTile {
                    Layout.preferredWidth: Math.max(92, Math.round(root.metrics.fontSize * 6.2))
                    Layout.fillHeight: true
                    title: "Set Temp"
                    hint: ""

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.temperaturePanelRequested()
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

                    ActionTile {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(52, Math.round(root.metrics.fontSize * 3.4))
                        title: "Temperature"
                        hint: "set target"

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.openSettingsAction("temperature")
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

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Nozzle " + root.extruderTemperature.toFixed(1) + "° / " + root.extruderTarget.toFixed(1) + "°"
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize))
                }

                ActionTile {
                    Layout.preferredWidth: Math.max(92, Math.round(root.metrics.fontSize * 6.2))
                    Layout.fillHeight: true
                    title: "Set Temp"

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.temperaturePanelRequested()
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

            ActionTile {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Temperature"
                hint: "set target"

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.openSettingsAction("temperature")
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
}
