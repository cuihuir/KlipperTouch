from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

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

_DEFAULT_INDEX = QModelIndex()


@dataclass
class NotificationItem:
    level: str
    title: str
    message: str
    source: str
    timestamp: str
    read: bool
    sticky: bool
    action_panel: str


class NotificationModel(QAbstractListModel):
    LevelRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    MessageRole = Qt.ItemDataRole.UserRole + 3
    SourceRole = Qt.ItemDataRole.UserRole + 4
    TimestampRole = Qt.ItemDataRole.UserRole + 5
    ReadRole = Qt.ItemDataRole.UserRole + 6
    StickyRole = Qt.ItemDataRole.UserRole + 7
    ActionPanelRole = Qt.ItemDataRole.UserRole + 8

    unreadCountChanged = Signal()
    countChanged = Signal()
    toastRequested = Signal(str, str, str)

    def __init__(self, max_items: int = 100) -> None:
        super().__init__()
        self._items: list[NotificationItem] = []
        self._max_items = max(1, max_items)
        self._unread_count = 0

    @Property(int, notify=unreadCountChanged)
    def unreadCount(self) -> int:  # noqa: N802
        return self._unread_count

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._items)

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _DEFAULT_INDEX,
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object:
        if not index.isValid() or index.row() < 0 or index.row() >= len(self._items):
            return None
        item = self._items[index.row()]
        if role == self.LevelRole:
            return item.level
        if role == self.TitleRole:
            return item.title
        if role == self.MessageRole:
            return item.message
        if role == self.SourceRole:
            return item.source
        if role == self.TimestampRole:
            return item.timestamp
        if role == self.ReadRole:
            return item.read
        if role == self.StickyRole:
            return item.sticky
        if role == self.ActionPanelRole:
            return item.action_panel
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.LevelRole: QByteArray(b"level"),
            self.TitleRole: QByteArray(b"title"),
            self.MessageRole: QByteArray(b"message"),
            self.SourceRole: QByteArray(b"source"),
            self.TimestampRole: QByteArray(b"timestamp"),
            self.ReadRole: QByteArray(b"read"),
            self.StickyRole: QByteArray(b"sticky"),
            self.ActionPanelRole: QByteArray(b"actionPanel"),
        }

    @Slot(str, str, str, str, bool, str)
    def addNotification(  # noqa: N802
        self,
        level: str,
        title: str,
        message: str = "",
        source: str = "",
        sticky: bool = False,
        action_panel: str = "",
    ) -> None:
        item = NotificationItem(
            level=level.strip() or "info",
            title=title.strip(),
            message=message.strip(),
            source=source.strip(),
            timestamp=datetime.now().strftime("%H:%M"),
            read=False,
            sticky=sticky,
            action_panel=action_panel.strip(),
        )
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._items.insert(0, item)
        self.endInsertRows()
        self._trim_history()
        self.countChanged.emit()
        self._refresh_unread_count()

    @Slot(list)
    def addMoonrakerWarnings(self, warnings: list[str] | tuple[str, ...]) -> None:  # noqa: N802
        seen = {
            (item.level, item.title, item.message, item.source)
            for item in self._items
        }
        for warning in warnings:
            message = str(warning).strip()
            key = ("warning", "Moonraker warning", message, "moonraker")
            if not message or key in seen:
                continue
            self.addNotification("warning", "Moonraker warning", message, "moonraker", True, "")
            seen.add(key)

    @Slot(str, str, str)
    def showToast(self, level: str, title: str, message: str = "") -> None:  # noqa: N802
        self.toastRequested.emit(level.strip() or "info", title.strip(), message.strip())

    @Slot()
    def markAllRead(self) -> None:  # noqa: N802
        if not self._items:
            return
        for item in self._items:
            item.read = True
        top_left = self.index(0, 0)
        bottom_right = self.index(len(self._items) - 1, 0)
        self.dataChanged.emit(top_left, bottom_right, [self.ReadRole])
        self._set_unread_count(0)

    @Slot()
    def clear(self) -> None:
        if not self._items:
            return
        self.beginRemoveRows(QModelIndex(), 0, len(self._items) - 1)
        self._items.clear()
        self.endRemoveRows()
        self.countChanged.emit()
        self._set_unread_count(0)

    def _trim_history(self) -> None:
        if len(self._items) <= self._max_items:
            return
        first_removed = self._max_items
        last_removed = len(self._items) - 1
        self.beginRemoveRows(QModelIndex(), first_removed, last_removed)
        del self._items[first_removed:]
        self.endRemoveRows()

    def _set_unread_count(self, value: int) -> None:
        if value == self._unread_count:
            return
        self._unread_count = value
        self.unreadCountChanged.emit()

    def _refresh_unread_count(self) -> None:
        self._set_unread_count(sum(1 for item in self._items if not item.read))
