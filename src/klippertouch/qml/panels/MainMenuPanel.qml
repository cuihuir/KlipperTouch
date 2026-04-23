import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    id: root
    required property var metrics
    property int virtualRows: 5
    property int temperatureRows: 3
    property int menuRows: 2
    property int landscapeMenuRows: 3
    property real landscapeTemperatureFraction: 0.5
    property int temperaturePanelHeight: Math.round(height * temperatureRows / virtualRows)
    property int menuPanelHeight: height - temperaturePanelHeight

    function shouldExpandLastTile(index) {
        return index === menuModel.count - 1 && menuModel.count % 2 === 1
    }

    ListModel {
        id: menuModel
        ListElement { tileLabel: "Move"; tileIcon: "move"; tileAccent: "#d46900" }
        ListElement { tileLabel: "Temperature"; tileIcon: "heat-up"; tileAccent: "#ed3c63" }
        ListElement { tileLabel: "Extrude"; tileIcon: "extrude"; tileAccent: "#849900" }
        ListElement { tileLabel: "More"; tileIcon: "settings"; tileAccent: "#007db4" }
        ListElement { tileLabel: "Print"; tileIcon: "printer"; tileAccent: "#d46900" }
    }

    TemperatureSummary {
        id: temperatureSummary
        metrics: root.metrics
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: root.metrics.margin
        width: root.metrics.portrait
            ? parent.width - root.metrics.margin * 2
            : Math.round((parent.width - root.metrics.margin * 2) * root.landscapeTemperatureFraction)
        height: root.metrics.portrait ? root.temperaturePanelHeight - root.metrics.margin * 2 : parent.height - root.metrics.margin * 2
    }

    GridLayout {
        id: menuGrid
        columns: root.metrics.portrait ? 3 : 2
        rows: root.metrics.portrait ? root.menuRows : root.landscapeMenuRows
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap
        anchors.left: root.metrics.portrait ? parent.left : temperatureSummary.right
        anchors.right: parent.right
        anchors.top: root.metrics.portrait ? temperatureSummary.bottom : parent.top
        anchors.bottom: parent.bottom
        anchors.margins: root.metrics.margin
        height: root.metrics.portrait ? root.menuPanelHeight - root.metrics.margin * 2 : parent.height - root.metrics.margin * 2

        Repeater {
            model: menuModel

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
                Layout.columnSpan: root.shouldExpandLastTile(index) ? 2 : 1
                Layout.minimumHeight: Math.max(72, Math.round(root.metrics.fontSize * 5.8))
            }
        }
    }
}
