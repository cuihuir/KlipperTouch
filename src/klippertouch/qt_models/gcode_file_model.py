from dataclasses import replace
from typing import Any

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
    metadataChanged = Signal()
    metadataRequested = Signal(str)

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
        self._metadata_revision = 0

    def set_files(self, files: tuple[GCodeFile, ...]) -> None:
        files = _normalized_file_snapshot(files)
        files = _preserve_loaded_thumbnails(files, self._files)
        if files == self._files:
            return
        previous_selection = self._selected_path
        self.beginResetModel()
        self._files = files
        self._entries = browser_entries_for_directory(
            self._files,
            directory=self._current_path,
            sort_key=self._sort_key,
            filter_text=self._filter_text,
            sort_descending=self._sort_descending,
        )
        self._selected_path = self._selection_for_visible_entries()
        self.endResetModel()
        if self._selected_path != previous_selection:
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

    @Property(str, notify=selectedPathChanged)
    def selectedPreviewThumbnailUrl(self) -> str:
        file = self._file_for_name(self._selected_path)
        return file.preview_thumbnail_url if file is not None else ""

    @Property(int, notify=thumbnailChanged)
    def thumbnailRevision(self) -> int:
        return self._thumbnail_revision

    @Property(int, notify=metadataChanged)
    def metadataRevision(self) -> int:
        return self._metadata_revision

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

    @Slot(str)
    def requestMetadata(self, path: str) -> None:  # noqa: N802
        clean = _normalize_gcode_request_path(path)
        if self._file_for_name(clean) is None:
            return
        self.metadataRequested.emit(clean)

    @Slot(str)
    def removeFile(self, path: str) -> None:  # noqa: N802
        clean = path.strip().strip("/")
        if not clean or self._file_for_name(clean) is None:
            return
        self.set_files(tuple(file for file in self._files if file.path != clean))

    @Slot(str, dict, str)
    def setFileMetadata(  # noqa: N802
        self,
        path: str,
        metadata: dict[str, object],
        thumbnail_base_url: str,
    ) -> None:
        clean = path.strip().strip("/")
        thumbnail_path = thumbnail_from_metadata(clean, metadata)
        preview_thumbnail_path = thumbnail_from_metadata(clean, metadata, prefer_small=False)
        separator = "" if thumbnail_base_url.endswith("/") else "/"
        thumbnail_url = (
            f"{thumbnail_base_url}{separator}{thumbnail_path}" if thumbnail_path else ""
        )
        preview_thumbnail_url = (
            f"{thumbnail_base_url}{separator}{preview_thumbnail_path}"
            if preview_thumbnail_path
            else thumbnail_url
        )
        files = []
        changed_index = -1
        thumbnail_changed = False
        metadata_changed = False
        for index, file in enumerate(self._files):
            if file.path != clean:
                files.append(file)
                continue
            next_file = GCodeFile(
                path=file.path,
                display_name=file.display_name,
                modified=file.modified,
                size=file.size,
                permissions=file.permissions,
                thumbnail_url=thumbnail_url or file.thumbnail_url,
                preview_thumbnail_url=preview_thumbnail_url or file.preview_thumbnail_url,
                **_metadata_fields(metadata, file),
            )
            if (
                file.thumbnail_url != next_file.thumbnail_url
                or file.preview_thumbnail_url != next_file.preview_thumbnail_url
            ):
                thumbnail_changed = True
            if (
                file.estimated_time != next_file.estimated_time
                or file.filament_total != next_file.filament_total
                or file.object_height != next_file.object_height
                or file.layer_height != next_file.layer_height
                or file.slicer != next_file.slicer
                or file.slicer_version != next_file.slicer_version
                or file.nozzle_diameter != next_file.nozzle_diameter
                or file.filament_type != next_file.filament_type
                or file.filament_name != next_file.filament_name
                or file.filament_weight_total != next_file.filament_weight_total
            ):
                metadata_changed = True
            if file == next_file:
                return
            files.append(next_file)
            changed_index = index
        if changed_index < 0:
            return
        self._files = tuple(files)
        row = self._row_for_path(clean)
        if thumbnail_changed:
            self._thumbnail_revision += 1
            if row >= 0:
                item_index = self.index(row, 0)
                self.dataChanged.emit(item_index, item_index, [self.THUMBNAIL_URL_ROLE])
            self.thumbnailChanged.emit()
        if metadata_changed:
            self._metadata_revision += 1
            self.metadataChanged.emit()
        if thumbnail_changed and clean == self._selected_path:
            self.selectedPathChanged.emit()

    @Slot(str, result=str)
    def fileEstimatedTimeLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.estimated_time_label if file is not None else "-"

    @Slot(str, result=str)
    def fileFilamentTotalLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.filament_total_label if file is not None else "-"

    @Slot(str, result=str)
    def fileObjectHeightLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.object_height_label if file is not None else "-"

    @Slot(str, result=float)
    def fileObjectHeightFor(self, filename: str) -> float:  # noqa: N802
        file = self._file_for_name(filename)
        return file.object_height if file is not None else 0.0

    @Slot(str, result=str)
    def fileLayerHeightLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.layer_height_label if file is not None else "-"

    @Slot(str, result=str)
    def fileSlicerLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.slicer_label if file is not None else "-"

    @Slot(str, result=str)
    def fileNozzleDiameterLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.nozzle_diameter_label if file is not None else "-"

    @Slot(str, result=str)
    def fileFilamentTypeLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.filament_type_label if file is not None else "-"

    @Slot(str, result=str)
    def fileFilamentNameLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.filament_name_label if file is not None else "-"

    @Slot(str, result=str)
    def fileFilamentWeightTotalLabelFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.filament_weight_total_label if file is not None else "-"

    def _reset_entries(self) -> None:
        previous_selection = self._selected_path
        self.beginResetModel()
        self._entries = browser_entries_for_directory(
            self._files,
            directory=self._current_path,
            sort_key=self._sort_key,
            filter_text=self._filter_text,
            sort_descending=self._sort_descending,
        )
        self._selected_path = self._selection_for_visible_entries()
        self.endResetModel()
        if self._selected_path != previous_selection:
            self.selectedPathChanged.emit()

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

    @Slot(str, result=str)
    def filePreviewThumbnailUrlFor(self, filename: str) -> str:  # noqa: N802
        file = self._file_for_name(filename)
        return file.preview_thumbnail_url if file is not None else ""

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

    def _selection_for_visible_entries(self) -> str:
        if self._selected_path and any(
            entry.path == self._selected_path and not entry.is_directory
            for entry in self._entries
        ):
            return self._selected_path
        for entry in self._entries:
            if not entry.is_directory:
                return entry.path
        return ""


def _normalized_file_snapshot(files: tuple[GCodeFile, ...]) -> tuple[GCodeFile, ...]:
    return tuple(sorted(tuple(files), key=lambda file: file.path))


def _normalize_gcode_request_path(path: str) -> str:
    clean = path.strip().replace("\\", "/").strip("/")
    marker = "gcodes/"
    if clean.startswith(marker):
        clean = clean[len(marker) :]
    if f"/{marker}" in clean:
        clean = clean.rsplit(f"/{marker}", 1)[1]
    return clean.strip("/")


def _preserve_loaded_thumbnails(
    files: tuple[GCodeFile, ...],
    previous_files: tuple[GCodeFile, ...],
) -> tuple[GCodeFile, ...]:
    previous_by_path = {
        file.path: file
        for file in previous_files
        if (
            file.thumbnail_url
            or file.preview_thumbnail_url
            or file.estimated_time > 0
            or file.filament_total > 0
            or file.object_height > 0
            or file.layer_height > 0
            or file.slicer
            or file.slicer_version
            or file.nozzle_diameter > 0
            or file.filament_type
            or file.filament_name
            or file.filament_weight_total > 0
        )
    }
    if not previous_by_path:
        return files
    return tuple(_preserve_previous_metadata(file, previous_by_path) for file in files)


def _preserve_previous_metadata(
    file: GCodeFile,
    previous_by_path: dict[str, GCodeFile],
) -> GCodeFile:
    previous = previous_by_path.get(file.path)
    if previous is None:
        return file
    if file.modified != previous.modified or file.size != previous.size:
        return file
    return replace(
        file,
        thumbnail_url=file.thumbnail_url or previous.thumbnail_url,
        preview_thumbnail_url=file.preview_thumbnail_url or previous.preview_thumbnail_url,
        estimated_time=file.estimated_time or previous.estimated_time,
        filament_total=file.filament_total or previous.filament_total,
        object_height=file.object_height or previous.object_height,
        layer_height=file.layer_height or previous.layer_height,
        slicer=file.slicer or previous.slicer,
        slicer_version=file.slicer_version or previous.slicer_version,
        nozzle_diameter=file.nozzle_diameter or previous.nozzle_diameter,
        filament_type=file.filament_type or previous.filament_type,
        filament_name=file.filament_name or previous.filament_name,
        filament_weight_total=file.filament_weight_total or previous.filament_weight_total,
    )


def _metadata_fields(metadata: dict[str, object], file: GCodeFile) -> dict[str, Any]:
    return {
        "estimated_time": _metadata_float(metadata, "estimated_time", file.estimated_time),
        "filament_total": _metadata_float(metadata, "filament_total", file.filament_total),
        "object_height": _metadata_float(metadata, "object_height", file.object_height),
        "layer_height": _metadata_float(metadata, "layer_height", file.layer_height),
        "slicer": _metadata_string(metadata, "slicer", file.slicer),
        "slicer_version": _metadata_string(metadata, "slicer_version", file.slicer_version),
        "nozzle_diameter": _metadata_float(
            metadata,
            "nozzle_diameter",
            file.nozzle_diameter,
        ),
        "filament_type": _metadata_string(metadata, "filament_type", file.filament_type),
        "filament_name": _metadata_string(metadata, "filament_name", file.filament_name),
        "filament_weight_total": _metadata_float(
            metadata,
            "filament_weight_total",
            file.filament_weight_total,
        ),
    }


def _metadata_float(metadata: dict[str, object], key: str, fallback: float) -> float:
    if key not in metadata:
        return fallback
    value = metadata[key]
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        return fallback
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return fallback


def _metadata_string(metadata: dict[str, object], key: str, fallback: str) -> str:
    value = metadata.get(key, fallback)
    if isinstance(value, bool) or value is None:
        return fallback
    return str(value).strip()
