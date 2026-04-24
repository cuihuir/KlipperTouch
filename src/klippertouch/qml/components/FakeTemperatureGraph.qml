import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../Theme.js" as Theme

Rectangle {
    id: root
    property real fontSize: 16
    property real maxTemperature: 300
    property var extruderSeries: []
    property var bedSeries: []

    color: Theme.buttonsBg
    border.color: "#465456"
    border.width: 1
    radius: Math.round(root.fontSize * 0.45)

    function normalizeTemperature(value) {
        return Math.max(0.04, Math.min(0.96, 1 - value / root.maxTemperature))
    }

    function drawSeries(ctx, series, color) {
        if (!series || series.length <= 0) {
            return
        }
        if (series.length === 1) {
            ctx.beginPath()
            ctx.arc(
                plotArea.x + plotArea.width * 0.5,
                plotArea.y + plotArea.height * root.normalizeTemperature(series[0]),
                Math.max(3, Math.round(root.fontSize * 0.22)),
                0,
                Math.PI * 2
            )
            ctx.fillStyle = color
            ctx.fill()
            return
        }
        ctx.beginPath()
        for (var i = 0; i < series.length; i += 1) {
            var x = plotArea.x + plotArea.width * i / Math.max(1, series.length - 1)
            var y = plotArea.y + plotArea.height * root.normalizeTemperature(series[i])
            if (i === 0) {
                ctx.moveTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        }
        ctx.lineWidth = Math.max(2, Math.round(root.fontSize * 0.14))
        ctx.strokeStyle = color
        ctx.stroke()
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

            RowLayout {
                spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                Rectangle {
                    width: Math.max(10, Math.round(root.fontSize * 0.7))
                    height: width
                    radius: width / 2
                    color: Theme.color2
                }

                Label {
                    color: Theme.mutedText
                    text: "Extruder"
                    font.pixelSize: Math.max(11, Math.round(root.fontSize * 0.8))
                }

                Rectangle {
                    width: Math.max(10, Math.round(root.fontSize * 0.7))
                    height: width
                    radius: width / 2
                    color: Theme.color1
                }

                Label {
                    color: Theme.mutedText
                    text: "Bed"
                    font.pixelSize: Math.max(11, Math.round(root.fontSize * 0.8))
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Math.max(8, Math.round(root.fontSize * 0.5))

            ColumnLayout {
                Layout.preferredWidth: Math.max(34, Math.round(root.fontSize * 2.4))
                Layout.fillHeight: true
                spacing: 0

                Label {
                    id: maxTemperatureLabel
                    Layout.fillWidth: true
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
                    Layout.fillWidth: true
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
                    Layout.fillWidth: true
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

                Repeater {
                    id: targetSegments
                    model: 12

                    Rectangle {
                        width: Math.max(5, Math.round(plotArea.width / 28))
                        height: Math.max(1, Math.round(root.fontSize * 0.08))
                        x: Math.round(index * plotArea.width / 12)
                        y: Math.round(plotArea.height * 0.30)
                        color: Theme.color2
                        opacity: 0.75
                    }
                }

                Canvas {
                    id: graphCanvas
                    anchors.fill: parent

                    onPaint: {
                        var ctx = getContext("2d")
                        ctx.clearRect(0, 0, width, height)
                        drawSeries(ctx, extruderSeries, Theme.color2)
                        drawSeries(ctx, bedSeries, Theme.color1)
                    }

                    onWidthChanged: requestPaint()
                    onHeightChanged: requestPaint()
                }
            }
        }
    }

    onExtruderSeriesChanged: graphCanvas.requestPaint()
    onBedSeriesChanged: graphCanvas.requestPaint()
}
