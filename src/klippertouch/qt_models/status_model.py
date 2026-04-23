from PySide6.QtCore import Property, QObject, Signal

from klippertouch.domain.printer import PrinterStatus


class StatusModel(QObject):
    statusChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = PrinterStatus()

    def set_status(self, status: PrinterStatus) -> None:
        self._status = status
        self.statusChanged.emit()

    @Property(str, notify=statusChanged)
    def hostname(self) -> str:
        return self._status.hostname

    @Property(str, notify=statusChanged)
    def klippyState(self) -> str:
        return self._status.klippy_state

    @Property(str, notify=statusChanged)
    def klipperVersion(self) -> str:
        return self._status.klipper_version

    @Property(str, notify=statusChanged)
    def moonrakerVersion(self) -> str:
        return self._status.moonraker_version

    @Property(int, notify=statusChanged)
    def objectCount(self) -> int:
        return self._status.object_count
