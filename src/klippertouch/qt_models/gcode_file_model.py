from dataclasses import replace

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)

from klippertouch.domain.gcode_files import (
    GCodeFile,
    GCodeFileEntry,
    browser_entries_for_directory,
    thumbnail_from_metadata,
)

EMPTY_INDEX = QModelIndex()


class GCodeFileListModel(QAbstractListModel):
    currentPathChanged = Signal()
    sortKeyChanged = Signal()
    filterTextChanged = Signal()
    selectedPathChanged = Signal()
    thumbnailChanged = Signal()

    PATH_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    DISPLAY_NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 2
    SIZE_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 3
    MODIFIED_ROLE = int(Qt.ItemDataRole.UserRole) + 4
    PERMISSIONS_ROLE = int(Qt.ItemDataRole.UserRole) + 5
    IS_DIRECTORY_ROLE = int(Qt.ItemDataRole.UserRole) + 6
    MODIFIED_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 7
    THUMBNAIL_URL_ROLE = int(Qt.ItemDataRole.UserRole) + 8

    def __init__(self) -> None:
        super().__init__()
        self._files: tuple[GCodeFile, ...] = ()
        self._entries: tuple[GCodeFileEntry, ...] = ()
        self._current_path = ""
        self._sort_key = "name"
        self._sort_descending = False
        self._filter_text = ""
        self._selected_path = ""
        self._thumbnail_revision = 0

    def set_files(self, files: tuple[GCodeFile, ...]) -> None:
        files = _normalized_file_snapshot(files)
        files = _preserve_loaded_thumbnails(files, self._files)
        if files == self._files:
            return
        self.beginResetModel()
        self._files = files
        self._entries = browser_entries_for_directory(
            self._files,
            directory=self._current_path,
            sort_key=self._sort_key,
            filter_text=self._filter_text,
            sort_descending=self._sort_descending,
        )
        selection_removed = bool(self._selected_path) and self._file_for_name(
            self._selected_path
        ) is None
        if selection_removed:
            self._selected_path = ""
        self.endResetModel()
        if selection_removed:
            self.selectedPathChanged.emit()

    @Property(str, notify=currentPathChanged)
    def currentPath(self) -> str:
        return self._current_path

    @Property(str, notify=sortKeyChanged)
    def sortKey(self) -> str:
        return self._sort_key

    @Property(bool, notify=sortKeyChanged)
    def sortDescending(self) -> bool:
        return self._sort_descending

    @Property(str, notify=filterTextChanged)
    def filterText(self) -> str:
        return self._filter_text

    @Property(str, notify=selectedPathChanged)
    def selectedPath(self) -> str:
        return self._selected_path

    @Property(str, notify=selectedPathChanged)
    def selectedDisplayName(self) -> str:
        file = self._file_for_name(self._selected_path)
        return file.display_name if file is not None else ""

    @Property(str, notify=selectedPathChanged)
    def selectedSizeLabel(self) -> str:
        return self.fileSizeLabelFor(self._selected_path)

    @Property(str, notify=selectedPathChanged)
    def selectedModifiedLabel(self) -> str:
        return self.fileModifiedLabelFor(self._selected_path)

    @Property(str, notify=selectedPathChanged)
    def selectedPermissions(self) -> str:
        file = self._file_for_name(self._selected_path)
        return file.permissions if file is not None else ""

    @Property(str, notify=selectedPathChanged)
    def selectedThumbnailUrl(self) -> str:
        file = self._file_for_name(self._selected_path)
        return file.thumbnail_url if file is not None else ""

    @Property(int, notify=thumbnailChanged)
    def thumbnailRevision(self) -> int:
        return self._thumbnail_revision

    @Property(bool, notify=currentPathChanged)
    def canGoUp(self) -> bool:
        return bool(self._current_path)

    @Property(list, notify=currentPathChanged)
    def breadcrumbs(self) -> list[str]:
        return ["gcodes", *[part for part in self._current_path.split("/") if part]]

    @Slot(str)
    def setCurrentPath(self, path: str) -> None:  # noqa: N802
        normalized = path.strip().strip("/")
        if normalized == self._current_path:
            return
        self._current_path = normalized
        self._reset_entries()
        self.currentPathChanged.emit()

    @Slot(str)
    def setSortKey(self, sort_key: str) -> None:  # noqa: N802
        if sort_key not in {"name", "date", "size"}:
            return
        if sort_key == self._sort_key:
            self._sort_descending = not self._sort_descending
        else:
            self._sort_key = sort_key
            self._sort_descending = True
        self._sort_key = sort_key
        self._reset_entries()
        self.sortKeyChanged.emit()

    @Slot(str)
    def setFilterText(self, filter_text: str) -> None:  # noqa: N802
        normalized = filter_text.strip()
        if normalized == self._filter_text:
            return
        self._filter_text = normalized
        self._reset_entries()
        self.filterTextChanged.emit()

    @Slot(int)
    def setBreadcrumbIndex(self, index: int) -> None:  # noqa: N802
        if index <= 0:
            self.setCurrentPath("")
            return
        parts = [part for part in self._current_path.split("/") if part]
        if index > len(parts):
            return
        self.setCurrentPath("/".join(parts[:index]))

    @Slot()
    def goUp(self) -> None:  # noqa: N802
        if not self._current_path:
            return
        parent = "/".join(self._current_path.split("/")[:-1])
        self.setCurrentPath(parent)

    @Slot(str, bool)
    def selectPath(self, path: str, is_directory: bool) -> None:  # noqa: N802
        if is_directory:
            return
        clean = path.strip().strip("/")
        if self._file_for_name(clean) is None or clean == self._selected_path:
            return
        self._selected_path = clean
        self.selectedPathChanged.emit()

    @Slot()
    def clearSelection(self) -> None:  # noqa: N802
        if not self._selected_path:
            return
        self._selected_path = ""
        self.selectedPathChanged.emit()

    @Slot(str, dict, str)
    def setFileMetadata(  # noqa: N802
        self,
        path: str,
        metadata: dict[str, object],
        thumbnail_base_url: str,
    ) -> None:
        clean = path.strip().strip("/")
        thumbnail_path = thumbnail_from_metadata(clean, metadata)
        if not thumbnail_path:
            return
        separator = "" if thumbnail_base_url.endswith("/") else "/"
        thumbnail_url = f"{thumbnail_base_url}{separator}{thumbnail_path}"
        files = []
        changed_index = -1
        for index, file in enumerate(self._files):
            if file.path != clean:
                files.append(file)
                continue
            if file.thumbnail_url == thumbnail_url:
                return
            files.append(
                GCodeFile(
                    path=file.path,
                    display_name=file.display_name,
                    modified=file.modified,
                    size=file.size,
                    permissions=file.permissions,
                    thumbnail_url=thumbnail_url,
                )
            )
            changed_index = index
        if changed_index < 0:
            return
        self._files = tuple(files)
        self._thumbnail_revision += 1
        row = self._row_for_path(clean)
        if row >= 0:
            item_index = self.index(row, 0)
            self.dataChanged.emit(item_index, item_index, [self.THUMBNAIL_URL_ROLE])
        self.thumbnailChanged.emit()
        if clean == self._selected_path:
            self.selectedPathChanged.emit()

    def _reset_entries(self) -> None:
        self.beginResetModel()
        self._entries = browser_entries_for_directory(
            self._files,
            directory=self._current_path,
            sort_key=self._sort_key,
            filter_text=self._filter_text,
            sort_descending=self._sort_descending,
        )
        self.endResetModel()

    @Slot(str, result=str)
    def fileSizeLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.size_label if file is not None else "-"

    @Slot(str, result=str)
    def fileModifiedLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.modified_label if file is not None else "-"

    @Slot(str, result=str)
    def filePathFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.path if file is not None else ""

    @Slot(str, result=str)
    def fileThumbnailUrlFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.thumbnail_url if file is not None else ""

    def _file_for_name(self, filename: str) -> GCodeFile | None:
        clean = filename.strip().strip("/")
        if not clean:
            return None
        for file in self._files:
            if file.path == clean or file.display_name == clean:
                return file
        return None

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = EMPTY_INDEX,
    ) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._entries)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object:
        if not index.isValid() or not 0 <= index.row() < len(self._entries):
            return None

        item = self._entries[index.row()]
        if role == self.PATH_ROLE:
            return item.path
        if role == self.DISPLAY_NAME_ROLE:
            return item.display_name
        if role == self.SIZE_LABEL_ROLE:
            return item.size_label
        if role == self.MODIFIED_ROLE:
            return item.modified
        if role == self.PERMISSIONS_ROLE:
            return item.permissions
        if role == self.IS_DIRECTORY_ROLE:
            return item.is_directory
        if role == self.MODIFIED_LABEL_ROLE:
            return item.modified_label
        if role == self.THUMBNAIL_URL_ROLE:
            if item.is_directory:
                return ""
            file = self._file_for_name(item.path)
            return file.thumbnail_url if file is not None else ""
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.PATH_ROLE: QByteArray(b"path"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.SIZE_LABEL_ROLE: QByteArray(b"sizeLabel"),
            self.MODIFIED_ROLE: QByteArray(b"modified"),
            self.PERMISSIONS_ROLE: QByteArray(b"permissions"),
            self.IS_DIRECTORY_ROLE: QByteArray(b"isDirectory"),
            self.MODIFIED_LABEL_ROLE: QByteArray(b"modifiedLabel"),
            self.THUMBNAIL_URL_ROLE: QByteArray(b"thumbnailUrl"),
        }

    def _row_for_path(self, path: str) -> int:
        for row, entry in enumerate(self._entries):
            if entry.path == path:
                return row
        return -1


def _normalized_file_snapshot(files: tuple[GCodeFile, ...]) -> tuple[GCodeFile, ...]:
    return tuple(sorted(tuple(files), key=lambda file: file.path))


def _preserve_loaded_thumbnails(
    files: tuple[GCodeFile, ...],
    previous_files: tuple[GCodeFile, ...],
) -> tuple[GCodeFile, ...]:
    previous_by_path = {
        file.path: file.thumbnail_url for file in previous_files if file.thumbnail_url
    }
    if not previous_by_path:
        return files
    return tuple(
        replace(file, thumbnail_url=previous_by_path[file.path])
        if not file.thumbnail_url and file.path in previous_by_path
        else file
        for file in files
    )
