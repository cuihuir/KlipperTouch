from PySide6.QtCore import Property, QObject, QThread, QTimer, Signal, Slot

from klippertouch.domain.gcode_files import files_from_moonraker
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.status_model import StatusModel


class _FileListWorker(QObject):
    completed = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, client: MoonrakerClient) -> None:
        super().__init__()
        self._client = client

    @Slot()
    def run(self) -> None:
        try:
            self.completed.emit(self._client.get_gcode_file_list())
        except Exception as exc:
            self.failed.emit(str(exc))
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
    loadingChanged = Signal()
    errorChanged = Signal()

    def __init__(
        self,
        client: MoonrakerClient,
        model: GCodeFileListModel,
        refresh_interval_ms: int = 10000,
        metadata_interval_ms: int = 150,
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
        self._metadata_file_identity: dict[str, tuple[float, int]] = {}
        self._metadata_inflight: set[str] = set()
        self._metadata_active_path = ""
        self._file_refresh_thread: QThread | None = None
        self._file_refresh_worker: _FileListWorker | None = None
        self._metadata_refresh_thread: QThread | None = None
        self._metadata_refresh_worker: _MetadataWorker | None = None
        self._retired_threads: list[QThread] = []
        self._retired_workers: list[QObject] = []
        self._loading = False
        self._last_error = ""
        self._model.metadataRequested.connect(self._queue_requested_metadata)
        self._model.selectedPathChanged.connect(self._queue_selected_metadata)
        if self._status_model is not None:
            self._status_model.activePanelChanged.connect(self._sync_active_panel)
            self._status_model.printChanged.connect(self._queue_current_print_metadata)

    def start(self) -> None:
        if self._status_model is not None:
            self._sync_active_panel()
            return
        self.refresh_once()
        self._timer.start()

    @Property(bool, notify=loadingChanged)
    def loading(self) -> bool:
        return self._loading

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:  # noqa: N802
        return self._last_error

    def stop(self, timeout_ms: int = 5000) -> None:
        self._timer.stop()
        self._metadata_timer.stop()
        file_thread = self._file_refresh_thread
        if file_thread is not None and file_thread.isRunning():
            file_thread.quit()
            file_thread.wait(timeout_ms)
        self._file_refresh_thread = None
        self._file_refresh_worker = None
        metadata_thread = self._metadata_refresh_thread
        if metadata_thread is not None and metadata_thread.isRunning():
            metadata_thread.quit()
            metadata_thread.wait(timeout_ms)
        self._metadata_refresh_thread = None
        self._metadata_refresh_worker = None
        self._metadata_queue.clear()
        self._metadata_inflight.clear()
        self._metadata_active_path = ""
        self._set_loading(False)
        self._release_retired_threads()

    @Slot()
    def refresh_once(self) -> None:
        if not self._is_active():
            return
        if self._file_refresh_worker is not None:
            return
        thread = QThread()
        self._set_loading(True)
        self._file_refresh_worker = _FileListWorker(self._client)
        self._file_refresh_worker.moveToThread(thread)
        thread.started.connect(self._file_refresh_worker.run)
        self._file_refresh_worker.completed.connect(self._apply_files)
        self._file_refresh_worker.failed.connect(self._apply_file_error)
        self._file_refresh_worker.finished.connect(thread.quit)
        self._file_refresh_worker.finished.connect(self._file_refresh_worker.deleteLater)
        thread.finished.connect(self._clear_file_refresh_worker)
        self._file_refresh_thread = thread
        thread.start()

    @Slot(object)
    def _apply_files(self, value: object) -> None:
        if not self._is_active() or not isinstance(value, list):
            return
        self._set_last_error("")
        files = [item for item in value if isinstance(item, dict)]
        self._sync_metadata_file_identity(files)
        self._model.set_files(files_from_moonraker(files))
        self._queue_selected_metadata()

    @Slot(str)
    def _apply_file_error(self, message: str) -> None:
        self._set_last_error(message or "Failed to load files")

    @Slot()
    def refresh_metadata_once(self) -> None:
        if not self._metadata_is_active() or not self._metadata_queue:
            return
        if self._metadata_refresh_worker is not None:
            return
        filename = self._metadata_queue.pop(0)
        self._metadata_active_path = filename
        self._metadata_inflight.add(filename)
        thread = QThread()
        self._metadata_refresh_worker = _MetadataWorker(self._client, filename)
        self._metadata_refresh_worker.moveToThread(thread)
        thread.started.connect(self._metadata_refresh_worker.run)
        self._metadata_refresh_worker.completed.connect(self._apply_metadata)
        self._metadata_refresh_worker.finished.connect(thread.quit)
        self._metadata_refresh_worker.finished.connect(self._metadata_refresh_worker.deleteLater)
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

    @Slot()
    def _queue_selected_metadata(self) -> None:
        path = str(self._model.selectedPath or "").strip()
        self._queue_metadata_path(path, front=True)
        if self._metadata_is_active() and not self._metadata_timer.isActive():
            self._metadata_timer.start()

    def _queue_metadata_path(self, path: str, *, front: bool = False) -> None:
        clean = path.strip().strip("/")
        if (
            not clean
            or clean in self._metadata_loaded
            or clean in self._metadata_inflight
            or clean in self._metadata_queue
        ):
            return
        if front:
            self._metadata_queue.insert(0, clean)
        else:
            self._metadata_queue.append(clean)

    def _sync_metadata_file_identity(self, files: list[dict[str, object]]) -> None:
        next_identity = {
            path: (_float_or_default(item.get("modified")), _int_or_default(item.get("size")))
            for item in files
            for path in (str(item.get("path", "")).strip().strip("/"),)
            if path
        }
        stale = {
            path
            for path in self._metadata_loaded
            if self._metadata_file_identity.get(path) != next_identity.get(path)
        }
        if stale:
            self._metadata_loaded.difference_update(stale)
        self._metadata_file_identity = next_identity

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
        self._retire_thread(self._file_refresh_thread, self._file_refresh_worker)
        self._file_refresh_thread = None
        self._file_refresh_worker = None
        self._set_loading(False)
        QTimer.singleShot(0, self._release_retired_threads)
        self.refreshFinished.emit()

    @Slot()
    def _clear_metadata_refresh_worker(self) -> None:
        self._retire_thread(self._metadata_refresh_thread, self._metadata_refresh_worker)
        self._metadata_refresh_thread = None
        self._metadata_refresh_worker = None
        if self._metadata_active_path:
            self._metadata_inflight.discard(self._metadata_active_path)
            self._metadata_active_path = ""
        QTimer.singleShot(0, self._release_retired_threads)
        self.metadataRefreshFinished.emit()

    def _retire_thread(self, thread: QThread | None, worker: QObject | None) -> None:
        if thread is not None:
            self._retired_threads.append(thread)
        if worker is not None:
            self._retired_workers.append(worker)

    @Slot()
    def _release_retired_threads(self) -> None:
        for thread in self._retired_threads:
            thread.deleteLater()
        self._retired_threads.clear()
        self._retired_workers.clear()

    def _set_loading(self, loading: bool) -> None:
        if self._loading == loading:
            return
        self._loading = loading
        self.loadingChanged.emit()

    def _set_last_error(self, message: str) -> None:
        if self._last_error == message:
            return
        self._last_error = message
        self.errorChanged.emit()


def _float_or_default(value: object) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, int | float | str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _int_or_default(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int | float | str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0
