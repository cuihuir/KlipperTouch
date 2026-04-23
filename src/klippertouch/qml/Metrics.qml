import QtQml

QtObject {
    id: root

    property int viewportWidth: 1024
    property int viewportHeight: 600
    property bool portrait: viewportHeight > viewportWidth
    property int shortSide: Math.min(viewportWidth, viewportHeight)
    property real fontSize: Math.min(
        viewportWidth / (portrait ? 28 : 40),
        viewportHeight / (portrait ? 42 : 27)
    )
    property int iconSize: Math.round(fontSize * 3)
    property int titlebarHeight: Math.max(28, Math.round(fontSize * 2))
    property int actionBarWidth: portrait ? viewportWidth : Math.max(48, Math.round(viewportWidth * 0.10))
    property int actionBarHeight: portrait ? Math.max(48, Math.round(viewportHeight * 0.10)) : viewportHeight
    property int contentWidth: portrait ? viewportWidth : viewportWidth - actionBarWidth
    property int contentHeight: viewportHeight - titlebarHeight - (portrait ? actionBarHeight : 0)
    property int gap: Math.max(5, Math.round(fontSize * 0.55))
    property int margin: Math.max(6, Math.round(fontSize * 0.75))
}
