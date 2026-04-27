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
    property string controlStatus: ""
    property string controlError: ""
    signal recoveryActionRequested(string action)

    function moonrakerOffline() {
        return root.moonrakerVersion.length <= 0 || root.moonrakerVersion === "unknown"
    }

    function webhooksShutdown() {
        return root.webhooksState === "shutdown"
            || root.webhooksMessage.indexOf("Shutdown due to webhooks") >= 0
    }

    function recoveryStatusText() {
        if (root.controlError.length > 0) {
            return root.controlError
        }
        if (root.controlStatus.length > 0) {
            return root.controlStatus
        }
        if (root.webhooksState === "disconnected") {
            return "Moonraker disconnected"
        }
        if (root.webhooksState === "startup") {
            return "Klipper is attempting to start"
        }
        if (root.webhooksState === "ready") {
            return "Printer is ready"
        }
        return root.webhooksMessage
    }

    function headline() {
        if (root.moonrakerOffline()) {
            return "Moonraker offline"
        }
        if (root.webhooksState === "disconnected") {
            return "Moonraker disconnected"
        }
        if (root.webhooksState === "startup") {
            return "Klipper is attempting to start"
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
        if (root.webhooksState === "disconnected" || root.webhooksState === "startup") {
            return root.recoveryStatusText()
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

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(40, recoveryLabel.implicitHeight + root.metrics.gap)
            radius: Math.round(root.metrics.fontSize * 0.28)
            color: root.controlError.length > 0 ? "#221719" : "#121b1d"
            border.color: root.controlError.length > 0 ? "#80676a" : "#344044"
            border.width: 1
            visible: root.recoveryStatusText().length > 0

            Label {
                id: recoveryLabel
                anchors.centerIn: parent
                width: parent.width - root.metrics.gap * 2
                text: root.recoveryStatusText()
                color: Theme.text
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
        }

        GridLayout {
            Layout.fillWidth: true
            columns: root.width > 720 ? 4 : 2
            rowSpacing: root.metrics.gap
            columnSpacing: root.metrics.gap

            Repeater {
                model: [
                    {"label": "Firmware Restart", "action": "firmware_restart", "placeholder": false},
                    {"label": "Restart Klipper", "action": "restart_klipper", "placeholder": false},
                    {"label": "Restart Moonraker", "action": "restart_moonraker", "placeholder": true},
                    {"label": "Emergency Stop", "action": "emergency_stop", "placeholder": false}
                ]

                Rectangle {
                    required property string label
                    required property string action
                    required property bool placeholder

                    Layout.fillWidth: true
                    Layout.minimumHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.2))
                    Layout.preferredHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.2))
                    radius: Math.round(height * 0.18)
                    color: placeholder ? "#141b1d" : "#1a2528"
                    border.color: placeholder ? "#3d474a" : "#667276"
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        width: parent.width - root.metrics.gap
                        spacing: 2

                        Label {
                            width: parent.width
                            text: label
                            color: Theme.text
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                            font.bold: !placeholder
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                        }

                        Label {
                            width: parent.width
                            text: placeholder ? "Soon" : "Send"
                            color: "#9aa7ad"
                            font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.6))
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.recoveryActionRequested(action)
                    }
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
