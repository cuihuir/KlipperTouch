import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property string printState: "standby"
    property string printFilename: ""
    property real printProgress: 0
    property string printMessage: ""
    property real printDuration: 0
    property real totalDuration: 0
    property real filamentUsed: 0
    property int currentLayer: 0
    property int totalLayers: 0
    property real requestedSpeed: 0
    property real speedFactor: 100
    property real extrudeFactor: 100
    property real zOffset: 0
    property real maxAccel: 0
    property real maxVelocity: 0
    property var temperatureModel: null
    property var fileModel: null
    property var excludeObjectNames: []
    property var excludedObjectNames: []
    property string currentObject: ""
    property string detailPage: "summary"
    signal zOffsetAdjustRequested(real delta)
    signal speedFactorAdjustRequested(real delta)
    signal extrudeFactorAdjustRequested(real delta)
    signal objectExcludeRequested(string objectName)

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

    function remainingLabel() {
        if (root.totalDuration <= 0 || root.printDuration <= 0) {
            return "-"
        }
        return root.durationLabel(Math.max(0, root.totalDuration - root.printDuration))
    }

    function filamentLabel() {
        return (root.filamentUsed / 1000).toFixed(1) + " m"
    }

    function layerLabel() {
        if (root.totalLayers > 0) {
            return root.currentLayer + " / " + root.totalLayers
        }
        if (root.currentLayer > 0) {
            return String(root.currentLayer)
        }
        return "-"
    }

    function percentLabel(value) {
        return Math.round(value) + "%"
    }

    function speedLabel(value) {
        if (value <= 0) {
            return "-"
        }
        return Math.round(value) + " mm/s"
    }

    function accelLabel() {
        if (root.maxAccel <= 0) {
            return "-"
        }
        return Math.round(root.maxAccel) + " mm/s^2"
    }

    function zOffsetLabel() {
        return root.zOffset.toFixed(2) + " mm"
    }

    function stateHeadline() {
        if (root.printState === "paused") {
            return "Paused"
        }
        if (root.printState === "complete") {
            return "Completed"
        }
        if (root.printState === "cancelled") {
            return "Cancelled"
        }
        if (root.printState === "error") {
            return "Printer error"
        }
        return "Printing"
    }

    function stateMessage() {
        if (root.printMessage.length > 0) {
            return root.printMessage
        }
        if (root.printState === "paused") {
            return "Print paused. Read-only status remains visible."
        }
        if (root.printState === "complete") {
            return "Print completed. Read-only summary remains visible."
        }
        if (root.printState === "cancelled") {
            return "Print cancelled. Read-only summary remains visible."
        }
        if (root.printState === "error") {
            return "Printer error reported. Read-only summary remains visible."
        }
        return "Read-only job status"
    }

    function stateAccentColor() {
        if (root.printState === "paused") {
            return Theme.color1
        }
        if (root.printState === "complete") {
            return "#4caf50"
        }
        if (root.printState === "cancelled") {
            return "#8d6e63"
        }
        if (root.printState === "error") {
            return "#d8615b"
        }
        return Theme.color2
    }

    function stateProgressValue() {
        if (root.printState === "complete") {
            return 1
        }
        return Math.max(0, Math.min(1, root.printProgress / 100))
    }

    function primaryActionLabel() {
        return root.printState === "paused" ? "Resume" : "Pause"
    }

    function readonlyActionHint(actionName) {
        return actionName + " is staged for the control layer."
    }

    // qmllint disable missing-property
    function goBack() {
        if (root.detailPage !== "summary") {
            root.detailPage = "summary"
            return true
        }
        return false
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
                    text: root.detailPage === "advanced"
                        ? "Advanced tuning"
                        : root.detailPage === "exclude"
                            ? "Object exclusion"
                        : root.printFilename.length > 0 ? root.printFilename : "Job Status"
                    elide: Text.ElideMiddle
                    font.bold: true
                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.15))
                }

                Label {
                    visible: root.detailPage === "summary"
                    color: root.stateAccentColor()
                    text: root.stateHeadline()
                    horizontalAlignment: Text.AlignRight
                    font.bold: true
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.86))
                }
            }

            Rectangle {
                visible: root.detailPage === "summary"
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(118, Math.round(root.metrics.fontSize * 8.2))
                color: "#101617"
                border.color: root.stateAccentColor()
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                    Rectangle {
                        Layout.preferredWidth: Math.max(96, Math.round(root.metrics.fontSize * 6.8))
                        Layout.fillHeight: true
                        visible: jobThumbnail.source.toString().length > 0
                        color: "#0b1112"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.25)

                        Image {
                            id: jobThumbnail
                            anchors.fill: parent
                            anchors.margins: 2
                            source: root.fileModel && root.fileModel.thumbnailRevision >= 0
                                ? root.fileModel.filePreviewThumbnailUrlFor(root.printFilename)
                                : ""
                            fillMode: Image.PreserveAspectFit
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.stateMessage()
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                        }

                        ProgressBar {
                            Layout.fillWidth: true
                            value: root.stateProgressValue()
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))

                            Repeater {
                                model: [
                                    {"label": "Z", "value": root.zOffsetLabel()},
                                    {"label": "Speed", "value": root.percentLabel(root.speedFactor)},
                                    {"label": "Flow", "value": root.percentLabel(root.extrudeFactor)}
                                ]

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: Math.max(28, Math.round(root.metrics.fontSize * 1.9))
                                    color: "#0b1112"
                                    border.color: "#263233"
                                    border.width: 1
                                    radius: Math.round(root.metrics.fontSize * 0.22)

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: Math.max(5, Math.round(root.metrics.fontSize * 0.35))
                                        anchors.rightMargin: anchors.leftMargin
                                        spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.25))

                                        Label {
                                            color: Theme.mutedText
                                            text: modelData.label
                                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                        }

                                        Label {
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            text: modelData.value
                                            horizontalAlignment: Text.AlignRight
                                            elide: Text.ElideRight
                                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                                        }
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: root.metrics.gap

                            Label {
                                Layout.fillWidth: true
                                color: root.stateAccentColor()
                                text: root.stateHeadline()
                                font.pixelSize: Math.max(20, Math.round(root.metrics.fontSize * 1.5))
                            }

                            Label {
                                color: Theme.mutedText
                                text: root.printState === "complete"
                                    ? "Done"
                                    : root.printState === "cancelled"
                                        ? "Stopped"
                                        : root.printState === "error"
                                            ? "Check printer"
                                            : root.remainingLabel() + " remaining"
                                horizontalAlignment: Text.AlignRight
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                            }
                        }
                    }
                }
            }

            GridLayout {
                id: jobActionGrid
                visible: root.detailPage === "summary"
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.7))
                columns: 4
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Button {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    text: root.primaryActionLabel()
                    enabled: false
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                }

                Button {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    text: "Cancel"
                    enabled: false
                    ToolTip.visible: hovered
                    ToolTip.text: root.readonlyActionHint(text)
                }

                Button {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    text: "Skip Object"
                    enabled: root.excludeObjectNames.length > 0
                    ToolTip.visible: hovered
                    ToolTip.text: enabled ? "Open object exclusion list" : "No object data"
                    onClicked: root.detailPage = "exclude"
                }

                Button {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    text: "Advanced"
                    onClicked: root.detailPage = "advanced"
                }
            }

            Rectangle {
                visible: root.detailPage === "summary"
                    && root.temperatureModel && root.temperatureModel.rowCount() > 0
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(58, Math.round(root.metrics.fontSize * 4.1))
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: root.metrics.gap
                    spacing: root.metrics.gap

                    Label {
                        color: Theme.mutedText
                        text: "Temperatures"
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        orientation: ListView.Horizontal
                        clip: true
                        spacing: root.metrics.gap
                        model: root.temperatureModel

                        delegate: Rectangle {
                            required property string displayName
                            required property var temperature
                            required property var target

                            width: Math.max(150, Math.round(root.metrics.fontSize * 10.8))
                            height: parent ? parent.height : Math.max(34, root.metrics.fontSize * 2.3)
                            color: "#0b1112"
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.25)

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: Math.max(5, Math.round(root.metrics.fontSize * 0.35))
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: displayName
                                    elide: Text.ElideRight
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.text
                                    text: (typeof temperature === "undefined" || temperature === null
                                        ? "--"
                                        : Math.round(temperature) + "°")
                                        + " / "
                                        + (typeof target === "undefined" || target === null
                                            ? "--"
                                            : Math.round(target) + "°")
                                    elide: Text.ElideRight
                                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.92))
                                }
                            }
                        }
                    }
                }
            }

            GridView {
                id: cardGrid
                visible: root.detailPage === "summary"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                flickDeceleration: 2600
                cellWidth: width / (root.metrics.portrait ? 1 : 2)
                cellHeight: Math.max(60, Math.round(root.metrics.fontSize * 4.25))
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
                model: [
                    {"label": "Elapsed", "value": root.durationLabel(root.printDuration)},
                    {"label": "Remaining", "value": root.remainingLabel()},
                    {"label": "Total", "value": root.durationLabel(root.totalDuration)},
                    {"label": "File size", "value": root.fileModel ? root.fileModel.fileSizeLabelFor(root.printFilename) : "-"},
                    {"label": "Modified", "value": root.fileModel ? root.fileModel.fileModifiedLabelFor(root.printFilename) : "-"},
                    {"label": "Path", "value": root.fileModel ? root.fileModel.filePathFor(root.printFilename) : ""},
                    {"label": "Layer", "value": root.layerLabel()},
                    {"label": "Filament used", "value": root.filamentLabel()},
                    {"label": "Speed", "value": root.speedLabel(root.requestedSpeed)},
                    {"label": "Speed factor", "value": root.percentLabel(root.speedFactor)},
                    {"label": "Flow", "value": root.percentLabel(root.extrudeFactor)},
                    {"label": "Z offset", "value": root.zOffsetLabel()},
                    {"label": "Accel", "value": root.accelLabel()},
                    {"label": "Max velocity", "value": root.speedLabel(root.maxVelocity)},
                    {"label": "State", "value": root.printState},
                    {"label": "Mode", "value": "readonly"}
                ]

                delegate: Rectangle {
                    required property var modelData

                    width: cardGrid.cellWidth - root.metrics.gap
                    height: cardGrid.cellHeight - root.metrics.gap
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: modelData.label
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: modelData.value
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                        }
                    }
                }
            }

            ColumnLayout {
                id: advancedPage
                visible: root.detailPage === "advanced"
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Repeater {
                    model: [
                        {
                            "label": "Z offset",
                            "value": root.zOffsetLabel(),
                            "minus": "-0.05",
                            "plus": "+0.05",
                            "negativeDelta": -0.05,
                            "positiveDelta": 0.05,
                            "target": "z"
                        },
                        {
                            "label": "Speed factor",
                            "value": root.percentLabel(root.speedFactor),
                            "minus": "-5%",
                            "plus": "+5%",
                            "negativeDelta": -5,
                            "positiveDelta": 5,
                            "target": "speed"
                        },
                        {
                            "label": "Extrude factor",
                            "value": root.percentLabel(root.extrudeFactor),
                            "minus": "-5%",
                            "plus": "+5%",
                            "negativeDelta": -5,
                            "positiveDelta": 5,
                            "target": "extrude"
                        }
                    ]

                    Rectangle {
                        id: adjustmentCard
                        property string adjustmentTarget: modelData.target

                        Layout.fillWidth: true
                        Layout.preferredHeight: Math.max(78, Math.round(root.metrics.fontSize * 5.6))
                        color: "#101617"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: root.metrics.gap
                            spacing: root.metrics.gap

                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: modelData.label
                                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: Theme.text
                                    text: modelData.value
                                    verticalAlignment: Text.AlignVCenter
                                    font.bold: true
                                    font.pixelSize: Math.max(20, Math.round(root.metrics.fontSize * 1.45))
                                }
                            }

                            Repeater {
                                model: [
                                    {"text": modelData.minus, "delta": modelData.negativeDelta},
                                    {"text": modelData.plus, "delta": modelData.positiveDelta}
                                ]

                                Button {
                                    Layout.preferredWidth: Math.max(74, Math.round(root.metrics.fontSize * 5.2))
                                    Layout.fillHeight: true
                                    text: modelData.text
                                    onClicked: {
                                        if (adjustmentCard.adjustmentTarget === "z") {
                                            root.zOffsetAdjustRequested(modelData.delta)
                                        } else if (adjustmentCard.adjustmentTarget === "speed") {
                                            root.speedFactorAdjustRequested(modelData.delta)
                                        } else if (adjustmentCard.adjustmentTarget === "extrude") {
                                            root.extrudeFactorAdjustRequested(modelData.delta)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                GridLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(80, Math.round(root.metrics.fontSize * 5.4))
                    columns: root.metrics.portrait ? 1 : 3
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: [
                            {"label": "Requested speed", "value": root.speedLabel(root.requestedSpeed)},
                            {"label": "Max accel", "value": root.accelLabel()},
                            {"label": "Max velocity", "value": root.speedLabel(root.maxVelocity)}
                        ]

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#0b1112"
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.32)

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: root.metrics.gap
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: modelData.label
                                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.text
                                    text: modelData.value
                                    elide: Text.ElideRight
                                    font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                                }
                            }
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "Buttons emit adjustment requests only; Moonraker control commands are intentionally not connected yet."
                    wrapMode: Text.WordWrap
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                }
            }

            ColumnLayout {
                id: excludePage
                visible: root.detailPage === "exclude"
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(64, Math.round(root.metrics.fontSize * 4.6))
                    color: "#101617"
                    border.color: root.currentObject.length > 0 ? Theme.color4 : "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: 0

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: "Current object"
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.currentObject.length > 0 ? root.currentObject : "-"
                            elide: Text.ElideMiddle
                            font.bold: true
                            font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.12))
                        }
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: root.metrics.gap
                    model: root.excludeObjectNames
                    boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: Math.max(58, Math.round(root.metrics.fontSize * 4.1))
                        color: root.excludedObjectNames.indexOf(modelData) >= 0
                            ? "#171717"
                            : "#101617"
                        border.color: modelData === root.currentObject ? Theme.color4 : "#263233"
                        border.width: modelData === root.currentObject ? 2 : 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: root.metrics.gap
                            spacing: root.metrics.gap

                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 0

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.text
                                    text: String(modelData)
                                    elide: Text.ElideMiddle
                                    font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: root.excludedObjectNames.indexOf(modelData) >= 0
                                        ? "Excluded"
                                        : modelData === root.currentObject ? "Printing now" : "Available"
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }
                            }

                            Button {
                                Layout.preferredWidth: Math.max(112, Math.round(root.metrics.fontSize * 7.8))
                                Layout.fillHeight: true
                                text: "Skip"
                                enabled: root.excludedObjectNames.indexOf(modelData) < 0
                                onClicked: root.objectExcludeRequested(modelData)
                            }
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: "Skip buttons emit objectExcludeRequested only; Moonraker exclude commands are intentionally not connected yet."
                    wrapMode: Text.WordWrap
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                }
            }
        }
    }
}
