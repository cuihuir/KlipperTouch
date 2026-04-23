import QtQuick
import QtQuick.Controls
import "components"
import "panels"

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
    title: "KlipperTouch"

    property var bridgeModel: typeof statusModel === "undefined" ? null : statusModel
    property var temperatureBridgeModel: typeof temperatureDeviceModel === "undefined" ? null : temperatureDeviceModel
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property int objectCount: bridgeModel ? bridgeModel.objectCount : 0

    Metrics {
        id: metrics
        viewportWidth: window.width
        viewportHeight: window.height
    }

    BaseShell {
        anchors.fill: parent
        metrics: metrics
        hostname: window.hostname
        state: window.klippyState
        objectCount: window.objectCount
        temperatureModel: window.temperatureBridgeModel

        MainMenuPanel {
            anchors.fill: parent
            metrics: metrics
            temperatureModel: window.temperatureBridgeModel
        }
    }
}
