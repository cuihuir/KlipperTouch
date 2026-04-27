import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var moveButtons: [
        {"label": "Home", "hint": "locked"},
        {"label": "Y+", "hint": "locked"},
        {"label": "Motors Off", "hint": "locked"},
        {"label": "Z+", "hint": "locked"},
        {"label": "X-", "hint": "locked"},
        {"label": "Y-", "hint": "locked"},
        {"label": "X+", "hint": "locked"},
        {"label": "Z-", "hint": "locked"}
    ]
    property var distances: [".1", ".5", "1", "5", "10", "25", "50"]
    property string selectedDistance: "10"
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
    property string homedAxes: ""

    component LockedTile: Rectangle {
        id: tileRoot
        property string title: ""
        property string hint: "locked"
        property bool selected: false

        color: selected ? "#1b2b2e" : "#101617"
        opacity: selected ? 1.0 : 0.58
        border.color: selected ? Theme.color3 : "#263233"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.32)

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                color: tileRoot.selected ? Theme.text : Theme.mutedText
                text: tileRoot.title
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.08))
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

    GridLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        columns: root.metrics.portrait ? 1 : 2
        rows: root.metrics.portrait ? 2 : 1
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
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
                        text: "Move"
                        font.bold: true
                        font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                    }

                    Label {
                        color: Theme.mutedText
                        text: "Controls locked"
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                    }
                }

                GridLayout {
                    id: movePadGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: root.metrics.portrait ? 3 : 4
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: root.moveButtons

                        LockedTile {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(48, Math.round(root.metrics.fontSize * 3.2))
                            title: modelData.label
                            hint: modelData.hint
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(82, Math.round(root.metrics.fontSize * 5.6))
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.3))

                        GridLayout {
                            id: positionGrid
                            Layout.fillWidth: true
                            columns: 4
                            columnSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                            Repeater {
                                model: [
                                    {"label": "X", "value": root.positionX.toFixed(2)},
                                    {"label": "Y", "value": root.positionY.toFixed(2)},
                                    {"label": "Z", "value": root.positionZ.toFixed(2)},
                                    {"label": "E", "value": root.positionE.toFixed(2)}
                                ]

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 2.0))
                                    color: "#0b1112"
                                    border.color: "#263233"
                                    border.width: 1
                                    radius: Math.round(root.metrics.fontSize * 0.22)

                                    Label {
                                        anchors.centerIn: parent
                                        color: Theme.text
                                        text: modelData.label + " " + modelData.value
                                        horizontalAlignment: Text.AlignHCenter
                                        elide: Text.ElideRight
                                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                                    }
                                }
                            }
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.homedAxes.length > 0 ? "Homed: " + root.homedAxes : "Homed: unknown"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
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
                    text: "Move Distance (mm)"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                GridLayout {
                    id: distanceGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: root.metrics.portrait ? 4 : 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: root.distances

                        LockedTile {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(42, Math.round(root.metrics.fontSize * 3.0))
                            title: modelData + " mm"
                            hint: root.selectedDistance === modelData ? "selected" : "distance"
                            selected: root.selectedDistance === modelData

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.selectDistance(modelData)
                            }
                        }
                    }
                }
            }
        }
    }
}
