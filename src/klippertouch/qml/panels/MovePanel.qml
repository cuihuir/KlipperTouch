import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var moveButtons: [
        {"label": "Y+", "direction": "up"},
        {"label": "X-", "direction": "left"},
        {"label": "X+", "direction": "right"},
        {"label": "Y-", "direction": "down"},
        {"label": "Z+", "direction": "up"},
        {"label": "Z-", "direction": "down"}
    ]
    property var xyButtons: [
        {"label": "Y+", "direction": "up"},
        {"label": "X-", "direction": "left"},
        {"label": "X+", "direction": "right"},
        {"label": "Y-", "direction": "down"}
    ]
    property var zButtons: [
        {"label": "Z+", "direction": "up"},
        {"label": "Z-", "direction": "down"}
    ]
    property var distances: [".1", ".5", "1", "5", "10", "25", "50"]
    property string selectedDistance: "10"
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
    property string homedAxes: ""

    function selectDistance(distance) {
        root.selectedDistance = distance
    }

    component LockedTile: Rectangle {
        id: tileRoot
        property string title: ""
        property string hint: "locked"
        property bool selected: false

        color: selected ? "#1b2b2e" : "#101617"
        opacity: selected ? 1.0 : 0.9
        border.color: selected ? Theme.color3 : "#48565a"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.26)

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                color: tileRoot.selected ? Theme.text : Theme.text
                text: tileRoot.title
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.bold: tileRoot.selected
                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.02))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: tileRoot.hint
                visible: tileRoot.hint.length > 0
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.62))
            }
        }
    }

    component DirectionButton: Item {
        id: directionRoot
        property string title: ""
        property string direction: "up"

        Canvas {
            id: triangleCanvas
            anchors.fill: parent
            antialiasing: true
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()

            onPaint: {
                var ctx = getContext("2d")
                var pad = Math.max(3, Math.round(Math.min(width, height) * 0.08))
                ctx.reset()
                ctx.clearRect(0, 0, width, height)
                ctx.beginPath()
                if (directionRoot.direction === "up") {
                    ctx.moveTo(width / 2, pad)
                    ctx.lineTo(width - pad, height - pad)
                    ctx.lineTo(pad, height - pad)
                } else if (directionRoot.direction === "down") {
                    ctx.moveTo(pad, pad)
                    ctx.lineTo(width - pad, pad)
                    ctx.lineTo(width / 2, height - pad)
                } else if (directionRoot.direction === "left") {
                    ctx.moveTo(pad, height / 2)
                    ctx.lineTo(width - pad, pad)
                    ctx.lineTo(width - pad, height - pad)
                } else {
                    ctx.moveTo(width - pad, height / 2)
                    ctx.lineTo(pad, pad)
                    ctx.lineTo(pad, height - pad)
                }
                ctx.closePath()
                ctx.fillStyle = "#eef3fb"
                ctx.strokeStyle = "#0a0d0e"
                ctx.lineWidth = Math.max(2, Math.round(root.metrics.fontSize * 0.14))
                ctx.fill()
                ctx.stroke()
            }

            Connections {
                target: root
                function onWidthChanged() {
                    triangleCanvas.requestPaint()
                }
                function onHeightChanged() {
                    triangleCanvas.requestPaint()
                }
            }
        }

        Label {
            anchors.centerIn: parent
            width: directionRoot.direction === "left" || directionRoot.direction === "right" ? parent.height : parent.width
            height: directionRoot.direction === "left" || directionRoot.direction === "right" ? parent.width : parent.height
            text: directionRoot.title
            color: "#182025"
            font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.95))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.NoWrap
            rotation: directionRoot.direction === "left" ? -90 : directionRoot.direction === "right" ? 90 : 0
        }
    }

    GridLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        columns: 1
        rows: 2
        rowSpacing: root.metrics.gap

        GridLayout {
            id: controlGroupGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
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

                Item {
                    id: xyMovePad
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    property int padSize: Math.max(58, Math.min(width, height))
                    property int arrowSize: Math.max(64, Math.round(padSize * 0.32))
                    property int homeSize: Math.max(76, Math.round(padSize * 0.29))

                    Repeater {
                        model: root.xyButtons

                        DirectionButton {
                            required property var modelData
                            width: xyMovePad.arrowSize
                            height: xyMovePad.arrowSize
                            title: modelData.label
                            direction: modelData.direction
                            anchors.horizontalCenter: modelData.direction === "up" || modelData.direction === "down" ? parent.horizontalCenter : undefined
                            anchors.verticalCenter: modelData.direction === "left" || modelData.direction === "right" ? parent.verticalCenter : undefined
                            anchors.top: modelData.direction === "up" ? parent.top : undefined
                            anchors.bottom: modelData.direction === "down" ? parent.bottom : undefined
                            anchors.left: modelData.direction === "left" ? parent.left : undefined
                            anchors.right: modelData.direction === "right" ? parent.right : undefined
                        }
                    }

                    LockedTile {
                        width: xyMovePad.homeSize
                        height: xyMovePad.homeSize
                        anchors.centerIn: parent
                        title: "Home"
                        hint: "locked"
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

                Item {
                    id: zMovePad
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    property int padSize: Math.max(58, Math.min(width, height))
                    property int arrowSize: Math.max(70, Math.round(padSize * 0.32))
                    property int homeSize: Math.max(88, Math.round(padSize * 0.31))

                    DirectionButton {
                        width: zMovePad.arrowSize
                        height: zMovePad.arrowSize
                        title: "Z+"
                        direction: "up"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                    }

                    LockedTile {
                        width: zMovePad.homeSize
                        height: zMovePad.homeSize
                        anchors.centerIn: parent
                        title: "Z Home"
                        hint: "locked"
                    }

                    DirectionButton {
                        width: zMovePad.arrowSize
                        height: zMovePad.arrowSize
                        title: "Z-"
                        direction: "down"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                    }
                }
            }
        }

        Rectangle {
            id: auxiliaryPanel
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(104, Math.round(root.metrics.fontSize * 6.9))
            color: "#0d1415"
            border.color: "#344044"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: Math.max(5, Math.round(root.metrics.gap * 0.55))

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Math.max(4, Math.round(root.metrics.gap * 0.35))

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: "Move"
                            font.bold: true
                            font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.02))
                        }

                        Label {
                            color: Theme.mutedText
                            text: "Controls locked"
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                        }
                    }

                    GridLayout {
                        id: positionGrid
                        Layout.fillWidth: true
                        columns: 4
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

                GridLayout {
                    id: distanceGrid
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(34, Math.round(root.metrics.fontSize * 2.15))
                    columns: 7
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))

                    Repeater {
                        model: root.distances

                        LockedTile {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(34, Math.round(root.metrics.fontSize * 2.1))
                            title: modelData
                            hint: "mm"
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
