import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    property bool vertical: true
    property int buttonExtent: Math.max(44, Math.round((vertical ? width : height) * 0.62))

    color: "#2b3138"

    Flow {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        flow: root.vertical ? Flow.TopToBottom : Flow.LeftToRight

        Repeater {
            model: ["Back", "Home", "Menu", "Stop"]

            Button {
                enabled: false
                text: modelData
                height: root.buttonExtent
                width: root.vertical ? parent.width : root.buttonExtent * 1.45
            }
        }
    }
}
