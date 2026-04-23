import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    id: root
    required property var metrics

    TemperatureSummary {
        id: temperatureSummary
        metrics: root.metrics
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: root.metrics.margin
        width: root.metrics.portrait ? parent.width - root.metrics.margin * 2 : Math.round(parent.width * 0.43)
        height: root.metrics.portrait ? Math.round(parent.height * 0.42) : parent.height - root.metrics.margin * 2
    }

    GridLayout {
        id: menuGrid
        columns: root.metrics.portrait ? 3 : 2
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap
        anchors.left: root.metrics.portrait ? parent.left : temperatureSummary.right
        anchors.right: parent.right
        anchors.top: root.metrics.portrait ? temperatureSummary.bottom : parent.top
        anchors.bottom: parent.bottom
        anchors.margins: root.metrics.margin

        Repeater {
            model: ListModel {
                ListElement { tileLabel: "Homing"; tileIcon: "⌂"; tileAccent: "#f26722" }
                ListElement { tileLabel: "Temperature"; tileIcon: "♨"; tileAccent: "#c8009f" }
                ListElement { tileLabel: "Actions"; tileIcon: "✥"; tileAccent: "#00a889" }
                ListElement { tileLabel: "Configuration"; tileIcon: "⚙"; tileAccent: "#6bdc19" }
                ListElement { tileLabel: "Print"; tileIcon: "▣"; tileAccent: "#f26722" }
            }

            MenuTile {
                required property int index
                required property string tileLabel
                required property string tileIcon
                required property color tileAccent

                label: tileLabel
                iconText: tileIcon
                accent: tileAccent
                fontSize: root.metrics.fontSize
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.columnSpan: !root.metrics.portrait && index === 4 ? 2 : 1
                Layout.minimumHeight: Math.max(72, Math.round(root.metrics.fontSize * 5.8))
            }
        }
    }
}
