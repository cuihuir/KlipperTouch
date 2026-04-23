import QtQuick

Rectangle {
    id: root
    property real fontSize: 16

    color: "#101819"
    border.color: "#465456"
    border.width: 1

    Repeater {
        model: [0.2, 0.4, 0.6, 0.8]

        Rectangle {
            x: 0
            y: Math.round(root.height * modelData)
            width: root.width
            height: 1
            color: "#263233"
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        y: Math.round(parent.height * 0.34)
        height: Math.max(2, Math.round(root.fontSize * 0.12))
        color: "#ff00a8"
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        y: Math.round(parent.height * 0.47)
        height: Math.max(2, Math.round(root.fontSize * 0.12))
        color: "#f26722"
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        y: Math.round(parent.height * 0.51)
        height: Math.max(2, Math.round(root.fontSize * 0.12))
        color: "#00a889"
    }
}
