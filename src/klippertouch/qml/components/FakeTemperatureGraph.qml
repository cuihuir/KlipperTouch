import QtQuick
import "../Theme.js" as Theme

Rectangle {
    id: root
    property real fontSize: 16
    property var extruderSeries: [0.72, 0.58, 0.46, 0.39, 0.34, 0.32, 0.33, 0.31]
    property var bedSeries: [0.78, 0.70, 0.62, 0.55, 0.50, 0.48, 0.47, 0.46]

    color: Theme.buttonsBg
    border.color: "#465456"
    border.width: 1

    function drawSeries(ctx, series, color) {
        ctx.beginPath()
        for (var i = 0; i < series.length; i += 1) {
            var x = root.width * i / Math.max(1, series.length - 1)
            var y = root.height * series[i]
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
}
