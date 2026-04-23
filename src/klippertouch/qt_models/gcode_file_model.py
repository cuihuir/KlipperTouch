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
)

EMPTY_INDEX = QModelIndex()


class GCodeFileListModel(QAbstractListModel):
    currentPathChanged = Signal()
    sortKeyChanged = Signal()

    PATH_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    DISPLAY_NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 2
    SIZE_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 3
    MODIFIED_ROLE = int(Qt.ItemDataRole.UserRole) + 4
    PERMISSIONS_ROLE = int(Qt.ItemDataRole.UserRole) + 5
    IS_DIRECTORY_ROLE = int(Qt.ItemDataRole.UserRole) + 6
    MODIFIED_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 7

    def __init__(self) -> None:
        super().__init__()
        self._files: tuple[GCodeFile, ...] = ()
        self._entries: tuple[GCodeFileEntry, ...] = ()
        self._current_path = ""
        self._sort_key = "name"

    def set_files(self, files: tuple[GCodeFile, ...]) -> None:
        self.beginResetModel()
        self._files = tuple(files)
        self._entries = browser_entries_for_directory(
            self._files,
            directory=self._current_path,
            sort_key=self._sort_key,
        )
        self.endResetModel()

    @Property(str, notify=currentPathChanged)
    def currentPath(self) -> str:
        return self._current_path

    @Property(str, notify=sortKeyChanged)
    def sortKey(self) -> str:
        return self._sort_key

    @Property(bool, notify=currentPathChanged)
    def canGoUp(self) -> bool:
        return bool(self._current_path)

    @Property(list, notify=currentPathChanged)
    def breadcrumbs(self) -> list[str]:
        return ["gcodes", *[part for part in self._current_path.split("/") if part]]

    @Slot(str)
    def setCurrentPath(self, path: str) -> None:  # noqa: N802
        if path == self._current_path:
            return
        self._current_path = path.strip().strip("/")
        self._reset_entries()
        self.currentPathChanged.emit()

    @Slot(str)
    def setSortKey(self, sort_key: str) -> None:  # noqa: N802
        if sort_key not in {"name", "date", "size"} or sort_key == self._sort_key:
            return
        self._sort_key = sort_key
        self._reset_entries()
        self.sortKeyChanged.emit()

    @Slot()
    def goUp(self) -> None:  # noqa: N802
        if not self._current_path:
            return
        parent = "/".join(self._current_path.split("/")[:-1])
        self.setCurrentPath(parent)

    def _reset_entries(self) -> None:
        self.beginResetModel()
        self._entries = browser_entries_for_directory(
            self._files,
            directory=self._current_path,
            sort_key=self._sort_key,
        )
        self.endResetModel()

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
        }
