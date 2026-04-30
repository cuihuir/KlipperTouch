import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var notificationModel: null

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
            spacing: root.metrics.gap

            Label {
                text: "Notification Center"
                color: Theme.text
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.15))
                font.bold: true
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            TactileButton {
                Layout.preferredWidth: Math.max(110, Math.round(root.metrics.fontSize * 6.8))
                Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 2.75))
                enabled: root.notificationModel !== null
                text: "Mark read"
                fontSize: root.metrics.fontSize
                baseColor: "#182224"
                pressedColor: "#203236"
                accentColor: "#465154"
                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                onClicked: notificationModel.markAllRead()
            }

            TactileButton {
                Layout.preferredWidth: Math.max(88, Math.round(root.metrics.fontSize * 5.4))
                Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 2.75))
                enabled: root.notificationModel !== null
                text: "Clear"
                fontSize: root.metrics.fontSize
                baseColor: "#182224"
                pressedColor: "#203236"
                accentColor: "#465154"
                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                onClicked: notificationModel.clear()
            }
        }

        Label {
            text: "No notifications"
            color: Theme.mutedText
            font.pixelSize: root.metrics.fontSize
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !root.notificationModel || root.notificationModel.count <= 0
        }

        ListView {
            id: notificationList
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Math.max(8, Math.round(root.metrics.gap * 0.8))
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            model: root.notificationModel
            visible: root.notificationModel && root.notificationModel.count > 0

            delegate: Rectangle {
                required property string level
                required property string title
                required property string message
                required property string source
                required property string timestamp
                required property bool read
                required property bool sticky
                required property string actionPanel

                width: notificationList.width
                height: Math.max(76, contentColumn.implicitHeight + root.metrics.gap * 1.2)
                radius: Math.round(root.metrics.fontSize * 0.35)
                color: read ? "#0c1517" : "#111d20"
                border.color: level === "error" ? "#7d8588" : "#344044"
                border.width: read ? 1 : 2

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Math.max(10, Math.round(root.metrics.gap * 0.9))
                    spacing: root.metrics.gap

                    Rectangle {
                        Layout.preferredWidth: Math.max(8, Math.round(root.metrics.fontSize * 0.42))
                        Layout.fillHeight: true
                        radius: width / 2
                        color: level === "error" ? "#a8b0b3" : "#5f6b70"
                    }

                    ColumnLayout {
                        id: contentColumn
                        Layout.fillWidth: true
                        spacing: Math.max(2, Math.round(root.metrics.gap * 0.25))

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: root.metrics.gap

                            Label {
                                text: title
                                color: Theme.text
                                font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize * 0.9))
                                font.bold: !read
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }

                            Label {
                                text: timestamp
                                color: Theme.mutedText
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.68))
                            }
                        }

                        Label {
                            text: message
                            color: Theme.mutedText
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.75))
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                            visible: message.length > 0
                        }

                        Label {
                            text: source.length > 0 ? source : "system"
                            color: "#9aa7ad"
                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.66))
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }
    }
}
