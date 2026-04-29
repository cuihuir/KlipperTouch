import time
from pathlib import Path

from klippertouch.config.models import PrinterConfig
from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.file_refresh import GCodeFileRefresh
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.status_model import StatusModel


def test_file_refresh_updates_model_from_read_only_file_list() -> None:
    source = Path("src/klippertouch/moonraker/file_refresh.py").read_text(encoding="utf-8")

    assert "class GCodeFileRefresh" in source
    assert "QTimer" in source
    assert "QThread" in source
    assert "refresh_interval_ms: int = 10000" in source
    assert "self._timer.timeout.connect(self.refresh_once)" in source
    assert "self._file_refresh_worker = _FileListWorker" in source
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
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass

    assert model.rowCount() == 1


def test_file_refresh_start_schedules_refresh_without_blocking(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.calls = 0

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            self.calls += 1
            time.sleep(0.05)
            return [{"path": "cube.gcode", "size": 2048, "permissions": "rw"}]

    client = FakeClient()
    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(client, model)
    started = time.monotonic()

    refresh.start()
    assert time.monotonic() - started < 0.04
    with qtbot.waitSignal(model.modelReset, timeout=1000):
        pass
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass
    assert client.calls == 1
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
    status_model.set_status(PrinterStatus(print_filename="cube.gcode"))
    refresh = GCodeFileRefresh(client, model, status_model=status_model)

    refresh.start()

    assert client.calls == 0
    assert model.rowCount() == 0

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        status_model.setActivePanel("print")
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass

    assert client.calls == 1
    assert model.rowCount() == 1


def test_file_refresh_lazily_loads_requested_metadata_off_gui_thread(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.metadata_calls: list[str] = []

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            return [
                {"path": "a.gcode", "size": 2048, "permissions": "rw"},
                {"path": "b.gcode", "size": 4096, "permissions": "rw"},
            ]

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            time.sleep(0.05)
            self.metadata_calls.append(filename)
            return {
                "thumbnails": [
                    {
                        "size": 1200,
                        "relative_path": f".thumbs/{filename}.png",
                    }
                ]
            }

    client = FakeClient()
    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(client, model)

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        refresh.refresh_once()
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass

    assert client.metadata_calls == []

    started = time.monotonic()
    model.requestMetadata("a.gcode")
    assert time.monotonic() - started < 0.04
    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        pass
    with qtbot.waitSignal(refresh.metadataRefreshFinished, timeout=1000):
        pass

    assert client.metadata_calls == ["a.gcode"]

    model.requestMetadata("b.gcode")
    with qtbot.waitSignal(model.dataChanged, timeout=1000):
        pass
    with qtbot.waitSignal(refresh.metadataRefreshFinished, timeout=1000):
        pass

    assert client.metadata_calls == ["a.gcode", "b.gcode"]


def test_file_refresh_loads_metadata_while_print_or_job_status_is_active(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.metadata_calls = 0

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            return [{"path": "cube.gcode", "size": 2048, "permissions": "rw"}]

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            self.metadata_calls += 1
            return {"thumbnails": [{"size": 1200, "relative_path": ".thumbs/cube.png"}]}

    client = FakeClient()
    model = GCodeFileListModel()
    status_model = StatusModel()
    status_model.set_status(PrinterStatus(print_filename="cube.gcode"))
    refresh = GCodeFileRefresh(client, model, status_model=status_model)

    refresh.start()
    refresh.refresh_metadata_once()

    assert client.metadata_calls == 0

    status_model.setActivePanel("job_status")
    with qtbot.waitSignal(refresh.metadataRefreshFinished, timeout=1000):
        refresh.refresh_metadata_once()

    assert client.metadata_calls == 1

    status_model.setActivePanel("main")
    refresh.refresh_metadata_once()

    assert client.metadata_calls == 1
