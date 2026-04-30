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
    property bool connecting: false
    property bool ready: false
    property string activeDetailText: root.detail()
    property int detailPageIndex: 0
    property string recoveryPage: "main"
    property bool compactVertical: root.height < 380
    property int recoveryColumns: root.width > 680 ? 4 : root.width > 420 ? 2 : 1
    property int recoveryRows: Math.ceil(root.recoveryActionCount() / root.recoveryColumns)
    property int recoveryNavHeight: root.recoveryRows === 1
        ? Math.max(72, Math.round(root.metrics.fontSize * 4.4))
        : Math.max(106, Math.round(root.metrics.fontSize * 6.2))
    signal recoveryActionRequested(string action)
    onActiveDetailTextChanged: root.setDetailPageIndex(0)
    onDetailPageIndexChanged: messagePager.setCurrentIndex(root.detailPageIndex)

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
        if (root.ready) {
            return "Printer is ready"
        }
        if (root.connecting) {
            return "Connecting..."
        }
        return ""
    }

    function headline() {
        if (root.ready) {
            return "Printer is ready"
        }
        if (root.connecting) {
            if (root.moonrakerOffline()) {
                return "Connecting to Moonraker"
            }
            return "Connecting to printer"
        }
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
        if (root.ready) {
            return "Preparing interface..."
        }
        if (root.connecting) {
            if (root.moonrakerOffline()) {
                return "Waiting for Moonraker. KlipperTouch will continue when Moonraker responds."
            }
            return "Waiting for Klippy ready. Current state: " + root.klippyState
        }
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

    function detailPageSize() {
        if (root.compactVertical) {
            return 150
        }
        if (root.width < 620) {
            return 210
        }
        if (root.height < 520) {
            return 280
        }
        return 480
    }

    function detailPageCount() {
        return Math.max(1, Math.ceil(root.activeDetailText.length / root.detailPageSize()))
    }

    function pagerPageCount() {
        return root.detailPageCount() + 1
    }

    function detailPageText(pageIndex) {
        var pageSize = root.detailPageSize()
        return root.activeDetailText.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize)
    }

    function setDetailPageIndex(pageIndex) {
        root.detailPageIndex = Math.max(0, Math.min(pageIndex, root.pagerPageCount() - 1))
    }

    function recoveryActionModel() {
        if (root.recoveryPage === "shutdown") {
            return [
                {"label": "Back", "action": "recovery_main", "placeholder": false, "hint": "Return"},
                {"label": "KlipperTouch Restart", "action": "placeholder", "placeholder": true, "hint": "Soon"},
                {"label": "System Shutdown", "action": "placeholder", "placeholder": true, "hint": "Soon"},
                {"label": "System Restart", "action": "placeholder", "placeholder": true, "hint": "Soon"}
            ]
        }
        return [
            {"label": "Firmware Restart", "action": "firmware_restart", "placeholder": false, "hint": "Send"},
            {"label": "Restart Klipper", "action": "restart_klipper", "placeholder": false, "hint": "Send"},
            {"label": "Retry", "action": "retry", "placeholder": false, "hint": "Send"},
            {"label": "Shutdown", "action": "shutdown_menu", "placeholder": false, "hint": "Open"}
        ]
    }

    function recoveryActionCount() {
        return root.recoveryActionModel().length
    }

    function handleRecoveryAction(action) {
        if (action === "shutdown_menu") {
            root.recoveryPage = "shutdown"
            return
        }
        if (action === "recovery_main") {
            root.recoveryPage = "main"
            return
        }
        if (action === "placeholder") {
            return
        }
        root.recoveryActionRequested(action)
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

    Item {
        id: displayArea
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: recoveryNavBar.top
        anchors.margins: root.metrics.margin

        SwipeView {
            id: messagePager
            currentIndex: root.detailPageIndex
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: pagerControls.top
            anchors.bottomMargin: Math.max(2, Math.round(root.metrics.gap * 0.25))
            clip: true
            interactive: false

            Repeater {
                model: root.detailPageCount()

                Item {
                    required property int index

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: root.compactVertical ? Math.max(5, Math.round(root.metrics.gap * 0.45)) : Math.max(8, root.metrics.gap * 0.85)

                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: Math.max(48, Math.round(root.metrics.fontSize * 3.2))
                            Layout.preferredHeight: Math.max(48, Math.round(root.metrics.fontSize * 3.2))
                            visible: !root.compactVertical && index === 0
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
                            text: index === 0
                                ? root.headline()
                                : root.headline() + " (" + (index + 1) + "/" + root.detailPageCount() + ")"
                            color: Theme.text
                            font.pixelSize: root.compactVertical
                                ? Math.max(18, Math.round(root.metrics.fontSize * 1.05))
                                : Math.max(20, Math.round(root.metrics.fontSize * 1.35))
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 0
                            radius: Math.round(root.metrics.fontSize * 0.35)
                            color: "#0b1416"
                            border.color: "#2f3a3e"
                            border.width: 1
                            clip: true

                            Label {
                                id: detailLabel
                                anchors.fill: parent
                                anchors.margins: root.metrics.gap
                                text: root.detailPageText(index)
                                color: Theme.mutedText
                                font.pixelSize: root.compactVertical
                                    ? Math.max(10, Math.round(root.metrics.fontSize * 0.64))
                                    : Math.max(12, Math.round(root.metrics.fontSize * 0.82))
                                horizontalAlignment: Text.AlignLeft
                                verticalAlignment: Text.AlignTop
                                wrapMode: Text.WordWrap
                                clip: true
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.max(38, recoveryLabel.implicitHeight + root.metrics.gap)
                            radius: Math.round(root.metrics.fontSize * 0.28)
                            color: root.controlError.length > 0 ? "#221719" : "#121b1d"
                            border.color: root.controlError.length > 0 ? "#80676a" : "#344044"
                            border.width: 1
                            visible: root.recoveryStatusText().length > 0 && index === root.detailPageCount() - 1

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
                    }
                }
            }

            Item {
                id: servicePage

                Rectangle {
                    anchors.fill: parent
                    radius: Math.round(root.metrics.fontSize * 0.35)
                    color: "#0c1517"
                    border.color: "#2f3a3e"
                    border.width: 1

                    ColumnLayout {
                        id: statusColumn
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(6, Math.round(root.metrics.gap * 0.65))

                        Label {
                            text: "Host"
                            color: Theme.mutedText
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                            Layout.fillWidth: true
                        }

                        Label {
                            text: root.hostname
                            color: Theme.text
                            font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.25))
                            font.bold: true
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        Label {
                            text: "Klippy: " + root.klippyState
                            color: Theme.text
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.95))
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        Label {
                            text: "Moonraker: " + root.moonrakerVersion
                            color: Theme.text
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.95))
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        Label {
                            text: "Printer movement controls are unavailable while recovery is active."
                            color: "#9aa7ad"
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            verticalAlignment: Text.AlignBottom
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }

        Row {
            id: pagerControls
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            spacing: Math.max(6, Math.round(root.metrics.gap * 0.5))
            visible: root.pagerPageCount() > 1

            Rectangle {
                width: Math.max(38, Math.round(root.metrics.fontSize * 2.4))
                height: Math.max(30, Math.round(root.metrics.fontSize * 1.8))
                radius: Math.round(height * 0.28)
                color: previousPageArea.pressed ? "#182124" : "#101819"
                border.color: root.detailPageIndex > 0 ? "#667276" : "#394346"
                border.width: 1
                opacity: root.detailPageIndex > 0 ? 1.0 : 0.42

                Label {
                    anchors.centerIn: parent
                    text: "<"
                    color: Theme.text
                    font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.95))
                }

                MouseArea {
                    id: previousPageArea
                    anchors.fill: parent
                    enabled: root.detailPageIndex > 0
                    onClicked: root.setDetailPageIndex(root.detailPageIndex - 1)
                }
            }

            PageIndicator {
                id: pagerIndicator
                anchors.verticalCenter: parent.verticalCenter
                count: root.pagerPageCount()
                currentIndex: root.detailPageIndex
            }

            Rectangle {
                width: Math.max(38, Math.round(root.metrics.fontSize * 2.4))
                height: Math.max(30, Math.round(root.metrics.fontSize * 1.8))
                radius: Math.round(height * 0.28)
                color: nextPageArea.pressed ? "#182124" : "#101819"
                border.color: root.detailPageIndex < root.pagerPageCount() - 1 ? "#667276" : "#394346"
                border.width: 1
                opacity: root.detailPageIndex < root.pagerPageCount() - 1 ? 1.0 : 0.42

                Label {
                    anchors.centerIn: parent
                    text: ">"
                    color: Theme.text
                    font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.95))
                }

                MouseArea {
                    id: nextPageArea
                    anchors.fill: parent
                    enabled: root.detailPageIndex < root.pagerPageCount() - 1
                    onClicked: root.setDetailPageIndex(root.detailPageIndex + 1)
                }
            }
        }
    }

    Rectangle {
        id: recoveryNavBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: root.metrics.margin
        height: root.recoveryNavHeight
        radius: Math.round(root.metrics.fontSize * 0.36)
        color: "#081011"
        border.color: "#263235"
        border.width: 1

        GridLayout {
            id: recoveryActions
            anchors.fill: recoveryNavBar
            anchors.margins: root.metrics.gap
            columns: root.recoveryColumns
            rowSpacing: root.compactVertical ? Math.max(5, Math.round(root.metrics.gap * 0.5)) : root.metrics.gap
            columnSpacing: root.metrics.gap

            Repeater {
                model: root.recoveryActionModel()

                Rectangle {
                    required property string label
                    required property string action
                    required property bool placeholder
                    required property string hint

                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 0
                    radius: Math.round(height * 0.18)
                    color: recoveryPressArea.pressed ? "#182124" : placeholder ? "#141b1d" : "#1a2528"
                    scale: recoveryPressArea.pressed ? 0.97 : 1.0
                    border.color: recoveryPressArea.pressed ? Theme.text : placeholder ? "#3d474a" : "#667276"
                    border.width: 1
                    Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
                    Behavior on color { ColorAnimation { duration: 80 } }
                    Behavior on border.color { ColorAnimation { duration: 80 } }

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
                            text: hint
                            color: "#9aa7ad"
                            font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.6))
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                        }
                    }

                    MouseArea {
                        id: recoveryPressArea
                        anchors.fill: parent
                        onClicked: root.handleRecoveryAction(action)
                    }
                }
            }
        }
    }
}
