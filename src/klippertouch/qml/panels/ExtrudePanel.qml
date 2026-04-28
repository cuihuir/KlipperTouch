import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
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
        {"label": "Temperature"},
        {"label": "Pressure Advance"},
        {"label": "Retraction"},
        {"label": "Spoolman"}
    ]
    property string selectedDistance: "10"
    property string selectedSpeed: "5"
    property real actionFraction: 0.42
    property real settingsFraction: 0.58
    property real extruderTemperature: 0
    property real extruderTarget: 0
    property real positionE: 0
    readonly property color selectedAccent: "#7f9298"
    signal extrudeActionRequested(string action, real distance, real speed)

    component LockedTile: Rectangle {
        id: tileRoot
        property string title: ""
        property string hint: "locked"

        color: "#101617"
        opacity: 0.58
        border.color: "#263233"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.32)

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
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
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
            }
        }
    }

    function selectDistance(distance) {
        root.selectedDistance = distance
    }

    function selectSpeed(speed) {
        root.selectedSpeed = speed
    }

    GridLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        columns: root.metrics.portrait ? 1 : 2
        rows: root.metrics.portrait ? 2 : 1
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: !root.metrics.portrait
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * root.actionFraction
            Layout.preferredHeight: root.metrics.portrait
                ? Math.max(308, Math.round(root.metrics.fontSize * 19.2))
                : -1
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
                    text: "Extrude"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "Extrusion ready"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(92, Math.round(root.metrics.fontSize * 6.4))
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.32))

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
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.86))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Commanded extrusion status"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
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

                        LockedTile {
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
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * root.settingsFraction
            Layout.minimumWidth: 0
            columns: 2
            rowSpacing: root.metrics.gap
            columnSpacing: root.metrics.gap

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.preferredHeight: Math.max(78, Math.round(root.metrics.fontSize * 5.2))
                Layout.columnSpan: 2
                columns: 4
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: root.settingsButtons

                    LockedTile {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.2))
                        title: modelData.label
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

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Distance"
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: root.metrics.portrait ? 2 : 1
                        rowSpacing: root.metrics.gap
                        columnSpacing: root.metrics.gap

                        Repeater {
                            model: root.distances

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: Math.max(42, Math.round(root.metrics.fontSize * 3.0))
                                color: root.selectedDistance === modelData ? "#1b2b2e" : "#101617"
                                border.color: root.selectedDistance === modelData ? root.selectedAccent : "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.28)

                                Label {
                                    anchors.centerIn: parent
                                    color: root.selectedDistance === modelData ? Theme.text : Theme.mutedText
                                    text: modelData + " mm"
                                    horizontalAlignment: Text.AlignHCenter
                                    font.bold: root.selectedDistance === modelData
                                    font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.92))
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.selectDistance(modelData)
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

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Speed"
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: root.metrics.portrait ? 2 : 1
                        rowSpacing: root.metrics.gap
                        columnSpacing: root.metrics.gap

                        Repeater {
                            model: root.speeds

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumHeight: Math.max(42, Math.round(root.metrics.fontSize * 3.0))
                                color: root.selectedSpeed === modelData ? "#1b2b2e" : "#101617"
                                border.color: root.selectedSpeed === modelData ? root.selectedAccent : "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.28)

                                Label {
                                    anchors.centerIn: parent
                                    color: root.selectedSpeed === modelData ? Theme.text : Theme.mutedText
                                    text: modelData + " mm/s"
                                    horizontalAlignment: Text.AlignHCenter
                                    font.bold: root.selectedSpeed === modelData
                                    font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.92))
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.selectSpeed(modelData)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
