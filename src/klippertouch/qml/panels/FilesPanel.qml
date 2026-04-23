import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var fileModel: null
    property var activeFileModel: fileModel
    property string rootPath: "gcodes"
    property bool loading: false

    function modifiedLabel(value) {
        if (value <= 0) {
            return "-"
        }
        return new Date(value * 1000).toLocaleString(Qt.locale(), "yyyy-MM-dd hh:mm")
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

            GridLayout {
                Layout.fillWidth: true
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

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
                    horizontalAlignment: root.metrics.portrait ? Text.AlignLeft : Text.AlignRight
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(36, Math.round(root.metrics.fontSize * 2.55))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: root.metrics.gap
                    anchors.rightMargin: root.metrics.gap
                    spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                    Label {
                        color: Theme.mutedText
                        text: "Path"
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "/" + root.rootPath
                        elide: Text.ElideMiddle
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                    }

                    Label {
                        color: Theme.mutedText
                        text: root.loading ? "Loading files..." : fileList.count + " files"
                        horizontalAlignment: Text.AlignRight
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                    }
                }
            }

            Flow {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 2.2))
                spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                Repeater {
                    model: [
                        "Sort: Name  v",
                        "Sort: Date",
                        "Sort: Size",
                        "Refresh: auto"
                    ]

                    Rectangle {
                        width: chipText.implicitWidth + root.metrics.gap * 1.6
                        height: Math.max(30, Math.round(root.metrics.fontSize * 2.2))
                        color: modelData.indexOf("Name") >= 0 ? "#1b2b2e" : "#101617"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        Label {
                            id: chipText
                            anchors.centerIn: parent
                            color: Theme.mutedText
                            text: modelData
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
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
                    Layout.preferredWidth: Math.max(112, Math.round(root.metrics.fontSize * 8.2))
                    color: Theme.mutedText
                    text: "Modified"
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
                visible: count > 0

                delegate: Rectangle {
                    required property string path
                    required property string displayName
                    required property string sizeLabel
                    required property real modified
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
                        columns: root.metrics.portrait ? 1 : 4
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
                            text: root.metrics.portrait
                                ? path + " | " + sizeLabel + " | " + root.modifiedLabel(modified)
                                : sizeLabel
                            elide: Text.ElideMiddle
                            horizontalAlignment: root.metrics.portrait ? Text.AlignLeft : Text.AlignRight
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.preferredWidth: Math.max(112, Math.round(root.metrics.fontSize * 8.2))
                            visible: !root.metrics.portrait
                            color: Theme.mutedText
                            text: root.modifiedLabel(modified)
                            horizontalAlignment: Text.AlignRight
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

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: fileList.count === 0
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - root.metrics.gap * 2
                    spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: root.loading ? "Loading files..." : "No G-Code files found"
                        horizontalAlignment: Text.AlignHCenter
                        font.bold: true
                        font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.05))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: "Read-only file browser; print actions stay out of this page."
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }
                }
            }
        }
    }
}
