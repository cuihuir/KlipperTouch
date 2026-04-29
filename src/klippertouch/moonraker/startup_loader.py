from PySide6.QtCore import QObject, QThread, Signal, Slot

from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.probe import build_basic_status_from_client, build_status_from_client


class _StartupDataWorker(QObject):
    statusLoaded = Signal(object)
    temperatureStoreLoaded = Signal(object)
    filesLoaded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, client: MoonrakerClient) -> None:
        super().__init__()
        self._client = client

    @Slot()
    def run(self) -> None:
        try:
            self.statusLoaded.emit(build_basic_status_from_client(self._client))
        except Exception as exc:
            self.failed.emit(str(exc))

        try:
            self.statusLoaded.emit(build_status_from_client(self._client))
        except Exception as exc:
            self.failed.emit(str(exc))

        try:
            self.temperatureStoreLoaded.emit(self._client.get_temperature_store())
        except Exception as exc:
            self.failed.emit(str(exc))

        try:
            self.filesLoaded.emit(self._client.get_gcode_file_list())
        except Exception as exc:
            self.failed.emit(str(exc))

        self.finished.emit()


class StartupDataLoader(QObject):
    statusLoaded = Signal(object)
    temperatureStoreLoaded = Signal(object)
    filesLoaded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, client: MoonrakerClient) -> None:
        super().__init__()
        self._client = client
        self._thread: QThread | None = None
        self._worker: _StartupDataWorker | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        thread = QThread(self)
        worker = _StartupDataWorker(self._client)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.statusLoaded.connect(self.statusLoaded.emit)
        worker.temperatureStoreLoaded.connect(self.temperatureStoreLoaded.emit)
        worker.filesLoaded.connect(self.filesLoaded.emit)
        worker.failed.connect(self.failed.emit)
        worker.finished.connect(self.finished.emit)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_worker)
        self._thread = thread
        self._worker = worker
        thread.start()

    def stop(self, timeout_ms: int = 15000) -> None:
        thread = self._thread
        if thread is None:
            return
        if thread.isRunning():
            thread.quit()
            thread.wait(timeout_ms)
        self._thread = None
        self._worker = None

    @Slot()
    def _clear_worker(self) -> None:
        self._thread = None
        self._worker = None


def coerce_printer_status(value: object) -> PrinterStatus | None:
    if isinstance(value, PrinterStatus):
        return value
    return None


def coerce_mapping(value: object) -> dict[str, object] | None:
    if isinstance(value, dict):
        return value
    return None


def coerce_file_list(value: object) -> list[dict[str, object]] | None:
    if not isinstance(value, list):
        return None
    files: list[dict[str, object]] = []
    for item in value:
        if isinstance(item, dict):
            files.append(item)
    return files
