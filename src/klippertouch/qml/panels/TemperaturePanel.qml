import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme
import "../components"
import "../models"

Item {
    id: root
    required property var metrics
    property var temperatureModel: null
    property int deviceColumns: root.metrics.portrait ? 1 : 2
    property bool hasExternalTemperatureModel: typeof temperatureModel !== "undefined"
        && temperatureModel !== null
    property var activeTemperatureModel: root.hasExternalTemperatureModel
        ? temperatureModel
        : fallbackTemperatureModel

    TemperatureDeviceModel {
        id: fallbackTemperatureModel
    }

    GridLayout {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        rowSpacing: root.metrics.gap
        columnSpacing: root.metrics.gap
        columns: root.metrics.portrait ? 1 : 2
        rows: root.metrics.portrait ? 2 : 1

        FakeTemperatureGraph {
            id: graph
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * 0.48
            Layout.preferredHeight: root.metrics.portrait ? parent.height * 0.42 : parent.height
            Layout.minimumWidth: 0
            Layout.minimumHeight: 0
            seriesModel: typeof root.activeTemperatureModel.graphSeriesModel === "undefined"
                ? []
                : root.activeTemperatureModel.graphSeriesModel
        }

        Connections {
            target: root.activeTemperatureModel
            ignoreUnknownSignals: true

            function onGraphSeriesChanged() {
                graph.requestRedraw()
            }

            function onHistoryChanged() {
                graph.requestRedraw()
            }

            function onModelReset() {
                graph.requestRedraw()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: root.metrics.portrait ? parent.width : parent.width * 0.52
            Layout.preferredHeight: root.metrics.portrait ? parent.height * 0.58 : parent.height
            Layout.minimumWidth: 0
            Layout.minimumHeight: 0
            color: Theme.buttonsBg
            border.color: "#465456"
            border.width: 1
            radius: Math.round(root.metrics.fontSize * 0.45)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: root.metrics.gap
                spacing: root.metrics.gap

                RowLayout {
                    Layout.fillWidth: true
                    Layout.columnSpan: root.metrics.portrait ? 1 : 2
                    spacing: root.metrics.gap

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: "Temperature status"
                        font.bold: true
                        font.pixelSize: Math.max(14, Math.round(root.metrics.fontSize))
                    }

                    Label {
                        color: Theme.mutedText
                        text: "readonly"
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                    }
                }

                TemperatureDevicePager {
                    id: devicePager
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    temperatureModel: root.activeTemperatureModel
                    deviceColumns: root.deviceColumns
                    compact: false
                    showTargets: true
                    fontSize: root.metrics.fontSize
                }
            }
        }
    }
}
