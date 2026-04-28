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

    def firmware_restart(self) -> dict[str, bool]:
        self.calls.append(("firmware_restart", ""))
        return {"ok": True}

    def restart_klipper(self) -> dict[str, bool]:
        self.calls.append(("restart_klipper", ""))
        return {"ok": True}

    def emergency_stop(self) -> dict[str, bool]:
        self.calls.append(("emergency_stop", ""))
        return {"ok": True}

    def disable_motors(self) -> dict[str, bool]:
        self.calls.append(("disable_motors", ""))
        return {"ok": True}

    def jog_toolhead(self, axis: str, distance: float) -> dict[str, bool]:
        self.calls.append(("jog", f"{axis}:{distance}"))
        return {"ok": True}

    def home_axes(self, *axes: str) -> dict[str, bool]:
        self.calls.append(("home", ",".join(axes)))
        return {"ok": True}

    def extrude_filament(self, distance: float, speed: float) -> dict[str, bool]:
        self.calls.append(("extrude_filament", f"{distance}:{speed}"))
        return {"ok": True}

    def load_filament(self, speed: float) -> dict[str, bool]:
        self.calls.append(("load_filament", speed))
        return {"ok": True}

    def unload_filament(self, speed: float) -> dict[str, bool]:
        self.calls.append(("unload_filament", speed))
        return {"ok": True}

    def set_temperature_target(self, device_name: str, target: float) -> dict[str, bool]:
        self.calls.append(("temperature_target", f"{device_name}:{target}"))
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


def test_job_control_model_normalizes_absolute_gcodes_path_before_start(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestStartPrint("/home/tope/printer_data/gcodes/folder/cube.gcode")

    assert client.calls == [("start", "folder/cube.gcode")]


def test_job_control_model_rejects_empty_start_filename(qtbot) -> None:
    model = JobControlModel(FakeClient())
    errors: list[str] = []
    model.errorChanged.connect(lambda: errors.append(model.lastError))

    model.requestStartPrint("   ")

    assert errors == ["Filename is required"]


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


def test_job_control_model_sends_recovery_restart_commands(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestFirmwareRestart()
    model.requestKlipperRestart()

    assert client.calls == [("firmware_restart", ""), ("restart_klipper", "")]
    assert model.lastStatus == "Restart Klipper sent"


def test_job_control_model_sends_emergency_stop(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestEmergencyStop()

    assert client.calls == [("emergency_stop", "")]
    assert model.lastStatus == "Emergency Stop sent"


def test_job_control_model_sends_disable_motors(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestDisableMotors()

    assert client.calls == [("disable_motors", "")]
    assert model.lastStatus == "Disable motors sent"


def test_job_control_model_sends_validated_jog_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestMoveJog("x_minus", 10)
    model.requestMoveJog("z_plus", 0.5)

    assert client.calls == [("jog", "x:-10.0"), ("jog", "z:0.5")]
    assert model.lastStatus == "Move sent"


def test_job_control_model_rejects_invalid_jog_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestMoveJog("bad", 10)
    assert client.calls == []
    assert model.lastError == "Invalid move direction"

    model.requestMoveJog("x_plus", 0)
    assert client.calls == []
    assert model.lastError == "Move distance must be positive"


def test_job_control_model_sends_home_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestHome("xy")
    model.requestHome("z")
    model.requestHome("all")

    assert client.calls == [("home", "x,y"), ("home", "z"), ("home", "")]
    assert model.lastStatus == "Home sent"


def test_job_control_model_rejects_invalid_home_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestHome("bad")

    assert client.calls == []
    assert model.lastError == "Invalid home target"


def test_job_control_model_sends_validated_extrude_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestExtrudeFilament("extrude", 10, 5)
    model.requestExtrudeFilament("retract", 5, 2)

    assert client.calls == [
        ("extrude_filament", "10.0:5.0"),
        ("extrude_filament", "-5.0:2.0"),
    ]
    assert model.lastStatus == "Retract sent"


def test_job_control_model_rejects_invalid_extrude_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestExtrudeFilament("bad", 10, 5)
    assert client.calls == []
    assert model.lastError == "Invalid extrusion action"

    model.requestExtrudeFilament("extrude", 0, 5)
    assert client.calls == []
    assert model.lastError == "Extrusion distance must be positive"

    model.requestExtrudeFilament("extrude", 5, 0)
    assert client.calls == []
    assert model.lastError == "Extrusion speed must be positive"


def test_job_control_model_sends_load_unload_macro_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestLoadFilament(5)
    model.requestUnloadFilament(2)

    assert client.calls == [("load_filament", 5.0), ("unload_filament", 2.0)]
    assert model.lastStatus == "Unload filament sent"


def test_job_control_model_rejects_invalid_load_unload_speed(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestLoadFilament(0)
    assert client.calls == []
    assert model.lastError == "Filament speed must be positive"

    model.requestUnloadFilament(-1)
    assert client.calls == []
    assert model.lastError == "Filament speed must be positive"


def test_job_control_model_sends_temperature_target_requests(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestTemperatureTarget("extruder", 0)
    model.requestTemperatureTarget("heater_bed", 60)

    assert client.calls == [
        ("temperature_target", "extruder:0.0"),
        ("temperature_target", "heater_bed:60.0"),
    ]
    assert model.lastStatus == "Temperature target sent"


def test_job_control_model_rejects_invalid_temperature_targets(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestTemperatureTarget("", 0)
    assert client.calls == []
    assert model.lastError == "Temperature device is required"

    model.requestTemperatureTarget("extruder", -1)
    assert client.calls == []
    assert model.lastError == "Temperature target must be between 0 and 350"

    model.requestTemperatureTarget("extruder", 351)
    assert client.calls == []
    assert model.lastError == "Temperature target must be between 0 and 350"


def test_job_control_model_reports_placeholder_recovery_actions(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)

    model.requestPlaceholderControl("Restart Moonraker")

    assert client.calls == []
    assert model.lastStatus == "Restart Moonraker is not implemented yet"


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
    deleted: list[str] = []
    model.fileDeleted.connect(lambda path: deleted.append(path))

    model.requestDeleteFile("cube.gcode")

    assert client.calls == [("delete", "cube.gcode")]
    assert deleted == ["cube.gcode"]
    assert model.lastStatus == "Delete sent"


def test_job_control_model_normalizes_absolute_gcodes_path_before_delete(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)
    deleted: list[str] = []
    model.fileDeleted.connect(lambda path: deleted.append(path))

    model.requestDeleteFile("/home/tope/printer_data/gcodes/folder/cube.gcode")

    assert client.calls == [("delete", "folder/cube.gcode")]
    assert deleted == ["folder/cube.gcode"]


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


def test_job_control_model_emits_duplicate_requested_state_for_repeated_controls(qtbot) -> None:
    client = FakeClient()
    model = JobControlModel(client)
    states: list[str] = []
    model.requestedPrintStateChanged.connect(lambda: states.append(model.requestedPrintState))

    model.requestClearJob()
    model.requestClearJob()

    assert states == ["standby", "standby"]
