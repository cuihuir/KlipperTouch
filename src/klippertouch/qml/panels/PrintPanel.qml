import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var fileModel: null
    property var activeFileModel: fileModel
    property string printState: "standby"
    property string printFilename: ""
    property real printProgress: 0
    property string printMessage: ""
    property real printDuration: 0
    property real totalDuration: 0

    function durationLabel(seconds) {
        var safeSeconds = Math.max(0, Math.round(seconds))
        var minutes = Math.floor(safeSeconds / 60)
        var hours = Math.floor(minutes / 60)
        minutes = minutes % 60
        if (hours > 0) {
            return hours + "h " + minutes + "m"
        }
        return minutes + "m"
    }

    Rectangle {
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

            RowLayout {
                Layout.fillWidth: true
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "G-Code files"
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    color: Theme.mutedText
                    text: "readonly"
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(92, Math.round(root.metrics.fontSize * 6.8))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.printFilename.length > 0 ? root.printFilename : "No active file"
                            elide: Text.ElideMiddle
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.02))
                        }

                        Label {
                            color: Theme.mutedText
                            text: root.printState
                            horizontalAlignment: Text.AlignRight
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.86))
                        }
                    }

                    ProgressBar {
                        Layout.fillWidth: true
                        value: Math.max(0, Math.min(1, root.printProgress / 100))
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.printMessage.length > 0 ? root.printMessage : "Read-only job status"
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            color: Theme.mutedText
                            text: Math.round(root.printProgress) + "% | " + root.durationLabel(root.printDuration)
                            horizontalAlignment: Text.AlignRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                visible: !root.metrics.portrait
                spacing: root.metrics.gap

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "File"
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                }

                Label {
                    Layout.preferredWidth: Math.max(72, Math.round(root.metrics.fontSize * 5.2))
                    color: Theme.mutedText
                    text: "Size"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                }

                Label {
                    Layout.preferredWidth: Math.max(76, Math.round(root.metrics.fontSize * 5.4))
                    color: Theme.mutedText
                    text: "Permissions"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                }
            }

            ListView {
                id: fileList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))
                model: root.activeFileModel

                delegate: Rectangle {
                    required property string path
                    required property string displayName
                    required property string sizeLabel
                    required property string permissions

                    width: fileList.width
                    height: Math.max(46, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 4.2 : 3.3)))
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    GridLayout {
                        anchors.fill: parent
                        anchors.leftMargin: root.metrics.gap
                        anchors.rightMargin: root.metrics.gap
                        columns: root.metrics.portrait ? 1 : 3
                        rowSpacing: 0
                        columnSpacing: root.metrics.gap

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: displayName
                            elide: Text.ElideMiddle
                            font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                        }

                        Label {
                            Layout.preferredWidth: root.metrics.portrait
                                ? fileList.width - root.metrics.gap * 2
                                : Math.max(72, Math.round(root.metrics.fontSize * 5.2))
                            color: Theme.mutedText
                            text: root.metrics.portrait ? path + " | " + sizeLabel : sizeLabel
                            elide: Text.ElideMiddle
                            horizontalAlignment: root.metrics.portrait ? Text.AlignLeft : Text.AlignRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.preferredWidth: Math.max(76, Math.round(root.metrics.fontSize * 5.4))
                            visible: !root.metrics.portrait
                            color: Theme.mutedText
                            text: permissions
                            horizontalAlignment: Text.AlignRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }
                    }
                }
            }
        }
    }
}
