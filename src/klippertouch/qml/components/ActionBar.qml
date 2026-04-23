import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    property bool vertical: true
    property var buttonLabels: ["Back", "Home", "Menu", "Stop"]
    property var buttonIcons: ["back", "main", "settings", "emergency"]
    property int spacingSize: Math.max(4, Math.round((vertical ? width : height) * 0.06))

    color: "#2b3138"

    function iconSource(iconName) {
        return "../assets/material-dark/images/" + iconName + ".svg"
    }

    Grid {
        id: buttonGrid
        anchors.fill: parent
        anchors.margins: root.spacingSize
        spacing: root.spacingSize
        rows: root.vertical ? root.buttonLabels.length : 1
        columns: root.vertical ? 1 : root.buttonLabels.length
        property real cellWidth: (width - spacing * Math.max(0, columns - 1)) / columns
        property real cellHeight: (height - spacing * Math.max(0, rows - 1)) / rows

        Repeater {
            model: root.buttonIcons

            Button {
                property int actionIconSize: Math.round(Math.min(width, height) * 0.58)

                enabled: false
                text: ""
                height: buttonGrid.cellHeight
                width: buttonGrid.cellWidth
                padding: Math.max(4, Math.round(Math.min(width, height) * 0.18))

                icon.source: root.iconSource(modelData)
                icon.width: actionIconSize
                icon.height: actionIconSize
                icon.color: "#e2e2e2"
            }
        }
    }
}
