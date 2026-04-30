import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Rectangle {
    id: root
    property string text: ""
    property string hint: ""
    property string iconName: ""
    property real fontSize: 16
    property bool placeholder: false
    property bool pressedFeedback: false
    readonly property bool feedbackActive: root.pressedFeedback || pressArea.pressed

    signal clicked()

    radius: Math.round(height * 0.18)
    color: root.feedbackActive ? "#182124" : root.placeholder ? "#141b1d" : "#1a2528"
    scale: root.feedbackActive ? 0.97 : 1.0
    border.color: root.feedbackActive ? Theme.text : root.placeholder ? "#3d474a" : "#667276"
    border.width: 1

    Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutQuad } }
    Behavior on color { ColorAnimation { duration: 80 } }
    Behavior on border.color { ColorAnimation { duration: 80 } }

    Rectangle {
        id: tileDepth
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: Math.max(3, Math.round(root.fontSize * 0.18))
        visible: !root.feedbackActive && !root.placeholder
        color: "#050808"
        opacity: 0.82
        radius: parent.radius
    }

    Column {
        anchors.centerIn: parent
        width: parent.width - Math.max(4, Math.round(root.fontSize * 0.7))
        spacing: 2

        Image {
            width: parent.width
            height: Math.max(18, Math.round(root.fontSize * 1.25))
            source: Theme.iconSource(root.iconName.length > 0 ? root.iconName : "placeholder")
            sourceSize.width: height
            sourceSize.height: height
            fillMode: Image.PreserveAspectFit
            opacity: root.placeholder ? 0.55 : 1.0
        }

        Label {
            width: parent.width
            text: root.text
            color: Theme.text
            font.pixelSize: Math.max(11, Math.round(root.fontSize * 0.76))
            font.bold: !root.placeholder
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }

        Label {
            width: parent.width
            text: root.hint
            color: "#9aa7ad"
            font.pixelSize: Math.max(9, Math.round(root.fontSize * 0.6))
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
    }

    MouseArea {
        id: pressArea
        anchors.fill: parent
        onClicked: root.clicked()
    }
}
