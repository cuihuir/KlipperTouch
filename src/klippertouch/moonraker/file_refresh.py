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
        status_model: StatusModel | None = None,
    ) -> None:
        super().__init__()
        self._client = client
        self._model = model
        self._status_model = status_model
        self._timer = QTimer(self)
        self._timer.setInterval(refresh_interval_ms)
        self._timer.timeout.connect(self.refresh_once)
        if self._status_model is not None:
            self._status_model.activePanelChanged.connect(self._sync_active_panel)

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

    @Slot()
    def _sync_active_panel(self) -> None:
        if self._is_active():
            self.refresh_once()
            if not self._timer.isActive():
                self._timer.start()
            return
        self._timer.stop()

    def _is_active(self) -> bool:
        if self._status_model is None:
            return True
        return self._status_model.active_panel_name == "print"
