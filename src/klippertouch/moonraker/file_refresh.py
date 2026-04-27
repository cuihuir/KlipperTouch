from PySide6.QtCore import QObject, QTimer, Slot

from klippertouch.domain.gcode_files import files_from_moonraker
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.status_model import StatusModel


class GCodeFileRefresh(QObject):
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
        if self._status_model is not None:
            self._status_model.activePanelChanged.connect(self._sync_active_panel)
            self._status_model.printChanged.connect(self._queue_current_print_metadata)

    def start(self) -> None:
        if self._status_model is not None:
            self._sync_active_panel()
            return
        self.refresh_once()
        self._timer.start()

    @Slot()
    def refresh_once(self) -> None:
        if not self._is_active():
            return
        try:
            files = self._client.get_gcode_file_list()
        except Exception:
            return
        self._model.set_files(files_from_moonraker(files))
        self._queue_metadata(files)

    @Slot()
    def refresh_metadata_once(self) -> None:
        if not self._metadata_is_active() or not self._metadata_queue:
            return
        filename = self._metadata_queue.pop(0)
        try:
            metadata = self._client.get_gcode_file_metadata(filename)
        except Exception:
            return
        self._metadata_loaded.add(filename)
        self._model.setFileMetadata(filename, metadata, self._thumbnail_base_url())

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
        known = set(self._metadata_queue) | self._metadata_loaded
        for item in files:
            path = str(item.get("path", "")).strip()
            if not path or path in known:
                continue
            self._metadata_queue.append(path)
            known.add(path)

    @Slot()
    def _queue_current_print_metadata(self) -> None:
        if self._status_model is None:
            return
        path = str(self._status_model.printFilename or "").strip()
        if not path or path in self._metadata_loaded or path in self._metadata_queue:
            return
        self._metadata_queue.insert(0, path)

    def _thumbnail_base_url(self) -> str:
        return f"{self._client.endpoint}/server/files/gcodes/"
