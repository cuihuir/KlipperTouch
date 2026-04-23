import QtQuick
import "../Theme.js" as Theme

Item {
    id: root
    property string iconName: "heat-up"
    property real iconSize: 24
    property bool compact: false

    width: root.iconSize
    height: root.iconSize

    function accentColor() {
        if (root.iconName === "extruder") {
            return Theme.color2
        }
        if (root.iconName === "bed") {
            return Theme.color1
        }
        return Theme.color4
    }

    Rectangle {
        anchors.fill: parent
        radius: Math.round(width * 0.28)
        color: root.accentColor()
        opacity: root.compact ? 0.28 : 0.2
        border.color: root.accentColor()
        border.width: root.compact ? 0 : 1
    }

    Image {
        anchors.centerIn: parent
        source: Theme.iconSource(root.iconName)
        width: Math.round(root.iconSize * (root.compact ? 0.82 : 0.7))
        height: width
        fillMode: Image.PreserveAspectFit
        sourceSize.width: width
        sourceSize.height: height
    }
}
