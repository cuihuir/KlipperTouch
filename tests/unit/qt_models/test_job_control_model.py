from klippertouch.moonraker.safety import UnsafeCommandError
from klippertouch.qt_models.job_control_model import JobControlModel


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def pause_print(self) -> dict[str, bool]:
        self.calls.append(("pause", ""))
        return {"ok": True}

    def start_print(self, filename: str) -> dict[str, bool]:
        self.calls.append(("start", filename))
        return {"ok": True}

    def resume_print(self) -> dict[str, bool]:
        self.calls.append(("resume", ""))
        return {"ok": True}

    def cancel_print(self) -> dict[str, bool]:
        self.calls.append(("cancel", ""))
        return {"ok": True}


class BlockingClient(FakeClient):
    def pause_print(self) -> dict[str, bool]:
        raise UnsafeCommandError("blocked")


def test_job_control_model_sends_pause_resume_cancel_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)
    statuses: list[str] = []
    model.statusChanged.connect(lambda: statuses.append(model.lastStatus))

    model.requestPause()
    model.requestResume()
    model.requestCancel()

    assert client.calls == [("pause", ""), ("resume", ""), ("cancel", "")]
    assert statuses == ["Pause sent", "Resume sent", "Cancel sent"]
    assert model.lastError == ""


def test_job_control_model_starts_selected_file(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestStartPrint("cube.gcode")

    assert client.calls == [("start", "cube.gcode")]
    assert model.lastStatus == "Print sent"


def test_job_control_model_reports_read_only_blocks(qtbot) -> None:
    model = JobControlModel(BlockingClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestPause()

    assert errors == ["blocked"]
    assert model.lastStatus == ""


def test_job_control_model_rejects_object_skip_until_gcode_control_exists(qtbot) -> None:
    model = JobControlModel(FakeClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestSkipObject("part_b")

    assert errors == ["Object exclusion control is not implemented yet"]


def test_job_control_model_rejects_delete_until_file_control_exists(qtbot) -> None:
    model = JobControlModel(FakeClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestDeleteFile("cube.gcode")

    assert errors == ["File delete control is not implemented yet"]
