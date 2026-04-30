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
    assert "QThread(self)" not in source
    assert "self._retired_threads: list[QThread]" in source
    assert "QTimer.singleShot(0, self._release_retired_threads)" in source
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
    assert 'setContextProperty("gcodeFileRefresh", file_refresh)' in source
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

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            return {}

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

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            return {}

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

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            return {}

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


def test_file_refresh_exposes_loading_and_file_list_errors(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.fail = True

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            if self.fail:
                raise RuntimeError("moonraker offline")
            return [{"path": "cube.gcode", "size": 2048, "permissions": "rw"}]

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            return {}

    client = FakeClient()
    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(client, model)

    assert refresh.loading is False
    assert refresh.lastError == ""

    refresh.refresh_once()
    assert refresh.loading is True
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass

    assert refresh.loading is False
    assert "moonraker offline" in refresh.lastError
    assert model.rowCount() == 0

    client.fail = False
    refresh.refresh_once()
    assert refresh.loading is True
    with qtbot.waitSignal(model.modelReset, timeout=1000):
        pass
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass

    assert refresh.loading is False
    assert refresh.lastError == ""
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


def test_file_refresh_loads_selected_file_metadata_after_list_refresh(qtbot) -> None:
    class FakeClient(MoonrakerClient):
        def __init__(self) -> None:
            super().__init__(PrinterConfig(name="p", moonraker_host="host"))
            self.metadata_calls: list[str] = []

        def get_gcode_file_list(self) -> list[dict[str, object]]:
            return [
                {"path": "selected.gcode", "size": 2048, "permissions": "rw"},
                {"path": "other.gcode", "size": 4096, "permissions": "rw"},
            ]

        def get_gcode_file_metadata(self, filename: str) -> dict[str, object]:
            self.metadata_calls.append(filename)
            return {"estimated_time": 600.0}

    client = FakeClient()
    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(client, model, metadata_interval_ms=1)

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        refresh.refresh_once()
    with qtbot.waitSignal(refresh.refreshFinished, timeout=1000):
        pass
    with qtbot.waitSignal(refresh.metadataRefreshFinished, timeout=1000):
        pass

    assert client.metadata_calls == ["other.gcode"]
    assert model.selectedPath == "other.gcode"
    assert model.fileEstimatedTimeLabelFor("other.gcode") == "10m"


def test_file_refresh_stop_cleans_metadata_thread_without_file_list_thread() -> None:
    class FakeThread:
        def __init__(self) -> None:
            self.quit_called = False
            self.wait_timeout_ms = -1

        def isRunning(self) -> bool:  # noqa: N802
            return True

        def quit(self) -> None:
            self.quit_called = True

        def wait(self, timeout_ms: int) -> None:
            self.wait_timeout_ms = timeout_ms

    model = GCodeFileListModel()
    refresh = GCodeFileRefresh(
        MoonrakerClient(PrinterConfig(name="p", moonraker_host="host")),
        model,
    )
    metadata_thread = FakeThread()
    refresh._metadata_refresh_thread = metadata_thread  # noqa: SLF001

    refresh.stop(timeout_ms=1234)

    assert metadata_thread.quit_called is True
    assert metadata_thread.wait_timeout_ms == 1234
    assert refresh._metadata_refresh_thread is None  # noqa: SLF001


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
