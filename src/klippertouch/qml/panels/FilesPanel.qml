import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../Theme.js" as Theme

Item {
    id: root
    objectName: "filesPanel"
    required property var metrics
    property var fileModel: null
    property var activeFileModel: fileModel
    property string rootPath: "gcodes"
    property bool loading: false
    property string loadError: ""
    property bool readOnlyMode: true
    property bool compactFileRows: root.metrics.portrait || width < 920
    property bool detailPage: false
    property string pendingFileAction: ""
    property string controlStatus: ""
    property string controlError: ""
    signal fileActionRequested(string action, string path)
    signal refreshRequested()

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
            root.detailPage = false
            root.pendingFileAction = ""
        } else if (root.activeFileModel) {
            root.activeFileModel.selectPath(path, isDirectory)
            root.activeFileModel.requestMetadata(path)
            root.detailPage = true
            root.pendingFileAction = ""
        }
    }

    function goBack() {
        if (root.pendingFileAction.length > 0) {
            root.pendingFileAction = ""
            return true
        }
        if (root.detailPage) {
            root.detailPage = false
            root.restoreFileListScroll()
            return true
        }
        return false
    }

    function restoreFileListScroll() {
        if (fileList) {
            fileList.restoreScrollPosition()
        }
    }

    function requestFileAction(action) {
        if (root.activeFileModel && root.activeFileModel.selectedPath.length > 0) {
            root.pendingFileAction = action
        }
    }

    function clearFileAction() {
        root.pendingFileAction = ""
    }

    function controlFeedbackText() {
        return root.controlError.length > 0 ? root.controlError : root.controlStatus
    }

    function handleFileDeleted(path) {
        if (root.activeFileModel && root.activeFileModel.selectedPath === path) {
            root.pendingFileAction = ""
            root.detailPage = false
            root.activeFileModel.clearSelection()
        }
    }

    function handleFilePrintStarted(path) {
        if (root.activeFileModel && root.activeFileModel.selectedPath === path) {
            root.pendingFileAction = ""
        }
    }

    function emptyTitle() {
        if (root.loadError.length > 0) {
            return "Unable to load files"
        }
        if (root.loading) {
            return "Loading files..."
        }
        if (root.activeFileModel && root.activeFileModel.currentPath.length > 0) {
            return "Current folder is empty"
        }
        return "No G-Code files found"
    }

    function selectedMetadataModel() {
        if (!root.activeFileModel || root.activeFileModel.selectedPath.length <= 0) {
            return []
        }
        root.activeFileModel.metadataRevision
        return [
            {"label": "Size", "value": root.activeFileModel.selectedSizeLabel},
            {"label": "Modified", "value": root.activeFileModel.selectedModifiedLabel},
            {
                "label": "Estimated time",
                "value": root.activeFileModel.fileEstimatedTimeLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Layer height",
                "value": root.activeFileModel.fileLayerHeightLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Object height",
                "value": root.activeFileModel.fileObjectHeightLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Filament total",
                "value": root.activeFileModel.fileFilamentTotalLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Slicer",
                "value": root.activeFileModel.fileSlicerLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Nozzle",
                "value": root.activeFileModel.fileNozzleDiameterLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Filament type",
                "value": root.activeFileModel.fileFilamentTypeLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Filament name",
                "value": root.activeFileModel.fileFilamentNameLabelFor(root.activeFileModel.selectedPath)
            },
            {
                "label": "Filament weight",
                "value": root.activeFileModel.fileFilamentWeightTotalLabelFor(root.activeFileModel.selectedPath)
            },
            {"label": "Permissions", "value": root.activeFileModel.selectedPermissions},
            {
                "label": root.readOnlyMode ? "Mode" : "Controls",
                "value": root.readOnlyMode ? "readonly" : "enabled"
            }
        ]
    }

    function selectedMetadataSections() {
        if (!root.activeFileModel || root.activeFileModel.selectedPath.length <= 0) {
            return []
        }
        root.activeFileModel.metadataRevision
        return [
            {
                "section": "File",
                "items": [
                    {"label": "Size", "value": root.activeFileModel.selectedSizeLabel},
                    {"label": "Modified", "value": root.activeFileModel.selectedModifiedLabel}
                ]
            },
            {
                "section": "Print",
                "items": [
                    {
                        "label": "Estimated time",
                        "value": root.activeFileModel.fileEstimatedTimeLabelFor(root.activeFileModel.selectedPath)
                    },
                    {
                        "label": "Layer height",
                        "value": root.activeFileModel.fileLayerHeightLabelFor(root.activeFileModel.selectedPath)
                    },
                    {
                        "label": "Object height",
                        "value": root.activeFileModel.fileObjectHeightLabelFor(root.activeFileModel.selectedPath)
                    }
                ]
            },
            {
                "section": "Filament",
                "items": [
                    {
                        "label": "Filament total",
                        "value": root.activeFileModel.fileFilamentTotalLabelFor(root.activeFileModel.selectedPath)
                    },
                    {
                        "label": "Filament type",
                        "value": root.activeFileModel.fileFilamentTypeLabelFor(root.activeFileModel.selectedPath)
                    },
                    {
                        "label": "Filament name",
                        "value": root.activeFileModel.fileFilamentNameLabelFor(root.activeFileModel.selectedPath)
                    },
                    {
                        "label": "Filament weight",
                        "value": root.activeFileModel.fileFilamentWeightTotalLabelFor(root.activeFileModel.selectedPath)
                    }
                ]
            },
            {
                "section": "Access",
                "items": [
                    {
                        "label": "Slicer",
                        "value": root.activeFileModel.fileSlicerLabelFor(root.activeFileModel.selectedPath)
                    },
                    {
                        "label": "Nozzle",
                        "value": root.activeFileModel.fileNozzleDiameterLabelFor(root.activeFileModel.selectedPath)
                    },
                    {"label": "Permissions", "value": root.activeFileModel.selectedPermissions},
                    {
                        "label": root.readOnlyMode ? "Mode" : "Controls",
                        "value": root.readOnlyMode ? "readonly" : "enabled"
                    }
                ]
            }
        ]
    }

    function selectedPreviewSize() {
        var availableWidth = Math.max(96, root.width - root.metrics.margin * 4 - root.metrics.gap * 4)
        var reservedActionHeight = root.pendingFileAction.length > 0
            ? root.selectedActionPreviewHeight()
            : Math.max(52, Math.round(root.metrics.fontSize * 3.6))
        var reservedMetadataHeight = Math.max(
            root.metrics.portrait ? 220 : 96,
            Math.round(root.metrics.fontSize * (root.metrics.portrait ? 14.0 : 6.2))
        )
        var availableHeight = Math.max(
            96,
            root.height
                - root.metrics.margin * 4
                - root.metrics.gap * 10
                - reservedActionHeight
                - reservedMetadataHeight
        )
        return Math.round(Math.max(96, Math.min(300, availableWidth, availableHeight)))
    }

    function selectedPreviewColumns() {
        var previewAndGap = root.selectedPreviewSize() + root.metrics.gap + Math.max(280, root.metrics.fontSize * 18)
        return width >= previewAndGap ? 2 : 1
    }

    function selectedActionPreviewHeight() {
        return root.metrics.portrait
            ? Math.max(92, Math.round(root.metrics.fontSize * 5.7))
            : Math.max(62, Math.round(root.metrics.fontSize * 4.2))
    }

    component MetadataGroupCard: Rectangle {
        id: metadataGroupCard
        property string sectionTitle: ""
        property var sectionItems: []

        implicitHeight: metadataGroupColumn.implicitHeight + root.metrics.gap * 1.2
        color: "#0b1112"
        border.color: "#263233"
        border.width: 1
        radius: Math.round(root.metrics.fontSize * 0.25)

        ColumnLayout {
            id: metadataGroupColumn
            anchors.fill: parent
            anchors.margins: Math.max(5, Math.round(root.metrics.fontSize * 0.38))
            spacing: Math.max(3, Math.round(root.metrics.fontSize * 0.22))

            Label {
                Layout.fillWidth: true
                color: Theme.mutedText
                text: metadataGroupCard.sectionTitle
                font.bold: true
                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
            }

            Repeater {
                model: metadataGroupCard.sectionItems

                RowLayout {
                    Layout.fillWidth: true
                    spacing: root.metrics.gap

                    Label {
                        Layout.preferredWidth: Math.max(82, Math.round(root.metrics.fontSize * 6.0))
                        color: Theme.mutedText
                        text: modelData.label
                        elide: Text.ElideRight
                        font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                    }

                    Label {
                        Layout.fillWidth: true
                        color: Theme.text
                        text: modelData.value.length > 0 ? modelData.value : "-"
                        elide: Text.ElideRight
                        horizontalAlignment: Text.AlignRight
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.9))
                    }
                }
            }
        }
    }

    component FileActionButton: TactileButton {
        property string actionRole: ""

        Layout.preferredWidth: Math.max(126, Math.round(root.metrics.fontSize * 8.8))
        Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 3.0))
        enabled: !root.readOnlyMode
            && root.activeFileModel
            && root.activeFileModel.selectedPath.length > 0
        fontSize: root.metrics.fontSize
        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
        baseColor: "#121b1d"
        pressedColor: "#172528"
        accentColor: "#354346"
        disabledAccentColor: "#263233"
        iconSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
        disabledOpacity: 0.55
        onClicked: {
            if (actionRole.length > 0) {
                root.requestFileAction(actionRole)
            }
        }
    }

    component RetryButton: TactileButton {
        enabled: !root.loading
        text: "Retry"
        iconName: "update"
        fontSize: root.metrics.fontSize
        baseColor: "#101617"
        pressedColor: "#172528"
        accentColor: "#465456"
        iconSize: Math.max(18, Math.round(root.metrics.fontSize * 1.2))
        disabledOpacity: 0.55
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
                visible: !root.detailPage
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
                        readonly property bool pressedFeedback: chipMouse.pressed

                        Layout.preferredWidth: chipText.implicitWidth + root.metrics.gap * 1.4
                        Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 2.2))
                        scale: chipMouse.pressed ? 0.96 : 1.0
                        transformOrigin: Item.Center
                        color: chipMouse.pressed
                            ? "#26373b"
                            : root.isSortActive(modelData.sortKey) ? "#1b2b2e" : "#101617"
                        opacity: root.isChipEnabled(modelData.sortKey) ? 1.0 : 0.45
                        border.color: chipMouse.pressed ? "#7f9298" : "#263233"
                        border.width: chipMouse.pressed ? 2 : 1
                        radius: Math.round(root.metrics.fontSize * 0.32)
                        Behavior on scale {
                            NumberAnimation { duration: 70; easing.type: Easing.OutQuad }
                        }

                        Rectangle {
                            id: sortChipDepth
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            height: Math.max(2, Math.round(root.metrics.fontSize * 0.16))
                            visible: !chipMouse.pressed && root.isChipEnabled(modelData.sortKey)
                            color: "#050808"
                            opacity: 0.85
                            radius: parent.radius
                        }

                        Label {
                            id: chipText
                            anchors.centerIn: parent
                            color: Theme.mutedText
                            text: root.chipText(modelData.label, modelData.sortKey)
                            font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                        }

                        MouseArea {
                            id: chipMouse
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
                visible: !root.detailPage
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
                    text: root.loadError.length > 0
                        ? "load error"
                        : root.loading ? "Loading files..." : fileList.count + " items"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                }

                RetryButton {
                    visible: root.loadError.length > 0
                    Layout.preferredWidth: Math.max(76, Math.round(root.metrics.fontSize * 5.4))
                    Layout.preferredHeight: Math.max(30, Math.round(root.metrics.fontSize * 2.2))
                    font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.8))
                    onClicked: root.refreshRequested()
                }

                Label {
                    color: Theme.mutedText
                    text: root.readOnlyMode ? "readonly" : "controls"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.85))
                }
            }

            ListView {
                id: fileList
                visible: !root.detailPage && fileList.count > 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 0
                clip: true
                spacing: Math.max(4, Math.round(root.metrics.fontSize * 0.35))
                model: root.activeFileModel
                boundsBehavior: Flickable.StopAtBounds
                flickDeceleration: 2600
                property real savedContentY: 0
                property bool restoringContentY: false

                function boundedContentY(value) {
                    return Math.max(0, Math.min(value, Math.max(0, contentHeight - height)))
                }

                function restoreScrollPosition() {
                    var targetY = savedContentY
                    Qt.callLater(function() {
                        restoringContentY = true
                        contentY = boundedContentY(targetY)
                        restoringContentY = false
                    })
                }

                onContentYChanged: {
                    if (!restoringContentY && (moving || dragging || flicking)) {
                        savedContentY = boundedContentY(contentY)
                    }
                }
                onMovementEnded: savedContentY = boundedContentY(contentY)
                onModelChanged: restoreScrollPosition()
                onCountChanged: restoreScrollPosition()

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                footer: Item {
                    width: fileList.width
                    height: root.metrics.gap
                }

                delegate: Rectangle {
                    readonly property bool pressedFeedback: fileRowMouse.pressed

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
                    scale: fileRowMouse.pressed ? 0.985 : 1.0
                    transformOrigin: Item.Center
                    color: fileRowMouse.pressed
                        ? "#203236"
                        : !isDirectory && root.activeFileModel && root.activeFileModel.selectedPath === path
                        ? "#17282b"
                        : "#101617"
                    border.color: fileRowMouse.pressed
                        ? "#7f9298"
                        : !isDirectory && root.activeFileModel && root.activeFileModel.selectedPath === path
                        ? Theme.color4
                        : "#263233"
                    border.width: fileRowMouse.pressed ? 2 : 1
                    radius: Math.round(root.metrics.fontSize * 0.32)
                    Behavior on scale {
                        NumberAnimation { duration: 70; easing.type: Easing.OutQuad }
                    }

                    Rectangle {
                        id: fileRowDepth
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: Math.max(2, Math.round(root.metrics.fontSize * 0.18))
                        visible: !fileRowMouse.pressed
                        color: "#050808"
                        opacity: 0.75
                        radius: parent.radius
                    }

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
                                id: thumbnailImage
                                anchors.fill: parent
                                anchors.margins: 2
                                source: thumbnailUrl
                                fillMode: Image.PreserveAspectFit
                                asynchronous: thumbnailUrl.indexOf("file:") !== 0
                                cache: true
                                sourceSize.width: width
                                sourceSize.height: height
                                visible: !isDirectory
                                    && thumbnailUrl.length > 0
                                    && thumbnailImage.status === Image.Ready
                            }

                            Label {
                                anchors.centerIn: parent
                                color: Theme.mutedText
                                text: isDirectory ? "DIR" : "G"
                                visible: isDirectory
                                    || thumbnailUrl.length <= 0
                                    || thumbnailImage.status !== Image.Ready
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
                        id: fileRowMouse
                        anchors.fill: parent
                        onClicked: root.enterPath(path, isDirectory)
                    }

                    Component.onCompleted: {
                        if (!isDirectory && thumbnailUrl.length <= 0 && root.activeFileModel) {
                            activeFileModel.requestMetadata(path)
                        }
                    }
                }
            }

            ColumnLayout {
                id: detailPageView
                visible: root.detailPage
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.metrics.gap

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
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

                        GridLayout {
                            id: selectedPreviewAndMetadataLayout
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: root.selectedPreviewColumns()
                            rowSpacing: root.metrics.gap
                            columnSpacing: root.metrics.gap

                            Rectangle {
                                id: selectedPreviewFrame
                                Layout.preferredWidth: root.selectedPreviewSize()
                                Layout.preferredHeight: root.selectedPreviewSize()
                                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
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
                                    asynchronous: true
                                    cache: true
                                    sourceSize.width: width
                                    sourceSize.height: height
                                }
                            }

                            Flickable {
                                id: selectedMetadataFlickable
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.minimumWidth: 0
                                Layout.columnSpan: selectedPreviewFrame.visible ? 1 : selectedPreviewAndMetadataLayout.columns
                                clip: true
                                boundsBehavior: Flickable.StopAtBounds
                                contentWidth: width
                                contentHeight: selectedMetadataGrid.implicitHeight

                                ScrollBar.vertical: ScrollBar {
                                    policy: ScrollBar.AsNeeded
                                }

                                GridLayout {
                                    id: selectedMetadataGrid
                                    width: selectedMetadataFlickable.width
                                    columns: selectedMetadataFlickable.width >= 360 ? 2 : 1
                                    rowSpacing: Math.max(6, Math.round(root.metrics.fontSize * 0.45))
                                    columnSpacing: root.metrics.gap

                                    Repeater {
                                        model: root.selectedMetadataSections()

                                        MetadataGroupCard {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: implicitHeight
                                            sectionTitle: modelData.section
                                            sectionItems: modelData.items
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    id: selectedActionBar
                    visible: root.pendingFileAction.length === 0
                    Layout.fillWidth: true
                    Layout.preferredHeight: visible ? Math.max(52, Math.round(root.metrics.fontSize * 3.6)) : 0
                    Layout.maximumHeight: Layout.preferredHeight
                    Layout.fillHeight: false
                    color: "#0b1112"
                    border.color: "#263233"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: Math.max(5, Math.round(root.metrics.fontSize * 0.35))
                        spacing: root.metrics.gap

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: "Actions"
                                font.bold: true
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: "File actions"
                                elide: Text.ElideRight
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                            }
                        }

                        FileActionButton {
                            actionRole: "print"
                            text: "Print"
                            iconName: "printer"
                        }

                        FileActionButton {
                            actionRole: "delete"
                            text: "Delete"
                            iconName: "cancel"
                        }
                    }
                }

                Rectangle {
                    id: selectedActionPreview
                    visible: root.pendingFileAction.length > 0
                    Layout.fillWidth: true
                    Layout.preferredHeight: visible ? root.selectedActionPreviewHeight() : 0
                    Layout.maximumHeight: Layout.preferredHeight
                    Layout.fillHeight: false
                    color: root.pendingFileAction === "delete" ? "#181311" : "#111819"
                    border.color: root.pendingFileAction === "delete" ? "#4a3430" : "#354346"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.32)

                    GridLayout {
                        id: selectedActionPreviewLayout
                        anchors.fill: parent
                        anchors.margins: root.metrics.gap
                        columns: root.metrics.portrait ? 1 : 2
                        rowSpacing: Math.max(4, Math.round(root.metrics.fontSize * 0.28))
                        columnSpacing: root.metrics.gap

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 0

                            Label {
                                Layout.fillWidth: true
                                color: Theme.text
                                text: "Confirmation preview only"
                                font.bold: true
                                font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                            }

                            Label {
                                Layout.fillWidth: true
                                color: Theme.mutedText
                                text: (root.pendingFileAction === "delete" ? "Delete " : "Print ")
                                    + (root.activeFileModel ? root.activeFileModel.selectedDisplayName : "")
                                elide: Text.ElideMiddle
                                font.pixelSize: Math.max(10, Math.round(root.metrics.fontSize * 0.72))
                            }
                        }

                        RowLayout {
                            id: selectedActionPreviewButtonRow
                            Layout.fillWidth: root.metrics.portrait
                            Layout.alignment: root.metrics.portrait ? Qt.AlignRight : Qt.AlignVCenter
                            Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 3.0))
                            spacing: root.metrics.gap

                            FileActionButton {
                                Layout.fillWidth: root.metrics.portrait
                                text: "Confirm"
                                enabled: true
                                iconName: "confirm"
                                onClicked: {
                                    root.fileActionRequested(
                                        root.pendingFileAction,
                                        root.activeFileModel ? root.activeFileModel.selectedPath : ""
                                    )
                                    root.clearFileAction()
                                }
                            }

                            FileActionButton {
                                Layout.fillWidth: root.metrics.portrait
                                text: "Dismiss"
                                enabled: true
                                iconName: "cancel"
                                onClicked: root.clearFileAction()
                            }
                        }
                    }
                }

                Rectangle {
                    id: selectedActionFeedback
                    visible: root.controlFeedbackText().length > 0
                    Layout.fillWidth: true
                    Layout.preferredHeight: visible ? Math.max(34, Math.round(root.metrics.fontSize * 2.35)) : 0
                    Layout.fillHeight: false
                    color: root.controlError.length > 0 ? "#181311" : "#111819"
                    border.color: root.controlError.length > 0 ? "#4a3430" : "#354346"
                    border.width: 1
                    radius: Math.round(root.metrics.fontSize * 0.28)

                    Label {
                        anchors.fill: parent
                        anchors.leftMargin: root.metrics.gap
                        anchors.rightMargin: root.metrics.gap
                        color: Theme.text
                        text: root.controlFeedbackText()
                        elide: Text.ElideRight
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: !root.detailPage && fileList.count === 0
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
                        text: root.loadError.length > 0
                            ? root.loadError
                            : "Read-only file browser; print actions stay out of this page."
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        font.pixelSize: Math.max(11, Math.round(root.metrics.fontSize * 0.82))
                    }

                    RetryButton {
                        visible: root.loadError.length > 0
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: Math.max(132, Math.round(root.metrics.fontSize * 8.8))
                        Layout.preferredHeight: Math.max(44, Math.round(root.metrics.fontSize * 3.0))
                        font.pixelSize: Math.max(12, Math.round(root.metrics.fontSize * 0.88))
                        onClicked: root.refreshRequested()
                    }
                }
            }
        }
    }
}
