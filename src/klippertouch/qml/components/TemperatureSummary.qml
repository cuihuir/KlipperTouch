import QtQuick
import QtQuick.Controls
import "../Theme.js" as Theme
import "../models"

Item {
    id: root
    required property var metrics
    property var temperatureModel: null
    property bool hasExternalTemperatureModel: typeof temperatureModel !== "undefined"
        && temperatureModel !== null
    property var activeTemperatureModel: root.hasExternalTemperatureModel
        ? temperatureModel
        : fallbackTemperatureModel

    TemperatureDeviceModel {
        id: fallbackTemperatureModel
    }

    Column {
        id: devices
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Math.round(parent.height * (root.metrics.portrait ? 0.55 : 0.52))
        spacing: root.metrics.gap
        clip: true

        Row {
            width: parent.width
            height: Math.max(18, Math.round(root.metrics.fontSize * 1.45))

            Label {
                color: Theme.mutedText
                text: ""
                width: parent.width * 0.46
            }

            Label {
                color: Theme.mutedText
                text: "Temp (°C)"
                width: parent.width * 0.27
                horizontalAlignment: Text.AlignRight
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.85))
            }

            Label {
                color: Theme.mutedText
                text: "Target (°C)"
                width: parent.width * 0.27
                horizontalAlignment: Text.AlignRight
                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.85))
            }
        }

        TemperatureDevicePager {
            width: parent.width
            height: parent.height - y
            temperatureModel: root.activeTemperatureModel
            deviceColumns: 1
            compact: true
            showTargets: true
            fontSize: root.metrics.fontSize
        }
    }

    FakeTemperatureGraph {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: devices.bottom
        anchors.bottom: parent.bottom
        anchors.topMargin: root.metrics.gap
        fontSize: root.metrics.fontSize
        seriesModel: typeof root.activeTemperatureModel.graphSeriesModel === "undefined"
            ? []
            : root.activeTemperatureModel.graphSeriesModel
    }
}
