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

                GridView {
                    id: deviceGrid
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    cellWidth: Math.floor(deviceGrid.width / root.deviceColumns)
                    cellHeight: Math.max(112, Math.round(root.metrics.fontSize * 7.9))
                    model: root.activeTemperatureModel

                    delegate: Item {
                        property string deviceKey: typeof name === "undefined" || name === null
                            ? resolvedName
                            : name
                        property bool deviceGraphVisible: typeof graphVisible === "undefined" || graphVisible === null
                            ? false
                            : graphVisible
                        property string resolvedIcon: typeof icon === "undefined" || icon === null
                            ? "heat-up"
                            : icon
                        property string resolvedName: typeof displayName === "undefined" || displayName === null
                            ? "Temperature"
                            : displayName

                        width: Math.max(0, deviceGrid.cellWidth)
                        height: deviceGrid.cellHeight

                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: Math.max(3, Math.round(root.metrics.gap * 0.35))
                            color: "#101617"
                            border.color: deviceGraphVisible ? Theme.color4 : "#263233"
                            border.width: deviceGraphVisible ? 2 : 1
                            radius: Math.round(root.metrics.fontSize * 0.32)

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (typeof root.activeTemperatureModel.toggleGraphDevice === "function") {
                                        root.activeTemperatureModel.toggleGraphDevice(deviceKey)
                                    }
                                }
                            }

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: root.metrics.gap
                                spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.4))

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: root.metrics.gap

                                    TemperatureIcon {
                                        iconName: resolvedIcon
                                        iconSize: Math.max(28, Math.round(root.metrics.fontSize * 1.9))
                                        Layout.preferredWidth: iconSize
                                        Layout.preferredHeight: iconSize
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        color: Theme.text
                                        text: resolvedName
                                        elide: Text.ElideRight
                                        wrapMode: Text.WordWrap
                                        maximumLineCount: 2
                                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                                        font.bold: true
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 1
                                    color: "#263233"
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: "Actual"
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.text
                                    text: typeof temperature === "undefined" || temperature === null
                                        ? "--"
                                        : Math.round(temperature) + "°"
                                    font.pixelSize: Math.max(20, Math.round(root.metrics.fontSize * 1.42))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: "Target"
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }

                                Label {
                                    Layout.fillWidth: true
                                    color: Theme.mutedText
                                    text: typeof target === "undefined" || target === null
                                        ? "--"
                                        : Math.round(target) + "°"
                                    font.pixelSize: Math.max(16, Math.round(root.metrics.fontSize * 1.08))
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
