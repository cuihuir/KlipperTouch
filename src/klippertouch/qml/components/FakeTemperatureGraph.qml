import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../Theme.js" as Theme

Rectangle {
    id: root
    property real fontSize: 16
    property real maxTemperature: 300
    property var seriesModel: []

    color: Theme.buttonsBg
    border.color: "#465456"
    border.width: 1
    radius: Math.round(root.fontSize * 0.45)

    function normalizeTemperature(value) {
        return Math.max(0.04, Math.min(0.96, 1 - value / root.maxTemperature))
    }

    function requestRedraw() {
        graphContent.visible = false
        graphContent.visible = true
    }

    function seriesPoints(series, plotWidth, plotHeight) {
        var points = []
        if (!series || series.length <= 0) {
            return points
        }
        for (var i = 0; i < series.length; i += 1) {
            var x = plotWidth * i / Math.max(1, series.length - 1)
            var y = plotHeight * root.normalizeTemperature(series[i])
            points.push({"x": x, "y": y})
        }
        return points
    }

    function segmentModel(series, color, plotWidth, plotHeight) {
        var model = []
        var points = root.seriesPoints(series, plotWidth, plotHeight)
        if (points.length === 1) {
            model.push({
                "x": points[0].x - Math.max(2, Math.round(root.fontSize * 0.18)),
                "y": points[0].y - Math.max(2, Math.round(root.fontSize * 0.18)),
                "width": Math.max(4, Math.round(root.fontSize * 0.36)),
                "rotation": 0,
                "color": color,
                "round": true
            })
            return model
        }
        for (var i = 1; i < points.length; i += 1) {
            var start = points[i - 1]
            var end = points[i]
            var dx = end.x - start.x
            var dy = end.y - start.y
            model.push({
                "x": start.x,
                "y": start.y,
                "width": Math.max(1, Math.sqrt(dx * dx + dy * dy)),
                "rotation": Math.atan2(dy, dx) * 180 / Math.PI,
                "color": color,
                "round": false
            })
        }
        return model
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(8, Math.round(root.fontSize * 0.55))
        spacing: Math.max(6, Math.round(root.fontSize * 0.4))

        RowLayout {
            Layout.fillWidth: true
            spacing: Math.max(10, Math.round(root.fontSize * 0.7))

            Label {
                color: Theme.text
                text: "Temperature history"
                font.bold: true
                font.pixelSize: Math.max(14, Math.round(root.fontSize))
            }

            Item {
                Layout.fillWidth: true
            }

            Row {
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                Repeater {
                    model: root.seriesModel

                    Row {
                        spacing: Math.max(4, Math.round(root.fontSize * 0.25))

                        Rectangle {
                            width: Math.max(10, Math.round(root.fontSize * 0.7))
                            height: width
                            radius: width / 2
                            color: modelData.color
                        }

                        Label {
                            color: Theme.mutedText
                            text: modelData.displayName
                            font.pixelSize: Math.max(11, Math.round(root.fontSize * 0.8))
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Math.max(8, Math.round(root.fontSize * 0.5))

            ColumnLayout {
                Layout.preferredWidth: Math.max(34, Math.round(root.fontSize * 2.4))
                Layout.minimumWidth: Layout.preferredWidth
                Layout.maximumWidth: Layout.preferredWidth
                Layout.fillWidth: false
                Layout.fillHeight: true
                spacing: 0

                Label {
                    id: maxTemperatureLabel
                    Layout.preferredWidth: parent.Layout.preferredWidth
                    Layout.alignment: Qt.AlignTop
                    color: Theme.mutedText
                    text: Math.round(root.maxTemperature) + "°"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
                }

                Item {
                    Layout.fillHeight: true
                }

                Label {
                    id: midTemperatureLabel
                    Layout.preferredWidth: parent.Layout.preferredWidth
                    color: Theme.mutedText
                    text: Math.round(root.maxTemperature / 2) + "°"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
                }

                Item {
                    Layout.fillHeight: true
                }

                Label {
                    id: baseTemperatureLabel
                    Layout.preferredWidth: parent.Layout.preferredWidth
                    Layout.alignment: Qt.AlignBottom
                    color: Theme.mutedText
                    text: "0°"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(10, Math.round(root.fontSize * 0.72))
                }
            }

            Item {
                id: plotArea
                Layout.fillWidth: true
                Layout.fillHeight: true

                Repeater {
                    id: horizontalGrid
                    model: [0.2, 0.4, 0.6, 0.8]

                    Rectangle {
                        x: 0
                        y: Math.round(plotArea.height * modelData)
                        width: plotArea.width
                        height: 1
                        color: "#263233"
                    }
                }

                Repeater {
                    id: verticalGrid
                    model: [0.2, 0.4, 0.6, 0.8]

                    Rectangle {
                        x: Math.round(plotArea.width * modelData)
                        y: 0
                        width: 1
                        height: plotArea.height
                        color: "#202a2b"
                    }
                }

                Item {
                    id: graphContent
                    anchors.fill: parent

                    Repeater {
                        model: root.seriesModel

                        Item {
                            anchors.fill: parent

                            Repeater {
                                model: root.segmentModel(
                                    modelData.series,
                                    modelData.color,
                                    plotArea.width,
                                    plotArea.height
                                )

                                Rectangle {
                                    x: modelData.x
                                    y: modelData.y
                                    width: modelData.width
                                    height: Math.max(2, Math.round(root.fontSize * 0.14))
                                    radius: modelData.round ? width / 2 : height / 2
                                    color: modelData.color
                                    rotation: modelData.rotation
                                    transformOrigin: Item.Left
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
