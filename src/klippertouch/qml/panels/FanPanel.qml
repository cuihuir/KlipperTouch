import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    objectName: "fanPanel"
    required property var metrics
    property var fanDevices: []
    property string controlStatus: ""
    property string controlError: ""
    signal fanSpeedRequested(string deviceName, real percent)

    Rectangle {
        anchors.fill: parent
        color: "#071112"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        spacing: root.metrics.gap

        RowLayout {
            Layout.fillWidth: true
            visible: !root.metrics.ultraWide
            spacing: root.metrics.gap

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Fans"
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
            }

            Label {
                color: root.controlError.length > 0 ? "#c7ced1" : Theme.mutedText
                text: root.controlError.length > 0
                    ? root.controlError
                    : root.controlStatus.length > 0 ? root.controlStatus : root.fanDevices.length + " devices"
                elide: Text.ElideRight
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
            }
        }

        Label {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.fanDevices.length <= 0
            color: Theme.mutedText
            text: "No fans detected"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: root.metrics.fontSize
        }

        GridView {
            id: fanGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.metrics.ultraWide && root.fanDevices.length > 0
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            model: root.fanDevices
            readonly property int gridCols: 3
            readonly property int gridRows: 2
            readonly property int cellGap: root.metrics.gap
            cellWidth: Math.floor(width / gridCols)
            cellHeight: Math.floor(height / gridRows)

            delegate: Rectangle {
                id: gridFanCard
                required property var modelData
                readonly property real speedValue: Number(modelData.speed || 0)
                property real draftSpeed: speedValue
                readonly property real displaySpeed: gridSlider.pressed ? draftSpeed : speedValue
                readonly property bool hasRpm: modelData.rpm !== undefined && modelData.rpm !== null
                readonly property real rpmValue: hasRpm ? Number(modelData.rpm) : 0
                readonly property int gaugeSize: Math.min(
                    Math.round(fanGrid.cellHeight - fanGrid.cellGap * 3),
                    Math.round(root.metrics.safeTouchSize * 1.8)
                )

                onSpeedValueChanged: {
                    if (!gridSlider.pressed && !releaseGuard.running) {
                        draftSpeed = speedValue
                    }
                }

                width: fanGrid.cellWidth - fanGrid.cellGap
                height: fanGrid.cellHeight - fanGrid.cellGap
                x: Math.round(fanGrid.cellGap / 2)
                y: Math.round(fanGrid.cellGap / 2)
                color: "#0d1415"
                border.color: modelData.speed_settable ? "#536165" : "#344346"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.45)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: Math.max(8, Math.round(root.metrics.gap * 0.9))

                    ColumnLayout {
                        Layout.fillHeight: true
                        Layout.maximumWidth: Math.round(gridFanCard.width * 0.20)
                        Layout.alignment: Qt.AlignVCenter
                        spacing: 2

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: gridFanCard.modelData.display_name
                            elide: Text.ElideRight
                            font.bold: true
                            font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.0))
                        }

                        Label {
                            Layout.fillWidth: true
                            visible: gridFanCard.hasRpm
                            color: Theme.mutedText
                            text: Math.round(gridFanCard.rpmValue) + " RPM"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                        }
                    }

                    Item {
                        id: gauge
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: gridFanCard.gaugeSize
                        Layout.preferredHeight: gridFanCard.gaugeSize
                        readonly property real value: gridFanCard.displaySpeed
                        readonly property int bw: Math.max(4, Math.round(width * 0.08))
                        readonly property real ringR: (width - bw * 2) / 2

                        Rectangle {
                            anchors.fill: parent
                            radius: width / 2
                            color: "transparent"
                            border.color: "#263233"
                            border.width: gauge.bw
                        }

                        Repeater {
                            model: 24

                            Rectangle {
                                readonly property real angle: (index / 24) * 2 * Math.PI - Math.PI / 2
                                x: gauge.width / 2 + gauge.ringR * Math.cos(angle) - width / 2
                                y: gauge.height / 2 + gauge.ringR * Math.sin(angle) - height / 2
                                width: gauge.bw
                                height: gauge.bw
                                radius: width / 2
                                color: (index / 24 * 100) < gauge.value ? "#7f9298" : "transparent"
                            }
                        }

                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.width - gauge.bw * 4 - 2
                            height: parent.height - gauge.bw * 4 - 2
                            radius: width / 2
                            color: "#0d1415"
                        }

                        Label {
                            anchors.centerIn: parent
                            color: Theme.text
                            text: Math.round(gauge.value) + "%"
                            font.bold: true
                            font.pixelSize: Math.max(11, Math.round(parent.width * 0.24))
                        }
                    }

                    Rectangle {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: root.metrics.safeTouchSize
                        Layout.preferredHeight: Layout.preferredWidth
                        Layout.maximumHeight: width
                        visible: gridFanCard.modelData.speed_settable
                        scale: gridOffMouse.pressed ? 0.96 : 1.0
                        transformOrigin: Item.Center
                        color: gridOffMouse.pressed ? "#26373b" : "#101819"
                        border.color: Math.round(gridFanCard.displaySpeed) === 0 ? "#7f9298" : "#536165"
                        border.width: Math.round(gridFanCard.displaySpeed) === 0 ? 2 : 1
                        radius: Math.round(root.metrics.fontSize * 0.32)
                        Behavior on scale { NumberAnimation { duration: 70; easing.type: Easing.OutQuad } }

                        Label {
                            anchors.centerIn: parent
                            color: Theme.text
                            text: "Off"
                            font.bold: true
                            font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.85))
                        }

                        MouseArea {
                            id: gridOffMouse
                            anchors.fill: parent
                            onClicked: {
                                gridFanCard.draftSpeed = 0
                                root.fanSpeedRequested(gridFanCard.modelData.name, 0)
                            }
                        }
                    }

                    Rectangle {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: root.metrics.safeTouchSize
                        Layout.preferredHeight: Layout.preferredWidth
                        Layout.maximumHeight: width
                        visible: gridFanCard.modelData.speed_settable
                        scale: gridFullMouse.pressed ? 0.96 : 1.0
                        transformOrigin: Item.Center
                        color: gridFullMouse.pressed ? "#26373b" : "#101819"
                        border.color: Math.round(gridFanCard.displaySpeed) === 100 ? "#7f9298" : "#536165"
                        border.width: Math.round(gridFanCard.displaySpeed) === 100 ? 2 : 1
                        radius: Math.round(root.metrics.fontSize * 0.32)
                        Behavior on scale { NumberAnimation { duration: 70; easing.type: Easing.OutQuad } }

                        Label {
                            anchors.centerIn: parent
                            color: Theme.text
                            text: "100%"
                            font.bold: true
                            font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.85))
                        }

                        MouseArea {
                            id: gridFullMouse
                            anchors.fill: parent
                            onClicked: {
                                gridFanCard.draftSpeed = 100
                                root.fanSpeedRequested(gridFanCard.modelData.name, 100)
                            }
                        }
                    }

                    Slider {
                        id: gridSlider
                        visible: gridFanCard.modelData.speed_settable
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: root.metrics.minimumTouchSize
                        Layout.alignment: Qt.AlignVCenter
                        from: 0
                        to: 100
                        stepSize: 0
                        live: true
                        value: gridFanCard.draftSpeed

                        onMoved: gridFanCard.draftSpeed = Math.max(0, Math.min(100, value))
                        onPressedChanged: {
                            if (pressed) {
                                gridFanCard.draftSpeed = gridFanCard.speedValue
                                releaseGuard.stop()
                            } else {
                                gridFanCard.draftSpeed = Math.max(0, Math.min(100, value))
                                root.fanSpeedRequested(gridFanCard.modelData.name, gridFanCard.draftSpeed)
                                releaseGuard.start()
                            }
                        }

                        Timer {
                            id: releaseGuard
                            interval: 1500
                        }

                        background: Rectangle {
                            x: gridSlider.leftPadding
                            y: gridSlider.topPadding + gridSlider.availableHeight / 2 - height / 2
                            width: gridSlider.availableWidth
                            height: Math.max(14, Math.round(root.metrics.fontSize * 0.85))
                            radius: height / 2
                            color: "#101819"
                            border.color: "#536165"
                            border.width: 1

                            Rectangle {
                                width: gridSlider.visualPosition * parent.width
                                height: parent.height
                                radius: parent.radius
                                color: "#7f9298"
                            }
                        }

                        handle: Rectangle {
                            x: gridSlider.leftPadding + gridSlider.visualPosition * (gridSlider.availableWidth - width)
                            y: gridSlider.topPadding + gridSlider.availableHeight / 2 - height / 2
                            width: root.metrics.minimumTouchSize
                            height: width
                            radius: width / 2
                            color: gridSlider.pressed ? "#d4dde0" : "#aebdc2"
                            border.color: "#0b1112"
                            border.width: 2
                        }
                    }
                }
            }
        }

        ListView {
            id: fanList
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !root.metrics.ultraWide && root.fanDevices.length > 0
            clip: true
            spacing: root.metrics.gap
            boundsBehavior: Flickable.StopAtBounds
            property real savedContentY: 0
            property bool restoringContentY: false
            model: root.fanDevices

            function boundedContentY(value) {
                return Math.max(0, Math.min(value, Math.max(0, contentHeight - height)))
            }

            function restoreScrollPosition() {
                var targetY = savedContentY
                Qt.callLater(function() {
                    restoringContentY = true
                    contentY = boundedContentY(targetY)
                    restoringContentY = false
                })
            }

            onContentYChanged: {
                if (!restoringContentY && (moving || dragging || flicking)) {
                    savedContentY = boundedContentY(contentY)
                }
            }
            onMovementEnded: savedContentY = boundedContentY(contentY)
            onModelChanged: restoreScrollPosition()
            onCountChanged: restoreScrollPosition()

            footer: Item {
                width: fanList.width
                height: root.metrics.gap
            }

            delegate: Rectangle {
                id: fanCard
                required property var modelData
                readonly property real speedValue: Number(modelData.speed || 0)
                property real draftSpeed: speedValue
                readonly property string modeText: modelData.speed_settable ? "manual" : "auto"
                readonly property real displaySpeed: speedSlider.pressed ? draftSpeed : speedValue
                readonly property bool hasRpm: modelData.rpm !== undefined && modelData.rpm !== null
                readonly property real rpmValue: hasRpm ? Number(modelData.rpm) : 0

                onSpeedValueChanged: {
                    if (!speedSlider.pressed) {
                        draftSpeed = speedValue
                    }
                }

                width: fanList.width
                height: Math.max(
                    modelData.speed_settable ? (root.metrics.portrait ? 156 : 144) : 92,
                    Math.round(
                        root.metrics.fontSize
                            * (modelData.speed_settable
                                ? (root.metrics.portrait ? 9.8 : 6.4)
                                : (root.metrics.portrait ? 5.9 : 4.1))
                    )
                )
                color: "#0d1415"
                border.color: modelData.speed_settable ? "#536165" : "#344346"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.38)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: Math.max(6, Math.round(root.metrics.gap * 0.65))

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: modelData.display_name
                                elide: Text.ElideRight
                                font.bold: true
                                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: modelData.name + " · " + fanCard.modeText
                                    + (fanCard.hasRpm ? " · " + Math.round(fanCard.rpmValue) + " RPM" : "")
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                            }
                        }

                        Label {
                            color: Theme.text
                            text: Math.round(fanCard.displaySpeed) + "%"
                            horizontalAlignment: Text.AlignRight
                            font.bold: true
                            font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                        color: "#101819"
                        border.color: "#263233"
                        border.width: 1
                        radius: height / 2

                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: Math.max(parent.height, parent.width * Math.max(0, Math.min(100, fanCard.displaySpeed)) / 100)
                            color: "#7f9298"
                            radius: parent.radius
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(
                            root.metrics.portrait ? 62 : 54,
                            Math.round(root.metrics.fontSize * (root.metrics.portrait ? 3.9 : 2.4))
                        )
                        visible: modelData.speed_settable
                        spacing: Math.max(6, Math.round(root.metrics.gap * 0.6))

                        Repeater {
                            model: [0, 100]

                            Rectangle {
                                required property int modelData
                                readonly property int percent: modelData

                                Layout.preferredWidth: Math.max(76, Math.round(root.metrics.fontSize * 4.6))
                                Layout.fillHeight: true
                                scale: fanShortcutMouse.pressed ? 0.96 : 1.0
                                transformOrigin: Item.Center
                                color: fanShortcutMouse.pressed ? "#26373b" : "#101819"
                                border.color: Math.round(fanCard.displaySpeed) === percent ? "#7f9298" : "#536165"
                                border.width: Math.round(fanCard.displaySpeed) === percent ? 2 : 1
                                radius: Math.round(root.metrics.fontSize * 0.28)
                                Behavior on scale {
                                    NumberAnimation { duration: 70; easing.type: Easing.OutQuad }
                                }

                                Rectangle {
                                    id: fanShortcutDepth
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.bottom: parent.bottom
                                    height: Math.max(2, Math.round(root.metrics.fontSize * 0.18))
                                    visible: !fanShortcutMouse.pressed
                                    color: "#050808"
                                    opacity: 0.78
                                    radius: parent.radius
                                }

                                Label {
                                    anchors.centerIn: parent
                                    color: Theme.text
                                    text: percent === 0 ? "Off" : percent + "%"
                                    font.bold: true
                                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                                }

                                MouseArea {
                                    id: fanShortcutMouse
                                    anchors.fill: parent
                                    onClicked: {
                                        fanCard.draftSpeed = percent
                                        root.fanSpeedRequested(fanCard.modelData.name, fanCard.draftSpeed)
                                    }
                                }
                            }
                        }

                        Slider {
                            id: speedSlider
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            from: 0
                            to: 100
                            stepSize: 0
                            live: true
                            value: fanCard.draftSpeed

                            onMoved: fanCard.draftSpeed = Math.max(0, Math.min(100, value))
                            onPressedChanged: {
                                if (pressed) {
                                    fanCard.draftSpeed = fanCard.speedValue
                                } else {
                                    fanCard.draftSpeed = Math.max(0, Math.min(100, value))
                                    root.fanSpeedRequested(fanCard.modelData.name, fanCard.draftSpeed)
                                }
                            }

                            background: Rectangle {
                                x: speedSlider.leftPadding
                                y: speedSlider.topPadding + speedSlider.availableHeight / 2 - height / 2
                                width: speedSlider.availableWidth
                                height: Math.max(12, Math.round(root.metrics.fontSize * 0.76))
                                radius: height / 2
                                color: "#101819"
                                border.color: "#536165"
                                border.width: 1

                                Rectangle {
                                    width: speedSlider.visualPosition * parent.width
                                    height: parent.height
                                    radius: parent.radius
                                    color: "#7f9298"
                                }
                            }

                            handle: Rectangle {
                                x: speedSlider.leftPadding + speedSlider.visualPosition * (speedSlider.availableWidth - width)
                                y: speedSlider.topPadding + speedSlider.availableHeight / 2 - height / 2
                                width: Math.max(38, Math.round(root.metrics.fontSize * 2.45))
                                height: width
                                radius: width / 2
                                color: speedSlider.pressed ? "#d4dde0" : "#aebdc2"
                                border.color: "#0b1112"
                                border.width: 2
                            }
                        }
                    }
                }
            }
        }
    }
}
