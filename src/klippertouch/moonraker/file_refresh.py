from PySide6.QtCore import QObject, QTimer, Slot

from klippertouch.domain.gcode_files import files_from_moonraker
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel


class GCodeFileRefresh(QObject):
    def __init__(
        self,
        client: MoonrakerClient,
        model: GCodeFileListModel,
        refresh_interval_ms: int = 10000,
    ) -> None:
        super().__init__()
        self._client = client
        self._model = model
        self._timer = QTimer(self)
        self._timer.setInterval(refresh_interval_ms)
        self._timer.timeout.connect(self.refresh_once)

    def start(self) -> None:
        self._timer.start()

    @Slot()
    def refresh_once(self) -> None:
        try:
            files = self._client.get_gcode_file_list()
        except Exception:
            return
        self._model.set_files(files_from_moonraker(files))
