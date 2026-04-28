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

    GridLayout {
        visible: root.detailPage === "main"
        anchors.fill: parent
        anchors.margins: root.metrics.margin
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

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: root.metrics.gap

                RowLayout {
                    Layout.fillWidth: true
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Extrude"
                        font.bold: true
                        font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                    }

                    Label {
                        color: Theme.mutedText
                        text: root.extruderTemperature.toFixed(1) + " / " + root.extruderTarget.toFixed(1)
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.82))
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(76, Math.round(root.metrics.fontSize * 5.2))
                    color: "#0d1415"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(2, Math.round(root.metrics.fontSize * 0.15))

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: "Nozzle " + root.extruderTemperature.toFixed(1) + "° / " + root.extruderTarget.toFixed(1) + "°"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "E position " + root.positionE.toFixed(2) + " mm"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.controlFeedbackText()
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                        }
                    }
                }

                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: root.actionButtons

                        ActionTile {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(56, Math.round(root.metrics.fontSize * 3.8))
                            title: modelData.label
                            hint: modelData.hint

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.extrudeActionRequested(modelData.action, parseFloat(root.selectedDistance), parseFloat(root.selectedSpeed))
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
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

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Distance"
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    Repeater {
                        model: root.distances

                        ActionTile {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(42, Math.round(root.metrics.fontSize * 3.0))
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
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    Repeater {
                        model: root.speeds

                        ActionTile {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(42, Math.round(root.metrics.fontSize * 3.0))
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

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.columnSpan: 1
            Layout.preferredWidth: root.metrics.portrait ? parent.width : -1
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
                    columns: root.metrics.ultraWide ? 4 : 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: root.settingsButtons

                        ActionTile {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(60, Math.round(root.metrics.fontSize * 4.2))
                            title: root.metrics.portrait || root.metrics.ultraWide
                                ? modelData.label
                                : modelData.shortLabel
                            hint: modelData.hint

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.openSettingsAction(modelData.action)
                            }
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
        }
    }
}
