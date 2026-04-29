from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from klippertouch.domain.gcode_files import files_from_moonraker
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.status_model import StatusModel


class _FileListWorker(QObject):
    completed = Signal(object)
    finished = Signal()

    def __init__(self, client: MoonrakerClient) -> None:
        super().__init__()
        self._client = client

    @Slot()
    def run(self) -> None:
        try:
            self.completed.emit(self._client.get_gcode_file_list())
        except Exception:
            pass
        self.finished.emit()


class _MetadataWorker(QObject):
    completed = Signal(str, object)
    finished = Signal()

    def __init__(self, client: MoonrakerClient, filename: str) -> None:
        super().__init__()
        self._client = client
        self._filename = filename

    @Slot()
    def run(self) -> None:
        try:
            self.completed.emit(
                self._filename,
                self._client.get_gcode_file_metadata(self._filename),
            )
        except Exception:
            pass
        self.finished.emit()


class GCodeFileRefresh(QObject):
    refreshFinished = Signal()
    metadataRefreshFinished = Signal()

    def __init__(
        self,
        client: MoonrakerClient,
        model: GCodeFileListModel,
        refresh_interval_ms: int = 10000,
        metadata_interval_ms: int = 350,
        status_model: StatusModel | None = None,
    ) -> None:
        super().__init__()
        self._client = client
        self._model = model
        self._status_model = status_model
        self._timer = QTimer(self)
        self._timer.setInterval(refresh_interval_ms)
        self._timer.timeout.connect(self.refresh_once)
        self._metadata_timer = QTimer(self)
        self._metadata_timer.setInterval(metadata_interval_ms)
        self._metadata_timer.timeout.connect(self.refresh_metadata_once)
        self._metadata_queue: list[str] = []
        self._metadata_loaded: set[str] = set()
        self._file_refresh_thread: QThread | None = None
        self._file_refresh_worker: _FileListWorker | None = None
        self._metadata_refresh_thread: QThread | None = None
        self._metadata_refresh_worker: _MetadataWorker | None = None
        self._model.metadataRequested.connect(self._queue_requested_metadata)
        if self._status_model is not None:
            self._status_model.activePanelChanged.connect(self._sync_active_panel)
            self._status_model.printChanged.connect(self._queue_current_print_metadata)

    def start(self) -> None:
        if self._status_model is not None:
            self._sync_active_panel()
            return
        self.refresh_once()
        self._timer.start()

    def stop(self, timeout_ms: int = 5000) -> None:
        self._timer.stop()
        self._metadata_timer.stop()
        thread = self._file_refresh_thread
        if thread is None:
            return
        if thread.isRunning():
            thread.quit()
            thread.wait(timeout_ms)
        self._file_refresh_thread = None
        self._file_refresh_worker = None
        metadata_thread = self._metadata_refresh_thread
        if metadata_thread is not None and metadata_thread.isRunning():
            metadata_thread.quit()
            metadata_thread.wait(timeout_ms)
        self._metadata_refresh_thread = None
        self._metadata_refresh_worker = None

    @Slot()
    def refresh_once(self) -> None:
        if not self._is_active():
            return
        if self._file_refresh_worker is not None:
            return
        thread = QThread(self)
        self._file_refresh_worker = _FileListWorker(self._client)
        self._file_refresh_worker.moveToThread(thread)
        thread.started.connect(self._file_refresh_worker.run)
        self._file_refresh_worker.completed.connect(self._apply_files)
        self._file_refresh_worker.finished.connect(thread.quit)
        self._file_refresh_worker.finished.connect(self._file_refresh_worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_file_refresh_worker)
        self._file_refresh_thread = thread
        thread.start()

    @Slot(object)
    def _apply_files(self, value: object) -> None:
        if not self._is_active() or not isinstance(value, list):
            return
        files = [item for item in value if isinstance(item, dict)]
        self._model.set_files(files_from_moonraker(files))

    @Slot()
    def refresh_metadata_once(self) -> None:
        if not self._metadata_is_active() or not self._metadata_queue:
            return
        if self._metadata_refresh_worker is not None:
            return
        filename = self._metadata_queue.pop(0)
        thread = QThread(self)
        self._metadata_refresh_worker = _MetadataWorker(self._client, filename)
        self._metadata_refresh_worker.moveToThread(thread)
        thread.started.connect(self._metadata_refresh_worker.run)
        self._metadata_refresh_worker.completed.connect(self._apply_metadata)
        self._metadata_refresh_worker.finished.connect(thread.quit)
        self._metadata_refresh_worker.finished.connect(self._metadata_refresh_worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_metadata_refresh_worker)
        self._metadata_refresh_thread = thread
        thread.start()

    @Slot()
    def _sync_active_panel(self) -> None:
        self._queue_current_print_metadata()
        if self._is_active():
            self.refresh_once()
            if not self._timer.isActive():
                self._timer.start()
            if not self._metadata_timer.isActive():
                self._metadata_timer.start()
            return
        self._timer.stop()
        if self._metadata_is_active() and self._metadata_queue:
            if not self._metadata_timer.isActive():
                self._metadata_timer.start()
            return
        self._metadata_timer.stop()

    def _is_active(self) -> bool:
        if self._status_model is None:
            return True
        return self._status_model.active_panel_name == "print"

    def _metadata_is_active(self) -> bool:
        if self._status_model is None:
            return True
        return self._status_model.active_panel_name in {"print", "job_status"}

    def _queue_metadata(self, files: list[dict[str, object]]) -> None:
        for item in files:
            path = str(item.get("path", "")).strip()
            self._queue_metadata_path(path)

    @Slot(str)
    def _queue_requested_metadata(self, path: str) -> None:
        self._queue_metadata_path(path, front=True)
        if self._metadata_is_active() and not self._metadata_timer.isActive():
            self._metadata_timer.start()
        if self._metadata_is_active():
            self.refresh_metadata_once()

    def _queue_metadata_path(self, path: str, *, front: bool = False) -> None:
        clean = path.strip().strip("/")
        if not clean or clean in self._metadata_loaded or clean in self._metadata_queue:
            return
        if front:
            self._metadata_queue.insert(0, clean)
        else:
            self._metadata_queue.append(clean)

    @Slot()
    def _queue_current_print_metadata(self) -> None:
        if self._status_model is None:
            return
        path = str(self._status_model.printFilename or "").strip()
        self._queue_metadata_path(path, front=True)

    @Slot(str, object)
    def _apply_metadata(self, filename: str, value: object) -> None:
        if not isinstance(value, dict):
            return
        self._metadata_loaded.add(filename)
        self._model.setFileMetadata(filename, value, self._thumbnail_base_url())

    def _thumbnail_base_url(self) -> str:
        return f"{self._client.endpoint}/server/files/gcodes/"

    @Slot()
    def _clear_file_refresh_worker(self) -> None:
        self._file_refresh_thread = None
        self._file_refresh_worker = None
        self.refreshFinished.emit()

    @Slot()
    def _clear_metadata_refresh_worker(self) -> None:
        self._metadata_refresh_thread = None
        self._metadata_refresh_worker = None
        self.metadataRefreshFinished.emit()
