import QtQuick
import QtQuick.Layouts
import "../components"
import "../models"

Item {
    id: root
    required property var metrics
    signal panelRequested(string panelName)

    MoreMenuModel {
        id: moreMenuModel
    }

    GridLayout {
        columns: root.metrics.portrait ? 2 : 3
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap
        anchors.fill: parent
        anchors.margins: root.metrics.margin

        Repeater {
            model: moreMenuModel

            MenuTile {
                required property string tileLabel
                required property string tileIcon
                required property color tileAccent
                required property string panelName

                label: tileLabel
                iconText: tileIcon
                accent: tileAccent
                fontSize: root.metrics.fontSize
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: Math.max(96, Math.round(root.metrics.fontSize * 6.6))
                onActivated: root.panelRequested(panelName)
            }
        }
    }
}
