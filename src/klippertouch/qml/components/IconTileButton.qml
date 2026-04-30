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
    property real iconSize: Math.max(18, Math.round(root.fontSize * 1.25))
    property real textFontScale: 0.76
    property real hintFontScale: 0.6
    property int textMaximumLineCount: 1
    property bool placeholder: false
    property bool selected: false
    property bool pressedFeedback: false
    property color baseColor: "#1a2528"
    property color selectedColor: "#1b2b2e"
    property color pressedColor: "#182124"
    property color placeholderColor: "#141b1d"
    property color accentColor: "#667276"
    property color selectedAccentColor: "#7f9298"
    property color pressedAccentColor: Theme.text
    property color placeholderAccentColor: "#3d474a"
    property color hintColor: "#9aa7ad"
    property real disabledOpacity: 0.46
    readonly property bool feedbackActive: root.pressedFeedback || pressArea.pressed

    signal clicked()

    opacity: root.enabled ? 1.0 : root.disabledOpacity
    radius: Math.round(height * 0.18)
    color: root.feedbackActive
        ? root.pressedColor
        : root.placeholder
            ? root.placeholderColor
            : root.selected ? root.selectedColor : root.baseColor
    scale: root.feedbackActive ? 0.97 : 1.0
    border.color: root.feedbackActive
        ? root.pressedAccentColor
        : root.placeholder
            ? root.placeholderAccentColor
            : root.selected ? root.selectedAccentColor : root.accentColor
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
            height: root.iconSize
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
            font.pixelSize: Math.max(10, Math.round(root.fontSize * root.textFontScale))
            font.bold: !root.placeholder
            horizontalAlignment: Text.AlignHCenter
            wrapMode: root.textMaximumLineCount > 1 ? Text.WordWrap : Text.NoWrap
            maximumLineCount: root.textMaximumLineCount
            elide: Text.ElideRight
        }

        Label {
            width: parent.width
            text: root.hint
            visible: root.hint.length > 0
            color: root.hintColor
            font.pixelSize: Math.max(8, Math.round(root.fontSize * root.hintFontScale))
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
