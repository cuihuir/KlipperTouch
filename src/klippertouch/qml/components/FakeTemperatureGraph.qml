import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../Theme.js" as Theme

Rectangle {
    id: root
    property real fontSize: 16
    property real maxTemperature: 300
    property var seriesModel: []
    property int visiblePointCount: Math.max(180, Math.round(plotArea.width))

    color: Theme.buttonsBg
    border.color: "#465456"
    border.width: 1
    radius: Math.round(root.fontSize * 0.45)

    function normalizeTemperature(value) {
        return Math.max(0.04, Math.min(0.96, 1 - value / root.maxTemperature))
    }

    function requestRedraw() {
        if (graphCanvas) {
            graphCanvas.requestPaint()
        }
    }

    function visibleSeries(series) {
        if (!series || series.length <= root.visiblePointCount) {
            return series || []
        }
        return series.slice(series.length - root.visiblePointCount)
    }

    function seriesPoints(series, plotWidth, plotHeight) {
        var points = []
        var currentSeries = root.visibleSeries(series)
        if (!currentSeries || currentSeries.length <= 0) {
            return points
        }
        for (var i = 0; i < currentSeries.length; i += 1) {
            if (currentSeries[i] === null || typeof currentSeries[i] === "undefined") {
                points.push(null)
                continue
            }
            var x = plotWidth * i / Math.max(1, currentSeries.length - 1)
            var y = plotHeight * root.normalizeTemperature(currentSeries[i])
            points.push({"x": x, "y": y})
        }
        return points
    }

    function drawSeries(ctx, item, plotWidth, plotHeight) {
        if (!item || !item.series) {
            return
        }
        var points = root.seriesPoints(item.series, plotWidth, plotHeight)
        if (points.length <= 0) {
            return
        }

        ctx.save()
        ctx.strokeStyle = item.color
        ctx.fillStyle = item.color
        ctx.globalAlpha = item.dashed ? 0.72 : 1.0
        ctx.lineWidth = Math.max(2, Math.round(root.fontSize * 0.14))
        ctx.lineCap = "round"
        ctx.lineJoin = "round"
        if (ctx.setLineDash) {
            var dashLength = Math.max(5, root.fontSize * 0.45)
            ctx.setLineDash(item.dashed ? [dashLength, dashLength] : [])
        }

        if (points.length === 1 && points[0] !== null) {
            ctx.beginPath()
            ctx.arc(
                points[0].x,
                points[0].y,
                Math.max(2, Math.round(root.fontSize * 0.18)),
                0,
                Math.PI * 2
            )
            ctx.fill()
            ctx.restore()
            return
        }

        ctx.beginPath()
        var hasActiveSegment = false
        for (var i = 0; i < points.length; i += 1) {
            if (points[i] === null) {
                hasActiveSegment = false
                continue
            }
            if (!hasActiveSegment) {
                ctx.moveTo(points[i].x, points[i].y)
                hasActiveSegment = true
            } else {
                ctx.lineTo(points[i].x, points[i].y)
            }
        }
        ctx.stroke()
        ctx.restore()
    }

    onSeriesModelChanged: requestRedraw()
    onMaxTemperatureChanged: requestRedraw()
    onVisiblePointCountChanged: requestRedraw()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(8, Math.round(root.fontSize * 0.55))
        spacing: Math.max(6, Math.round(root.fontSize * 0.4))

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Math.max(3, Math.round(root.fontSize * 0.18))

            Label {
                id: historyTitle
                Layout.fillWidth: true
                color: Theme.text
                text: "Temperature history"
                font.bold: true
                font.pixelSize: Math.max(14, Math.round(root.fontSize))
            }

            Item {
                id: legendViewport
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.preferredHeight: Math.max(root.fontSize, legendRow.implicitHeight)
                clip: true

                Row {
                    id: legendRow
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Math.max(8, Math.round(root.fontSize * 0.5))

                    Repeater {
                        model: root.seriesModel

                        Row {
                            visible: modelData.legendVisible === false ? false : true
                            spacing: Math.max(4, Math.round(root.fontSize * 0.25))

                            Rectangle {
                                width: Math.max(10, Math.round(root.fontSize * 0.7))
                                height: width
                                radius: width / 2
                                color: modelData.color
                            }

                            Label {
                                width: Math.min(
                                    implicitWidth,
                                    Math.max(root.fontSize * 3, legendViewport.width * 0.32)
                                )
                                color: Theme.mutedText
                                text: modelData.displayName
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(11, Math.round(root.fontSize * 0.8))
                            }
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

                Canvas {
                    id: graphCanvas
                    anchors.fill: parent
                    renderStrategy: Canvas.Threaded

                    onWidthChanged: requestPaint()
                    onHeightChanged: requestPaint()
                    onPaint: {
                        var ctx = getContext("2d")
                        ctx.clearRect(0, 0, width, height)
                        for (var i = 0; i < root.seriesModel.length; i += 1) {
                            var modelData = root.seriesModel[i]
                            root.drawSeries(ctx, modelData, width, height)
                        }
                    }
                }
            }
        }
    }
}
