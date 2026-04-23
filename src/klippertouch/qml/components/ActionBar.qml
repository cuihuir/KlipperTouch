import QtQuick
import "../Theme.js" as Theme

Rectangle {
    id: root
    property bool vertical: true
    property var buttonLabels: ["Back", "Home", "Menu", "Stop"]
    property var buttonIcons: ["back", "main", "settings", "emergency"]
    property var buttonActions: ["back", "home", "menu", "stop"]
    property int buttonCount: 4
    property int spacingSize: Math.max(4, Math.round((vertical ? width : height) * 0.06))
    signal actionRequested(string actionName)

    color: Theme.actionBarBg

    Item {
        id: buttonGrid
        anchors.fill: parent
        anchors.margins: root.spacingSize
        property real spacing: root.spacingSize
        property real cellWidth: root.vertical
            ? width
            : (width - spacing * Math.max(0, root.buttonCount - 1)) / root.buttonCount
        property real cellHeight: root.vertical
            ? (height - spacing * Math.max(0, root.buttonCount - 1)) / root.buttonCount
            : height

        Repeater {
            model: root.buttonIcons

            Rectangle {
                id: iconButton
                property int actionIconSize: Math.round(Math.min(width, height) * 0.58)

                x: root.vertical ? 0 : index * (buttonGrid.cellWidth + buttonGrid.spacing)
                y: root.vertical ? index * (buttonGrid.cellHeight + buttonGrid.spacing) : 0
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

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.actionRequested(root.buttonActions[index])
                }
            }
        }
    }
}
