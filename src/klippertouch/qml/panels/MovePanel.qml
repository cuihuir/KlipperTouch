import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var moveButtons: [
        {"label": "Y+", "direction": "up"},
        {"label": "X-", "direction": "left"},
        {"label": "X+", "direction": "right"},
        {"label": "Y-", "direction": "down"},
        {"label": "Z+", "direction": "up"},
        {"label": "Z-", "direction": "down"}
    ]
    property var xyButtons: [
        {"label": "Y+", "direction": "up"},
        {"label": "X-", "direction": "left"},
        {"label": "X+", "direction": "right"},
        {"label": "Y-", "direction": "down"}
    ]
    property var zButtons: [
        {"label": "Z+", "direction": "up"},
        {"label": "Z-", "direction": "down"}
    ]
    property var actionButtons: [
        {"label": "Disable Motors", "action": "disable_motors", "hint": "M84", "icon": "⏻"},
        {"label": "More", "action": "more", "hint": "settings", "icon": "⋯"}
    ]
    property var portraitPlaceholders: [
        {"placeholder": true},
        {"placeholder": true}
    ]
    property var distances: [".1", ".5", "1", "5", "10", "25", "50"]
    property string selectedDistance: "10"
    property bool moreVisible: false
    property string detailPage: "main"
    property real positionX: 0
    property real positionY: 0
    property real positionZ: 0
    property real positionE: 0
    property string homedAxes: ""
    readonly property color selectedAccent: "#7f9298"
    signal moveActionRequested(string action)

    function selectDistance(distance) {
        root.selectedDistance = distance
    }

    function showMore() {
        if (root.metrics.ultraWide) {
            root.moreVisible = !root.moreVisible
            return
        }
        root.detailPage = "more"
    }

    function goBack() {
        if (root.detailPage !== "main") {
            root.detailPage = "main"
            return true
        }
        return false
    }

    function arrowGlyph(direction) {
        if (direction === "up") {
            return "▲"
        }
        if (direction === "down") {
            return "▼"
        }
        if (direction === "left") {
            return "◀"
        }
        return "▶"
    }

    component LockedTile: Rectangle {
        id: tileRoot
        property string title: ""
        property string hint: "locked"
        property bool selected: false

        color: selected ? "#1b2b2e" : "#101617"
        opacity: selected ? 1.0 : 0.9
        border.color: selected ? root.selectedAccent : "#48565a"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.2)

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(3, Math.round(root.metrics.fontSize * 0.2))
            color: "transparent"
            border.color: "#1f2a2c"
            border.width: 1
            radius: Math.round(parent.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                color: tileRoot.selected ? Theme.text : Theme.text
                text: tileRoot.title
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.bold: tileRoot.selected
                font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 1.02))
            }

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: tileRoot.hint
                visible: tileRoot.hint.length > 0
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.62))
            }
        }
    }

    component DirectionButton: Rectangle {
        id: directionRoot
        property string title: ""
        property string direction: "up"

        color: "#101819"
        border.color: "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.22)

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(3, Math.round(root.metrics.fontSize * 0.2))
            color: "transparent"
            border.color: "#1f2a2c"
            border.width: 1
            radius: Math.round(directionRoot.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                text: root.arrowGlyph(directionRoot.direction)
                color: "#d9e0e2"
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.35))
                horizontalAlignment: Text.AlignHCenter
            }

            Label {
                Layout.fillWidth: true
                text: directionRoot.title
                color: Theme.text
                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.78))
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                wrapMode: Text.NoWrap
            }
        }
    }

    component ActionIconButton: Rectangle {
        id: actionRoot
        property string title: ""
        property string hint: ""
        property string icon: ""
        property bool selected: false

        color: selected ? "#1b2b2e" : "#101819"
        border.color: selected ? root.selectedAccent : "#536165"
        border.width: 1
        radius: Math.round(Math.min(width, height) * 0.22)

        Rectangle {
            anchors.fill: parent
            anchors.margins: Math.max(3, Math.round(root.metrics.fontSize * 0.2))
            color: "transparent"
            border.color: "#1f2a2c"
            border.width: 1
            radius: Math.round(parent.radius * 0.72)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - root.metrics.gap
            spacing: 0

            Label {
                Layout.fillWidth: true
                text: actionRoot.icon
                color: Theme.text
                font.pixelSize: Math.max(22, Math.round(root.metrics.fontSize * 1.6))
                horizontalAlignment: Text.AlignHCenter
            }

            Label {
                Layout.fillWidth: true
                text: actionRoot.title
                color: Theme.text
                font.bold: true
                font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.6))
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            Label {
                Layout.fillWidth: true
                text: actionRoot.hint
                color: Theme.mutedText
                font.pixelSize: Math.max(8, Math.round(root.metrics.fontSize * 0.52))
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
        }
    }

    GridLayout {
        visible: root.detailPage === "main" || root.metrics.ultraWide
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        columns: root.metrics.ultraWide ? 3 : 1
        rows: root.metrics.ultraWide ? 1 : 3
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap

        Rectangle {
            id: controlGroupGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.ultraWide ? Math.round(root.width * 0.48) : -1
            color: Theme.buttonsBg
            border.color: "#465456"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.45)

            Item {
                id: motionPad
                anchors.fill: parent
                anchors.margins: root.metrics.gap

                Item {
                    id: xyMovePad
                    width: root.metrics.portrait ? parent.width : Math.round(parent.width * 0.42)
                    height: root.metrics.portrait ? Math.round(parent.height * 0.48) : parent.height
                    anchors.left: parent.left
                    anchors.top: parent.top
                    property int padSize: Math.max(58, Math.min(width, height))
                    property int arrowSize: Math.max(64, Math.round(padSize * 0.32))
                    property int homeSize: Math.max(76, Math.round(padSize * 0.29))

                    Repeater {
                        model: root.xyButtons

                        DirectionButton {
                            required property var modelData
                            width: xyMovePad.arrowSize
                            height: xyMovePad.arrowSize
                            title: modelData.label
                            direction: modelData.direction
                            anchors.horizontalCenter: modelData.direction === "up" || modelData.direction === "down" ? parent.horizontalCenter : undefined
                            anchors.verticalCenter: modelData.direction === "left" || modelData.direction === "right" ? parent.verticalCenter : undefined
                            anchors.top: modelData.direction === "up" ? parent.top : undefined
                            anchors.bottom: modelData.direction === "down" ? parent.bottom : undefined
                            anchors.left: modelData.direction === "left" ? parent.left : undefined
                            anchors.right: modelData.direction === "right" ? parent.right : undefined
                        }
                    }

                    LockedTile {
                        width: xyMovePad.homeSize
                        height: xyMovePad.homeSize
                        anchors.centerIn: parent
                        title: "Home"
                        hint: "locked"
                    }
                }

                Item {
                    id: zMovePad
                    width: root.metrics.portrait ? Math.round(parent.width * 0.48) : Math.round(parent.width * 0.22)
                    height: root.metrics.portrait ? Math.round(parent.height * 0.46) : parent.height
                    anchors.right: undefined
                    anchors.horizontalCenter: undefined
                    anchors.leftMargin: root.metrics.portrait ? 0 : root.metrics.gap
                    anchors.top: root.metrics.portrait ? xyMovePad.bottom : parent.top
                    anchors.topMargin: root.metrics.portrait ? root.metrics.gap : 0
                    anchors.left: root.metrics.portrait ? parent.left : xyMovePad.right
                    property int padSize: Math.max(58, Math.min(width, height))
                    property int arrowSize: Math.max(70, Math.round(padSize * 0.32))
                    property int homeSize: Math.max(88, Math.round(padSize * 0.31))

                    DirectionButton {
                        width: zMovePad.arrowSize
                        height: zMovePad.arrowSize
                        title: "Z+"
                        direction: "up"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                    }

                    LockedTile {
                        width: zMovePad.homeSize
                        height: zMovePad.homeSize
                        anchors.centerIn: parent
                        title: "Z Home"
                        hint: "locked"
                    }

                    DirectionButton {
                        width: zMovePad.arrowSize
                        height: zMovePad.arrowSize
                        title: "Z-"
                        direction: "down"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                    }
                }

                GridLayout {
                    id: motionActions
                    width: root.metrics.portrait ? Math.round(parent.width * 0.52) : Math.round(parent.width * 0.24)
                    height: root.metrics.portrait ? zMovePad.height : Math.round(parent.height * 0.72)
                    y: root.metrics.portrait ? zMovePad.y : Math.round((parent.height - height) / 2)
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    columns: root.metrics.portrait ? 2 : 1
                    rows: root.metrics.portrait ? 1 : 2
                    rowSpacing: root.metrics.gap
                    columnSpacing: root.metrics.gap

                    Repeater {
                        model: root.actionButtons

                        ActionIconButton {
                            required property var modelData

                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            title: modelData.label
                            hint: modelData.hint
                            icon: modelData.icon
                            selected: modelData.action === "more"
                                && (root.moreVisible || root.detailPage === "more")

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (modelData.action === "more") {
                                        root.showMore()
                                    } else {
                                        root.moveActionRequested(modelData.action)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            id: positionPanel
            Layout.fillWidth: true
            Layout.fillHeight: root.metrics.ultraWide
            Layout.preferredWidth: root.metrics.ultraWide ? Math.round(root.width * 0.27) : -1
            Layout.preferredHeight: root.metrics.ultraWide
                ? -1
                : root.moreVisible
                    ? Math.max(118, Math.round(root.metrics.fontSize * 7.2))
                    : Math.max(82, Math.round(root.metrics.fontSize * 5.1))
            color: "#0d1415"
            border.color: "#344044"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: Math.max(5, Math.round(root.metrics.gap * 0.55))

                RowLayout {
                    Layout.fillWidth: true
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Position"
                        font.bold: true
                        font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.02))
                    }

                    Label {
                        color: Theme.mutedText
                        text: "Controls locked"
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.76))
                    }
                }

                Rectangle {
                    id: moveMorePanel
                    Layout.fillWidth: true
                    Layout.preferredHeight: root.moreVisible
                        ? Math.max(46, Math.round(root.metrics.fontSize * 2.9))
                        : 0
                    visible: root.moreVisible && root.metrics.ultraWide
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.22)

                    GridLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(5, Math.round(root.metrics.gap * 0.5))
                        columns: root.metrics.ultraWide ? 1 : 5
                        columnSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                        rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))

                        Repeater {
                            model: ["Invert X", "Invert Y", "Invert Z", "XY Speed", "Z Speed"]

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "#0b1112"
                                border.color: "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.18)

                                Label {
                                    anchors.centerIn: parent
                                    width: parent.width - 4
                                    color: Theme.mutedText
                                    text: modelData
                                    horizontalAlignment: Text.AlignHCenter
                                    elide: Text.ElideRight
                                    font.pixelSize: Math.max(9, Math.round(root.metrics.fontSize * 0.62))
                                }
                            }
                        }
                    }
                }

                GridLayout {
                    id: positionGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: root.metrics.ultraWide
                    columns: root.metrics.ultraWide ? 1 : 4
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.fontSize * 0.35))

                    Repeater {
                        model: [
                            {"label": "X", "value": root.positionX.toFixed(2)},
                            {"label": "Y", "value": root.positionY.toFixed(2)},
                            {"label": "Z", "value": root.positionZ.toFixed(2)},
                            {"label": "E", "value": root.positionE.toFixed(2)}
                        ]

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: root.metrics.ultraWide
                            Layout.preferredHeight: Math.max(28, Math.round(root.metrics.fontSize * 1.85))
                            color: "#101617"
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.18)

                            Label {
                                anchors.centerIn: parent
                                color: Theme.text
                                text: modelData.label + " " + modelData.value
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                            }
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: root.homedAxes.length > 0 ? "Homed: " + root.homedAxes : "Homed: unknown"
                    elide: Text.ElideRight
                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                }
            }
        }

        Rectangle {
            id: distancePanel
            Layout.fillWidth: true
            Layout.fillHeight: root.metrics.ultraWide
            Layout.preferredWidth: root.metrics.ultraWide ? Math.round(root.width * 0.22) : -1
            Layout.preferredHeight: root.metrics.ultraWide ? -1 : Math.max(70, Math.round(root.metrics.fontSize * 4.2))
            color: "#0d1415"
            border.color: "#344044"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.36)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: Math.max(5, Math.round(root.metrics.gap * 0.55))

                Label {
                    Layout.fillWidth: true
                    color: Theme.text
                    text: "Distance"
                    font.bold: true
                    font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.02))
                }

                GridLayout {
                    id: distanceGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: root.metrics.ultraWide
                    Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 1.9))
                    columns: root.metrics.ultraWide ? 1 : 7
                    rowSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))
                    columnSpacing: Math.max(5, Math.round(root.metrics.gap * 0.5))

                    Repeater {
                        model: root.distances

                        LockedTile {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: Math.max(30, Math.round(root.metrics.fontSize * 1.9))
                            title: modelData
                            hint: "mm"
                            selected: root.selectedDistance === modelData

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.selectDistance(modelData)
                            }
                        }
                    }

                    Repeater {
                        model: root.metrics.portrait ? root.portraitPlaceholders : []

                        Rectangle {
                            required property var modelData
                            property bool placeholder: modelData.placeholder
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            visible: false
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: moveMorePage
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        visible: root.detailPage === "more" && !root.metrics.ultraWide
        color: "#0d1415"
        border.color: "#344044"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.36)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap

            Label {
                Layout.fillWidth: true
                color: Theme.text
                text: "Move Settings"
                font.bold: true
                font.pixelSize: Math.max(18, Math.round(root.metrics.fontSize * 1.18))
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 1 : 2
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap

                Repeater {
                    model: ["Invert X", "Invert Y", "Invert Z", "XY Speed", "Z Speed"]

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: Math.max(54, Math.round(root.metrics.fontSize * 3.2))
                        color: "#101617"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.28)

                        Label {
                            anchors.centerIn: parent
                            width: parent.width - root.metrics.gap
                            color: Theme.text
                            text: modelData
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize * 0.9))
                        }
                    }
                }
            }
        }
    }
}
