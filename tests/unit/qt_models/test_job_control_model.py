from klippertouch.moonraker.safety import UnsafeCommandError
from klippertouch.qt_models.job_control_model import JobControlModel


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | float]] = []

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

    def adjust_z_offset(self, delta: float) -> dict[str, bool]:
        self.calls.append(("z_offset", delta))
        return {"ok": True}

    def set_speed_factor(self, percent: float) -> dict[str, bool]:
        self.calls.append(("speed", percent))
        return {"ok": True}

    def set_extrude_factor(self, percent: float) -> dict[str, bool]:
        self.calls.append(("extrude", percent))
        return {"ok": True}

    def exclude_object(self, object_name: str) -> dict[str, bool]:
        self.calls.append(("exclude", object_name))
        return {"ok": True}

    def delete_gcode_file(self, filename: str) -> dict[str, bool]:
        self.calls.append(("delete", filename))
        return {"ok": True}

    def clear_sdcard_file(self) -> dict[str, bool]:
        self.calls.append(("clear", ""))
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
    assert model.requestedPrintState == "cancelled"


def test_job_control_model_starts_selected_file(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestStartPrint("cube.gcode")

    assert client.calls == [("start", "cube.gcode")]
    assert model.lastStatus == "Print sent"
    assert model.requestedPrintState == "printing"


def test_job_control_model_reports_read_only_blocks(qtbot) -> None:
    model = JobControlModel(BlockingClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestPause()

    assert errors == ["blocked"]
    assert model.lastStatus == ""
    assert model.requestedPrintState == ""


def test_job_control_model_exposes_successful_requested_print_states(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)
    states: list[str] = []
    model.requestedPrintStateChanged.connect(lambda: states.append(model.requestedPrintState))

    model.requestPause()
    model.requestResume()
    model.requestCancel()

    assert states == ["paused", "printing", "cancelled"]


def test_job_control_model_sends_advanced_adjustments(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestZOffsetAdjust(0.05)
    model.requestSpeedFactor(95)
    model.requestExtrudeFactor(105)

    assert client.calls == [
        ("z_offset", 0.05),
        ("speed", 95.0),
        ("extrude", 105.0),
    ]
    assert model.lastStatus == "Flow sent"


def test_job_control_model_sends_object_skip(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestSkipObject("part_b")

    assert client.calls == [("exclude", "part_b")]
    assert model.lastStatus == "Object skip sent"


def test_job_control_model_rejects_empty_object_skip(qtbot) -> None:
    model = JobControlModel(FakeClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestSkipObject("")

    assert errors == ["Object name is required"]


def test_job_control_model_deletes_selected_file(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestDeleteFile("cube.gcode")

    assert client.calls == [("delete", "cube.gcode")]
    assert model.lastStatus == "Delete sent"


def test_job_control_model_rejects_empty_delete(qtbot) -> None:
    model = JobControlModel(FakeClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestDeleteFile("")

    assert errors == ["Filename is required"]


def test_job_control_model_clears_terminal_job_file(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestClearJob()

    assert client.calls == [("clear", "")]
    assert model.lastStatus == "Clear sent"
    assert model.requestedPrintState == "standby"
