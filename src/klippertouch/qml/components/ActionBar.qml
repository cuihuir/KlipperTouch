import QtQuick
import "../Theme.js" as Theme

Rectangle {
    id: root
    property bool vertical: true
    property var buttonLabels: ["Back", "Home", "Menu", "Stop"]
    property var buttonIcons: ["back", "main", "settings", "emergency"]
    property int spacingSize: Math.max(4, Math.round((vertical ? width : height) * 0.06))

    color: Theme.actionBarBg

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

            Rectangle {
                id: iconButton
                property int actionIconSize: Math.round(Math.min(width, height) * 0.58)

                height: buttonGrid.cellHeight
                width: buttonGrid.cellWidth
                color: Theme.buttonsBg
                radius: Math.round(Math.min(width, height) * 0.18)
                border.color: Theme.actionBarBg
                border.width: Math.max(1, Math.round(Math.min(width, height) * 0.035))

                Image {
                    anchors.centerIn: parent
                    source: Theme.iconSource(modelData)
                    width: iconButton.actionIconSize
                    height: iconButton.actionIconSize
                    fillMode: Image.PreserveAspectFit
                    sourceSize.width: width
                    sourceSize.height: height
                }

            }
        }
    }
}
