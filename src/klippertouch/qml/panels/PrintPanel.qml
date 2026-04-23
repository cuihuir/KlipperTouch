import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var fileModel: null
    property var activeFileModel: fileModel

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
