import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Button {
    id: control
    property real fontSize: 16
    property color baseColor: "#121b1d"
    property color pressedColor: "#172528"
    property color disabledColor: "#151a1b"
    property color accentColor: "#465456"
    property color disabledAccentColor: "#263233"
    property color depthColor: "#050808"
    property color textColor: Theme.text
    property color disabledTextColor: Theme.mutedText
    property string iconName: ""
    property real iconSize: Math.max(18, Math.round(control.fontSize * 1.25))
    property real depthSize: Math.max(3, Math.round(control.fontSize * 0.20))
    property bool showLeadingAccent: false
    property real leadingAccentWidth: Math.max(2, Math.round(control.fontSize * 0.18))
    property real disabledOpacity: 0.55

    opacity: control.enabled ? 1.0 : control.disabledOpacity
    scale: control.down && control.enabled ? 0.97 : 1.0
    transformOrigin: Item.Center
    Behavior on scale {
        NumberAnimation { duration: 70; easing.type: Easing.OutQuad }
    }

    contentItem: RowLayout {
        y: control.down && control.enabled ? Math.max(1, Math.round(control.fontSize * 0.08)) : 0
        spacing: control.iconName.length > 0 ? Math.max(4, Math.round(control.fontSize * 0.28)) : 0

        Item {
            Layout.fillWidth: true
            Layout.preferredWidth: 1
        }

        Image {
            visible: control.iconName.length > 0
            Layout.preferredWidth: control.iconSize
            Layout.preferredHeight: control.iconSize
            source: control.iconName.length > 0 ? Theme.iconSource(control.iconName) : ""
            sourceSize.width: control.iconSize
            sourceSize.height: control.iconSize
            fillMode: Image.PreserveAspectFit
            opacity: control.enabled ? 1.0 : 0.55
        }

        Label {
            Layout.maximumWidth: control.iconName.length > 0
                ? Math.max(24, control.width - control.iconSize - control.leftPadding - control.rightPadding - control.fontSize * 1.2)
                : Math.max(24, control.width - control.leftPadding - control.rightPadding)
            color: control.enabled ? control.textColor : control.disabledTextColor
            text: control.text
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            font.pixelSize: control.font.pixelSize > 0 ? control.font.pixelSize : Math.max(12, Math.round(control.fontSize * 0.82))
            font.bold: control.font.bold
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredWidth: 1
        }
    }

    background: Item {
        Rectangle {
            id: tactileDepth
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: control.depthSize
            visible: !control.down && control.enabled
            color: control.depthColor
            radius: tactileSurface.radius
        }

        Rectangle {
            id: tactileSurface
            anchors.fill: parent
            anchors.topMargin: control.down && control.enabled ? control.depthSize : 0
            anchors.bottomMargin: control.down ? 0 : control.depthSize
            color: control.enabled
                ? control.down ? control.pressedColor : control.baseColor
                : control.disabledColor
            border.color: control.enabled ? control.accentColor : control.disabledAccentColor
            border.width: control.enabled ? 1 : 1
            radius: Math.round(control.fontSize * 0.32)

            Rectangle {
                visible: control.showLeadingAccent
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: control.leadingAccentWidth
                color: control.enabled ? control.accentColor : control.disabledAccentColor
                opacity: control.enabled ? 0.85 : 0.25
                radius: parent.radius
            }
        }
    }
}
