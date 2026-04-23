from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)

from klippertouch.domain.gcode_files import GCodeFile

EMPTY_INDEX = QModelIndex()


class GCodeFileListModel(QAbstractListModel):
    PATH_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    DISPLAY_NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 2
    SIZE_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 3
    MODIFIED_ROLE = int(Qt.ItemDataRole.UserRole) + 4
    PERMISSIONS_ROLE = int(Qt.ItemDataRole.UserRole) + 5

    def __init__(self) -> None:
        super().__init__()
        self._files: tuple[GCodeFile, ...] = ()

    def set_files(self, files: tuple[GCodeFile, ...]) -> None:
        self.beginResetModel()
        self._files = tuple(files)
        self.endResetModel()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = EMPTY_INDEX,
    ) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._files)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object:
        if not index.isValid() or not 0 <= index.row() < len(self._files):
            return None

        item = self._files[index.row()]
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
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.PATH_ROLE: QByteArray(b"path"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.SIZE_LABEL_ROLE: QByteArray(b"sizeLabel"),
            self.MODIFIED_ROLE: QByteArray(b"modified"),
            self.PERMISSIONS_ROLE: QByteArray(b"permissions"),
        }
