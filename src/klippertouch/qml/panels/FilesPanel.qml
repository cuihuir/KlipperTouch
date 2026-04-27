import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    required property var metrics
    property var fileModel: null
    property var activeFileModel: fileModel
    property string rootPath: "gcodes"
    property bool loading: false
    property bool compactFileRows: root.metrics.portrait || width < 920

    function currentPathLabel() {
        if (root.activeFileModel && root.activeFileModel.currentPath.length > 0) {
            return "/" + root.rootPath + "/" + root.activeFileModel.currentPath
        }
        return "/" + root.rootPath
    }

    function setSort(sortKey) {
        if (root.activeFileModel) {
            root.activeFileModel.setSortKey(sortKey)
        }
    }

    function isSortActive(sortKey) {
        return root.activeFileModel && root.activeFileModel.sortKey === sortKey
    }

    function isChipEnabled(sortKey) {
        return sortKey !== "up" || (root.activeFileModel && root.activeFileModel.canGoUp)
    }

    function chipText(label, sortKey) {
        if (sortKey === "up") {
            return label
        }
        return root.isSortActive(sortKey)
            ? label + (root.activeFileModel && root.activeFileModel.sortDescending ? "  v" : "  ^")
            : label
    }

    function goUp() {
        if (root.activeFileModel) {
            root.activeFileModel.goUp()
        }
    }

    function enterPath(path, isDirectory) {
        if (isDirectory && root.activeFileModel) {
            root.activeFileModel.setCurrentPath(path)
        } else if (root.activeFileModel) {
            root.activeFileModel.selectPath(path, isDirectory)
        }
    }

    function emptyTitle() {
        if (root.loading) {
            return "Loading files..."
        }
        if (root.activeFileModel && root.activeFileModel.currentPath.length > 0) {
            return "Current folder is empty"
        }
        return "No G-Code files found"
    }

    Rectangle {
        anchors.fill: parent
        anchors.margins: root.metrics.margin
        color: Theme.buttonsBg
        border.color: "#465456"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.45)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.metrics.gap
            spacing: root.metrics.gap

            RowLayout {
                id: compactControlRow
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(34, Math.round(root.metrics.fontSize * 2.45))
                spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                Repeater {
                    model: [
                        {"label": "Name", "sortKey": "name"},
                        {"label": "Date", "sortKey": "date"},
                        {"label": "Size", "sortKey": "size"},
                        {"label": "Up", "sortKey": "up"}
                    ]

                    Rectangle {
                        Layout.preferredWidth: chipText.implicitWidth + root.metrics.gap * 1.4
                        Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 2.2))
                        color: root.isSortActive(modelData.sortKey) ? "#1b2b2e" : "#101617"
                        opacity: root.isChipEnabled(modelData.sortKey) ? 1.0 : 0.45
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        Label {
                            id: chipText
                            anchors.centerIn: parent
                            color: Theme.mutedText
                            text: root.chipText(modelData.label, modelData.sortKey)
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                        }

                        MouseArea {
                            anchors.fill: parent
                            enabled: root.isChipEnabled(modelData.sortKey)
                            onClicked: modelData.sortKey === "up" ? root.goUp() : root.setSort(modelData.sortKey)
                        }
                    }
                }

                TextField {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(34, Math.round(root.metrics.fontSize * 2.45))
                    placeholderText: "Search files"
                    color: Theme.text
                    placeholderTextColor: Theme.mutedText
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                    background: Rectangle {
                        color: "#101617"
                        border.color: "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)
                    }
                    onTextChanged: if (root.activeFileModel) root.activeFileModel.setFilterText(text)
                }
            }

            RowLayout {
                id: compactMetaRow
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(24, Math.round(root.metrics.fontSize * 1.7))
                spacing: root.metrics.gap

                Label {
                    id: pathLabel
                    Layout.fillWidth: true
                    color: Theme.mutedText
                    text: root.currentPathLabel()
                    elide: Text.ElideMiddle
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }

                Label {
                    color: Theme.mutedText
                    text: root.loading ? "Loading files..." : fileList.count + " items"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                }

                Label {
                    color: Theme.mutedText
                    text: "readonly"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: root.metrics.portrait ? 1 : 2
                rows: root.metrics.portrait ? 2 : 1
                rowSpacing: root.metrics.gap
                columnSpacing: root.metrics.gap
                visible: fileList.count > 0

                ListView {
                    id: fileList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumWidth: 0
                    clip: true
                    spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))
                    model: root.activeFileModel
                    boundsBehavior: Flickable.StopAtBounds
                    flickDeceleration: 2600
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    delegate: Rectangle {
                        required property string path
                        required property string displayName
                        required property string sizeLabel
                        required property real modified
                        required property bool isDirectory
                        required property string modifiedLabel
                        required property string permissions
                        required property string thumbnailUrl

                        width: fileList.width
                        height: Math.max(46, Math.round(root.metrics.fontSize * (root.metrics.portrait ? 4.2 : 3.3)))
                        color: !isDirectory && root.activeFileModel && root.activeFileModel.selectedPath === path
                            ? "#17282b"
                            : "#101617"
                        border.color: !isDirectory && root.activeFileModel && root.activeFileModel.selectedPath === path
                            ? Theme.color4
                            : "#263233"
                        border.width: 1
                        radius: Math.round(root.metrics.fontSize * 0.32)

                        GridLayout {
                            anchors.fill: parent
                            anchors.leftMargin: root.metrics.gap
                            anchors.rightMargin: root.metrics.gap
                            columns: root.compactFileRows ? 2 : 5
                            rowSpacing: 0
                            columnSpacing: root.metrics.gap

                            Rectangle {
                                Layout.preferredWidth: Math.max(40, Math.round(root.metrics.fontSize * 2.8))
                                Layout.preferredHeight: Layout.preferredWidth
                                Layout.rowSpan: 2
                                color: "#0b1112"
                                border.color: "#263233"
                                border.width: 1
                                radius: Math.round(root.metrics.fontSize * 0.22)

                                Image {
                                    anchors.fill: parent
                                    anchors.margins: 2
                                    source: thumbnailUrl
                                    fillMode: Image.PreserveAspectFit
                                    visible: !isDirectory && thumbnailUrl.length > 0
                                }

                                Label {
                                    anchors.centerIn: parent
                                    color: Theme.mutedText
                                    text: isDirectory ? "DIR" : "G"
                                    visible: isDirectory || thumbnailUrl.length <= 0
                                    font.bold: true
                                    font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                }
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: isDirectory ? "Folder  " + displayName : displayName
                                elide: Text.ElideMiddle
                                font.pixelSize: Math.max(13, Math.round(root.metrics.fontSize))
                            }

                            Label {
                                Layout.preferredWidth: root.compactFileRows
                                    ? fileList.width - root.metrics.gap * 2
                                    : Math.max(72, Math.round(root.metrics.fontSize * 5.2))
                                color: Theme.mutedText
                                text: root.compactFileRows
                                    ? path + " | " + sizeLabel + " | " + modifiedLabel
                                    : sizeLabel
                                elide: Text.ElideMiddle
                                horizontalAlignment: root.compactFileRows ? Text.AlignLeft : Text.AlignRight
                                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                            }

                            Label {
                                Layout.preferredWidth: Math.max(112, Math.round(root.metrics.fontSize * 8.2))
                                visible: !root.compactFileRows
                                color: Theme.mutedText
                                text: modifiedLabel
                                horizontalAlignment: Text.AlignRight
                                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                            }

                            Label {
                                Layout.preferredWidth: Math.max(76, Math.round(root.metrics.fontSize * 5.4))
                                visible: !root.compactFileRows
                                color: Theme.mutedText
                                text: permissions
                                horizontalAlignment: Text.AlignRight
                                font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.enterPath(path, isDirectory)
                        }
                    }
                }

                Rectangle {
                    id: detailsPanel
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumWidth: 0
                    color: "#101617"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                        Label {
                            Layout.fillWidth: true
                            color: Theme.text
                            text: root.activeFileModel && root.activeFileModel.selectedDisplayName.length > 0
                                ? root.activeFileModel.selectedDisplayName
                                : "Read-only file details"
                            elide: Text.ElideMiddle
                            font.bold: true
                            font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.05))
                        }

                        Label {
                            Layout.fillWidth: true
                            color: Theme.mutedText
                            text: root.activeFileModel && root.activeFileModel.selectedPath.length > 0
                                ? root.activeFileModel.selectedPath
                                : "Select a G-Code file to inspect metadata."
                            wrapMode: Text.WordWrap
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.max(120, Math.round(root.metrics.fontSize * 8.5))
                            visible: root.activeFileModel
                                && root.activeFileModel.selectedPreviewThumbnailUrl.length > 0
                            color: "#0b1112"
                            border.color: "#263233"
                            border.width: 1
                            radius: Math.round(root.metrics.fontSize * 0.25)

                            Image {
                                anchors.fill: parent
                                anchors.margins: root.metrics.gap
                                source: root.activeFileModel
                                    ? root.activeFileModel.selectedPreviewThumbnailUrl
                                    : ""
                                fillMode: Image.PreserveAspectFit
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))
                            columnSpacing: root.metrics.gap

                            Repeater {
                                model: [
                                    {"label": "Size", "value": root.activeFileModel ? root.activeFileModel.selectedSizeLabel : "-"},
                                    {"label": "Modified", "value": root.activeFileModel ? root.activeFileModel.selectedModifiedLabel : "-"},
                                    {"label": "Permissions", "value": root.activeFileModel ? root.activeFileModel.selectedPermissions : "-"},
                                    {"label": "Mode", "value": "readonly"}
                                ]

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 3.0))
                                    color: "#0b1112"
                                    border.color: "#263233"
                                    border.width: 1
                                    radius: Math.round(root.metrics.fontSize * 0.25)

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: Math.max(5, Math.round(root.metrics.fontSize * 0.35))
                                        spacing: 0

                                        Label {
                                            Layout.fillWidth: true
                                            color: Theme.mutedText
                                            text: modelData.label
                                            font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                                        }

                                        Label {
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            text: modelData.value.length > 0 ? modelData.value : "-"
                                            elide: Text.ElideRight
                                            font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                                        }
                                    }
                                }
                            }
                        }

                        Item {
                            Layout.fillHeight: true
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: fileList.count === 0
                color: "#101617"
                border.color: "#263233"
                border.width: 1
                radius: Math.round(root.metrics.fontSize * 0.32)

                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - root.metrics.gap * 2
                    spacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: root.emptyTitle()
                        horizontalAlignment: Text.AlignHCenter
                        font.bold: true
                        font.pixelSize: Math.max(15, Math.round(root.metrics.fontSize * 1.05))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.mutedText
                        text: "Read-only file browser; print actions stay out of this page."
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }
                }
            }
        }
    }
}
