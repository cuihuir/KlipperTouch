import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Rectangle {
    id: root
    required property var metrics
    property string printState: "standby"
    property string printFilename: ""
    property real printProgress: 0
    property string requestedPrintState: ""
    property var fileModel: null
    signal pauseRequested()
    signal resumeRequested()
    signal cancelRequested()
    signal tapped()

    color: tileMouseArea.pressed ? "#182124" : Theme.buttonsBg
    scale: tileMouseArea.pressed ? 0.97 : 1.0
    border.color: tileMouseArea.pressed ? Theme.text : root.stateAccent()
    border.width: Math.max(2, Math.round(root.metrics.fontSize * 0.12))
    radius: Math.round(root.metrics.fontSize)
    Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
    Behavior on color { ColorAnimation { duration: 80 } }
    Behavior on border.color { ColorAnimation { duration: 80 } }

    function effectivePrintState() {
        if (root.requestedPrintState === "printing" && root.printState === "standby") {
            return "starting"
        }
        if (root.requestedPrintState === "printing" && root.printState === "paused") {
            return "resuming"
        }
        if (root.requestedPrintState === "paused" && root.printState === "printing") {
            return "pausing"
        }
        if (root.requestedPrintState === "cancelled"
                && (root.printState === "printing" || root.printState === "paused")) {
            return "cancelling"
        }
        if (root.requestedPrintState === "standby"
                && (root.printState === "complete" || root.printState === "cancelled" || root.printState === "error")) {
            return "clearing"
        }
        if (root.printState === "complete" || root.printState === "cancelled"
                || root.printState === "error" || root.printState === "paused") {
            return root.printState
        }
        return root.requestedPrintState.length > 0 ? root.requestedPrintState : root.printState
    }

    function isTransitionalState(state) {
        return state === "starting" || state === "pausing"
            || state === "resuming" || state === "cancelling"
            || state === "clearing"
    }

    function stateAccent() {
        var s = root.effectivePrintState()
        if (s === "printing") return "#66ffb2"
        if (s === "paused") return "#ffd54f"
        if (s === "complete") return "#4dd0e1"
        if (s === "cancelled") return "#ff8a65"
        if (s === "error") return "#ff5252"
        return "#d46900"
    }

    function stateLabel() {
        var s = root.effectivePrintState()
        if (s === "printing") return "Printing"
        if (s === "paused") return "Paused"
        if (s === "complete") return "Done"
        if (s === "cancelled") return "Stopped"
        if (s === "error") return "Error"
        if (s === "pausing") return "Pausing..."
        if (s === "resuming") return "Resuming..."
        if (s === "cancelling") return "Cancelling..."
        if (s === "clearing") return "Clearing..."
        if (s === "starting") return "Starting..."
        return ""
    }

    function progressValue() {
        if (root.printState === "complete") return 1
        return Math.max(0, Math.min(1, root.printProgress / 100))
    }

    function buttonWidth() {
        return Math.max(180, Math.round(root.metrics.fontSize * 14))
    }

    function buttonHeight() {
        return Math.max(44, Math.round(root.metrics.fontSize * 2.8))
    }

    // Navigation MouseArea — covers the whole component
    MouseArea {
        id: tileMouseArea
        anchors.fill: parent
        onClicked: root.tapped()
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: Math.max(4, Math.round(root.metrics.fontSize * 0.3))
        spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.5))

        // Thumbnail
        Rectangle {
            id: thumbnailFrame
            Layout.fillHeight: true
            Layout.preferredWidth: height
            color: "#0b1112"
            border.color: "#3b4648"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.34)
            clip: true

            Image {
                id: thumbnailImage
                anchors.fill: parent
                anchors.margins: 3
                source: root.fileModel && root.fileModel.thumbnailRevision >= 0
                    ? root.fileModel.filePreviewThumbnailUrlFor(root.printFilename)
                    : ""
                fillMode: Image.PreserveAspectFit
                asynchronous: source.toString().indexOf("file:") !== 0
                cache: true
                sourceSize.width: width
                sourceSize.height: height
                visible: source.toString().length > 0 && thumbnailImage.status === Image.Ready
            }

            ColumnLayout {
                visible: !thumbnailImage.visible
                anchors.centerIn: parent
                width: parent.width - root.metrics.gap * 2
                spacing: 0

                Label {
                    Layout.fillWidth: true
                    color: "#8b9496"
                    text: "G"
                    horizontalAlignment: Text.AlignHCenter
                    font.bold: true
                    font.pixelSize: Math.max(28, Math.round(root.metrics.fontSize * 2.2))
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "G-code"
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.65))
                }
            }
        }

        // Info + Controls column
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Math.max(4, Math.round(root.metrics.gap * 0.5))

            // State label + filename
            RowLayout {
                Layout.fillWidth: true
                spacing: root.metrics.gap

                Rectangle {
                    Layout.preferredWidth: stateLabelItem.implicitWidth + Math.round(root.metrics.fontSize * 2.0)
                    Layout.preferredHeight: Math.max(28, Math.round(root.metrics.fontSize * 1.8))
                    color: {
                        var s = root.effectivePrintState()
                        if (s === "printing") return Qt.rgba(0.12, 0.50, 0.32, 0.95)
                        if (s === "paused") return Qt.rgba(0.55, 0.45, 0.20, 0.9)
                        if (s === "complete") return Qt.rgba(0.15, 0.45, 0.55, 0.9)
                        if (s === "cancelled") return Qt.rgba(0.50, 0.25, 0.20, 0.9)
                        if (s === "error") return Qt.rgba(0.60, 0.18, 0.15, 0.95)
                        return "#101617"
                    }
                    border.color: root.stateAccent()
                    border.width: 1
                    radius: height / 2

                    Label {
                        id: stateLabelItem
                        anchors.centerIn: parent
                        color: root.stateAccent()
                        text: root.stateLabel()
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.bold: true
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                    }
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: root.printFilename.length > 0 ? root.printFilename : "No active file"
                    elide: Text.ElideMiddle
                    font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.0))
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Progress bar + percentage
            RowLayout {
                Layout.fillWidth: true
                spacing: Math.max(6, Math.round(root.metrics.gap * 0.7))

                ProgressBar {
                    id: liteProgressBar
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(22, Math.round(root.metrics.fontSize * 1.4))
                    value: root.progressValue()
                    background: Rectangle {
                        color: "#172426"
                        radius: height / 2
                    }
                    contentItem: Item {
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: Math.max(height, liteProgressBar.visualPosition * parent.width)
                            radius: height / 2
                            color: root.stateAccent()
                        }
                    }
                }

                Label {
                    color: Theme.text
                    text: Math.round(root.progressValue() * 100) + "%"
                    font.bold: true
                    font.pixelSize: Math.max(28, Math.round(root.metrics.fontSize * 2.0))
                    verticalAlignment: Text.AlignVCenter
                    Layout.preferredWidth: Math.max(70, Math.round(root.metrics.fontSize * 4.5))
                    horizontalAlignment: Text.AlignRight
                }
            }

            // Action buttons
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Math.max(8, Math.round(root.metrics.gap))

                Item { Layout.fillWidth: true }

                // Pause/Resume button
                Rectangle {
                    id: pauseResumeButton
                    Layout.preferredWidth: root.buttonWidth()
                    Layout.preferredHeight: root.buttonHeight()
                    Layout.alignment: Qt.AlignVCenter
                    radius: Math.round(root.metrics.fontSize * 0.5)
                    color: pauseMouseArea.pressed ? Qt.darker(pauseButtonColor, 1.3) : pauseButtonColor
                    border.color: Qt.lighter(pauseButtonColor, 1.4)
                    border.width: 2
                    visible: root.printState === "printing" || root.printState === "paused"
                    enabled: !root.isTransitionalState(root.effectivePrintState())
                    opacity: enabled ? 1.0 : 0.4

                    property color pauseButtonColor: {
                        var s = root.effectivePrintState()
                        if (s === "paused" || s === "resuming") return Qt.rgba(0.12, 0.50, 0.32, 0.95)
                        return Qt.rgba(0.55, 0.45, 0.20, 0.9)
                    }

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: Math.max(4, Math.round(root.metrics.gap * 0.5))

                        Image {
                            Layout.preferredWidth: Math.round(pauseResumeButton.height * 0.45)
                            Layout.preferredHeight: Layout.preferredWidth
                            source: {
                                var s = root.effectivePrintState()
                                return Theme.iconSource(s === "paused" || s === "resuming" ? "resume" : "pause")
                            }
                            fillMode: Image.PreserveAspectFit
                            sourceSize.width: width
                            sourceSize.height: height
                            opacity: pauseResumeButton.enabled ? 1.0 : 0.4
                        }

                        Label {
                            color: Theme.text
                            text: {
                                var s = root.effectivePrintState()
                                return (s === "paused" || s === "resuming") ? "Resume" : "Pause"
                            }
                            font.bold: true
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.0))
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    MouseArea {
                        id: pauseMouseArea
                        anchors.fill: parent
                        enabled: parent.enabled
                        onClicked: {
                            var s = root.effectivePrintState()
                            if (s === "paused" || s === "resuming") {
                                root.resumeRequested()
                            } else {
                                root.pauseRequested()
                            }
                        }
                    }
                }

                // Cancel button — only visible when paused
                Rectangle {
                    id: cancelButton
                    Layout.preferredWidth: root.buttonWidth()
                    Layout.preferredHeight: root.buttonHeight()
                    Layout.alignment: Qt.AlignVCenter
                    radius: Math.round(root.metrics.fontSize * 0.5)
                    color: cancelMouseArea.pressed ? Qt.darker(Qt.rgba(0.50, 0.25, 0.20, 0.9), 1.3) : Qt.rgba(0.50, 0.25, 0.20, 0.9)
                    border.color: "#ff8a65"
                    border.width: 2
                    visible: root.printState === "paused"
                    enabled: !root.isTransitionalState(root.effectivePrintState())
                    opacity: enabled ? 1.0 : 0.4

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: Math.max(4, Math.round(root.metrics.gap * 0.5))

                        Image {
                            Layout.preferredWidth: Math.round(cancelButton.height * 0.45)
                            Layout.preferredHeight: Layout.preferredWidth
                            source: Theme.iconSource("cancel")
                            fillMode: Image.PreserveAspectFit
                            sourceSize.width: width
                            sourceSize.height: height
                            opacity: cancelButton.enabled ? 1.0 : 0.4
                        }

                        Label {
                            color: Theme.text
                            text: "Cancel"
                            font.bold: true
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.0))
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    MouseArea {
                        id: cancelMouseArea
                        anchors.fill: parent
                        enabled: parent.enabled
                        onClicked: root.cancelRequested()
                    }
                }

                Item { Layout.fillWidth: true }
            }
        }
    }
}
