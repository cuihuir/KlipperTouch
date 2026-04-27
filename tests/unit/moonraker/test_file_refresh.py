from pathlib import Path

from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.file_refresh import GCodeFileRefresh
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.status_model import StatusModel


def test_file_refresh_updates_model_from_read_only_file_list() -> None:
    source = Path("src/klippertouch/moonraker/file_refresh.py").read_text(encoding="utf-8")

    assert "class GCodeFileRefresh" in source
    assert "QTimer" in source
    assert "refresh_interval_ms: int = 10000" in source
    assert "self._timer.timeout.connect(self.refresh_once)" in source
    assert "self._client.get_gcode_file_list()" in source
    assert "self._model.set_files(files_from_moonraker(files))" in source
    assert "printer.gcode.script" not in source
    assert "printer.print.start" not in source


def test_app_wires_optional_read_only_file_refresh() -> None:
    source = Path("src/klippertouch/app.py").read_text(encoding="utf-8")

    assert "GCodeFileRefresh" in source
    assert "file_refresh_client" in source
    assert "file_refresh.start()" in source
    assert "engine.gcode_file_refresh = file_refresh" in source


def test_file_refresh_updates_model_and_keeps_existing_files_on_failure(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.fail = False

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            if self.fail:
                raise RuntimeError("offline")
            return [{"path": "cube.gcode", "size": 2048, "permissions": "rw"}]

    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(FakeClient(), model)

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        refresh.refresh_once()

    assert model.rowCount() == 1


def test_file_refresh_start_refreshes_immediately(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            return [{"path": "cube.gcode", "size": 2048, "permissions": "rw"}]

    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(FakeClient(), model)

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        refresh.start()

    assert model.rowCount() == 1


def test_file_refresh_only_runs_while_files_panel_is_active(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.calls = 0

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            self.calls += 1
            return [{"path": "cube.gcode", "size": 2048, "permissions": "rw"}]

    client = FakeClient()
    model = GCodeFileListModel()
    status_model = StatusModel()
    refresh = GCodeFileRefresh(client, model, status_model=status_model)

    refresh.start()

    assert client.calls == 0
    assert model.rowCount() == 0

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        status_model.setActivePanel("print")

    assert client.calls == 1
    assert model.rowCount() == 1

    status_model.setActivePanel("main")
    refresh.refresh_once()

    assert client.calls == 1

    refresh._client.fail = True
    refresh.refresh_once()

    assert model.rowCount() == 1
