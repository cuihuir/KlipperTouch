import QtQuick
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

    function normalizeTemperature(value) {
        return Math.max(0.04, Math.min(0.96, 1 - value / root.maxTemperature))
    }

    function drawSeries(ctx, series, color) {
        if (!series || series.length <= 0) {
            return
        }
        if (series.length === 1) {
            ctx.beginPath()
            ctx.arc(root.width * 0.5, root.height * root.normalizeTemperature(series[0]),
                    Math.max(3, Math.round(root.fontSize * 0.22)), 0, Math.PI * 2)
            ctx.fillStyle = color
            ctx.fill()
            return
        }
        ctx.beginPath()
        for (var i = 0; i < series.length; i += 1) {
            var x = root.width * i / Math.max(1, series.length - 1)
            var y = root.height * root.normalizeTemperature(series[i])
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

    Repeater {
        id: horizontalGrid
        model: [0.2, 0.4, 0.6, 0.8]

        Rectangle {
            x: 0
            y: Math.round(root.height * modelData)
            width: root.width
            height: 1
            color: "#263233"
        }
    }

    Repeater {
        id: verticalGrid
        model: [0.2, 0.4, 0.6, 0.8]

        Rectangle {
            x: Math.round(root.width * modelData)
            y: 0
            width: 1
            height: root.height
            color: "#202a2b"
        }
    }

    Repeater {
        id: targetSegments
        model: 12

        Rectangle {
            width: Math.max(5, Math.round(root.width / 28))
            height: Math.max(1, Math.round(root.fontSize * 0.08))
            x: Math.round(index * root.width / 12)
            y: Math.round(root.height * 0.30)
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

    onExtruderSeriesChanged: graphCanvas.requestPaint()
    onBedSeriesChanged: graphCanvas.requestPaint()
}
