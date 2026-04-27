import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property string hostname: "unknown"
    property string klippyState: "disconnected"
    property string moonrakerVersion: "unknown"
    property string webhooksState: ""
    property string webhooksMessage: ""

    function moonrakerOffline() {
        return root.moonrakerVersion.length <= 0 || root.moonrakerVersion === "unknown"
    }

    function webhooksShutdown() {
        return root.webhooksState === "shutdown"
            || root.webhooksMessage.indexOf("Shutdown due to webhooks") >= 0
    }

    function headline() {
        if (root.moonrakerOffline()) {
            return "Moonraker offline"
        }
        if (root.webhooksShutdown()) {
            return "Shutdown due to webhooks"
        }
        return "Klippy not ready"
    }

    function detail() {
        if (root.moonrakerOffline()) {
            return "KlipperTouch cannot reach Moonraker. Check host, network, and Moonraker service."
        }
        if (root.webhooksShutdown()) {
            return root.webhooksMessage.length > 0
                ? root.webhooksMessage
                : "Klippy reported Shutdown due to webhooks."
        }
        return "Current Klippy state: " + root.klippyState
    }

    Rectangle {
        anchors.fill: parent
        color: "#05090a"

        gradient: Gradient {
            GradientStop { position: 0.0; color: "#10191b" }
            GradientStop { position: 0.55; color: "#071112" }
            GradientStop { position: 1.0; color: "#030607" }
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(parent.width - root.metrics.margin * 2, Math.max(360, parent.width * 0.72))
        spacing: Math.max(12, root.metrics.gap * 1.2)

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: Math.max(64, Math.round(root.metrics.fontSize * 4.4))
            Layout.preferredHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.4))
            radius: width / 2
            color: "#151f22"
            border.color: "#637075"
            border.width: Math.max(2, Math.round(width * 0.035))

            Label {
                anchors.centerIn: parent
                text: "!"
                color: Theme.text
                font.pixelSize: Math.round(parent.width * 0.52)
                font.bold: true
            }
        }

        Label {
            text: root.headline()
            color: Theme.text
            font.pixelSize: Math.max(24, Math.round(root.metrics.fontSize * 1.75))
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        Label {
            text: root.detail()
            color: Theme.mutedText
            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.95))
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(72, statusColumn.implicitHeight + root.metrics.gap * 1.2)
            radius: Math.round(root.metrics.fontSize * 0.35)
            color: "#0c1517"
            border.color: "#2f3a3e"
            border.width: 1

            ColumnLayout {
                id: statusColumn
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: Math.max(3, Math.round(root.metrics.gap * 0.35))

                Label {
                    text: "Host: " + root.hostname
                    color: Theme.text
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.8))
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Label {
                    text: "Klippy: " + root.klippyState
                    color: Theme.text
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.8))
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Label {
                    text: "Moonraker: " + root.moonrakerVersion
                    color: Theme.text
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.8))
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }
        }

        Label {
            text: "No printer controls are available while this screen is active."
            color: "#9aa7ad"
            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }
}
