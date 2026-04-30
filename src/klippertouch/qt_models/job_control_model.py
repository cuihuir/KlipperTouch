from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Protocol

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot


class JobControlClient(Protocol):
    def start_print(self, filename: str) -> dict[str, object]: ...

    def pause_print(self) -> dict[str, object]: ...

    def resume_print(self) -> dict[str, object]: ...

    def cancel_print(self) -> dict[str, object]: ...

    def adjust_z_offset(self, delta: float) -> dict[str, object]: ...

    def set_speed_factor(self, percent: float) -> dict[str, object]: ...

    def set_extrude_factor(self, percent: float) -> dict[str, object]: ...

    def exclude_object(self, object_name: str) -> dict[str, object]: ...

    def delete_gcode_file(self, filename: str) -> dict[str, object]: ...

    def clear_sdcard_file(self) -> dict[str, object]: ...

    def firmware_restart(self) -> dict[str, object]: ...

    def restart_klipper(self) -> dict[str, object]: ...

    def emergency_stop(self) -> dict[str, object]: ...

    def disable_motors(self) -> dict[str, object]: ...

    def jog_toolhead(self, axis: str, distance: float, speed: float) -> dict[str, object]: ...

    def home_axes(self, *axes: str) -> dict[str, object]: ...

    def run_z_tilt_adjust(self) -> dict[str, object]: ...

    def run_accelerator_level(self) -> dict[str, object]: ...

    def run_uvw_home(self) -> dict[str, object]: ...

    def extrude_filament(self, distance: float, speed: float) -> dict[str, object]: ...

    def load_filament(self, speed: float) -> dict[str, object]: ...

    def unload_filament(self, speed: float) -> dict[str, object]: ...

    def set_temperature_target(self, device_name: str, target: float) -> dict[str, object]: ...

    def set_pressure_advance(self, advance: float, smooth_time: float) -> dict[str, object]: ...


@dataclass
class _PendingJobCommand:
    label: str
    command: Callable[[], dict[str, object]]
    requested_print_state: str
    on_success: Callable[[], None] | None


class JobControlModel(QObject):
    statusChanged = Signal()
    errorChanged = Signal()
    requestedPrintStateChanged = Signal()
    fileDeleted = Signal(str)

    def __init__(
        self,
        client: JobControlClient | None = None,
        extrusion_status_provider: Callable[[], tuple[str, str, bool]] | None = None,
    ) -> None:
        super().__init__()
        self._client = client
        self._extrusion_status_provider = extrusion_status_provider
        self._last_status = ""
        self._last_error = ""
        self._requested_print_state = ""
        self._command_queue: list[_PendingJobCommand] = []
        self._active_command: _PendingJobCommand | None = None
        self._command_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="KTouchJob")
        self._command_future: Future[tuple[bool, str]] | None = None
        self._command_poll_timer = QTimer(self)
        self._command_poll_timer.setInterval(10)
        self._command_poll_timer.timeout.connect(self._poll_command_future)

    @Property(str, notify=statusChanged)
    def lastStatus(self) -> str:  # noqa: N802
        return self._last_status

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:  # noqa: N802
        return self._last_error

    @Property(str, notify=requestedPrintStateChanged)
    def requestedPrintState(self) -> str:  # noqa: N802
        return self._requested_print_state

    @Slot()
    def requestPause(self) -> None:  # noqa: N802
        self._run_control("Pause", lambda client: client.pause_print(), "paused")

    @Slot()
    def requestResume(self) -> None:  # noqa: N802
        self._run_control("Resume", lambda client: client.resume_print(), "printing")

    @Slot()
    def requestCancel(self) -> None:  # noqa: N802
        self._run_control("Cancel", lambda client: client.cancel_print(), "cancelled")

    @Slot(str)
    def requestStartPrint(self, filename: str) -> None:  # noqa: N802
        clean_filename = _normalize_gcode_filename(filename)
        if not clean_filename:
            self._set_error("Filename is required")
            return
        self._run_control("Print", lambda client: client.start_print(clean_filename), "printing")

    @Slot()
    def requestClearJob(self) -> None:  # noqa: N802
        self._run_control("Clear", lambda client: client.clear_sdcard_file(), "standby")

    @Slot()
    def requestFirmwareRestart(self) -> None:  # noqa: N802
        self._run_control("Firmware restart", lambda client: client.firmware_restart())

    @Slot()
    def requestKlipperRestart(self) -> None:  # noqa: N802
        self._run_control("Restart Klipper", lambda client: client.restart_klipper())

    @Slot()
    def requestEmergencyStop(self) -> None:  # noqa: N802
        self._run_control("Emergency Stop", lambda client: client.emergency_stop())

    @Slot()
    def requestDisableMotors(self) -> None:  # noqa: N802
        self._run_control("Disable motors", lambda client: client.disable_motors())

    @Slot(str, float, float)
    def requestMoveJog(self, direction: str, distance: float, speed: float) -> None:  # noqa: N802
        clean_direction = direction.strip().lower()
        if distance <= 0:
            self._set_error("Move distance must be positive")
            return
        if speed <= 0:
            self._set_error("Move speed must be positive")
            return
        move_distance = float(distance)
        move_speed = float(speed)
        direction_map = {
            "x_minus": ("x", -move_distance),
            "x_plus": ("x", move_distance),
            "y_minus": ("y", -move_distance),
            "y_plus": ("y", move_distance),
            "z_minus": ("z", -move_distance),
            "z_plus": ("z", move_distance),
            "u_minus": ("u", -move_distance),
            "u_plus": ("u", move_distance),
            "v_minus": ("v", -move_distance),
            "v_plus": ("v", move_distance),
            "w_minus": ("w", -move_distance),
            "w_plus": ("w", move_distance),
        }
        if clean_direction not in direction_map:
            self._set_error("Invalid move direction")
            return
        axis, signed_distance = direction_map[clean_direction]
        direction_label = f"{axis.upper()}{'+' if signed_distance > 0 else '-'}"
        self._run_control(
            f"Move {direction_label}",
            lambda client: client.jog_toolhead(axis, signed_distance, move_speed),
        )

    @Slot(str)
    def requestHome(self, target: str) -> None:  # noqa: N802
        clean_target = target.strip().lower()
        target_map = {
            "all": (),
            "xy": ("x", "y"),
            "z": ("z",),
        }
        if clean_target == "uvw":
            self._run_control("UVW home", lambda client: client.run_uvw_home())
            return
        if clean_target not in target_map:
            self._set_error("Invalid home target")
            return
        self._run_control("Home", lambda client: client.home_axes(*target_map[clean_target]))

    @Slot()
    def requestZTiltAdjust(self) -> None:  # noqa: N802
        self._run_control("Z tilt adjust", lambda client: client.run_z_tilt_adjust())

    @Slot()
    def requestAcceleratorLevel(self) -> None:  # noqa: N802
        self._run_control("Accelerator level", lambda client: client.run_accelerator_level())

    @Slot(str, float, float)
    def requestExtrudeFilament(self, action: str, distance: float, speed: float) -> None:  # noqa: N802
        guard_error = self._extrusion_guard_error()
        if guard_error:
            self._set_error(guard_error)
            return
        clean_action = action.strip().lower()
        if distance <= 0:
            self._set_error("Extrusion distance must be positive")
            return
        if speed <= 0:
            self._set_error("Extrusion speed must be positive")
            return
        action_map = {
            "extrude": ("Extrude", float(distance)),
            "retract": ("Retract", -float(distance)),
        }
        if clean_action not in action_map:
            self._set_error("Invalid extrusion action")
            return
        label, signed_distance = action_map[clean_action]
        self._run_control(
            label,
            lambda client: client.extrude_filament(signed_distance, float(speed)),
        )

    @Slot(float)
    def requestLoadFilament(self, speed: float) -> None:  # noqa: N802
        self._run_filament_macro("Load filament", speed, lambda client: client.load_filament)

    @Slot(float)
    def requestUnloadFilament(self, speed: float) -> None:  # noqa: N802
        self._run_filament_macro("Unload filament", speed, lambda client: client.unload_filament)

    @Slot(str, float)
    def requestTemperatureTarget(self, device_name: str, target: float) -> None:  # noqa: N802
        clean_name = device_name.strip()
        if not clean_name:
            self._set_error("Temperature device is required")
            return
        if target < 0 or target > 350:
            self._set_error("Temperature target must be between 0 and 350")
            return
        self._run_control(
            "Temperature target",
            lambda client: client.set_temperature_target(clean_name, float(target)),
        )

    @Slot(float, float)
    def requestPressureAdvance(self, advance: float, smooth_time: float) -> None:  # noqa: N802
        if advance < 0 or advance > 5:
            self._set_error("Pressure advance must be between 0 and 5")
            return
        if smooth_time < 0 or smooth_time > 1:
            self._set_error("Smooth time must be between 0 and 1")
            return
        self._run_control(
            "Pressure advance",
            lambda client: client.set_pressure_advance(float(advance), float(smooth_time)),
        )

    @Slot(str)
    def requestPlaceholderControl(self, label: str) -> None:  # noqa: N802
        clean_label = label.strip() or "Action"
        self._set_status(f"{clean_label} is not implemented yet")

    @Slot(str)
    def requestDeleteFile(self, filename: str) -> None:  # noqa: N802
        clean_filename = _normalize_gcode_filename(filename)
        if not clean_filename:
            self._set_error("Filename is required")
            return
        self._run_control(
            "Delete",
            lambda client: client.delete_gcode_file(clean_filename),
            on_success=lambda: self.fileDeleted.emit(clean_filename),
        )

    @Slot(str)
    def requestSkipObject(self, object_name: str) -> None:  # noqa: N802
        clean_name = object_name.strip()
        if not clean_name:
            self._set_error("Object name is required")
            return
        self._run_control("Object skip", lambda client: client.exclude_object(clean_name))

    @Slot(float)
    def requestZOffsetAdjust(self, delta: float) -> None:  # noqa: N802
        self._run_control("Z offset", lambda client: client.adjust_z_offset(delta))

    @Slot(float)
    def requestSpeedFactor(self, percent: float) -> None:  # noqa: N802
        self._run_control("Speed", lambda client: client.set_speed_factor(percent))

    @Slot(float)
    def requestExtrudeFactor(self, percent: float) -> None:  # noqa: N802
        self._run_control("Flow", lambda client: client.set_extrude_factor(percent))

    def _run_filament_macro(
        self,
        label: str,
        speed: float,
        command: Callable[[JobControlClient], Callable[[float], dict[str, object]]],
    ) -> None:
        guard_error = self._extrusion_guard_error()
        if guard_error:
            self._set_error(guard_error)
            return
        if speed <= 0:
            self._set_error("Filament speed must be positive")
            return
        self._run_control(label, lambda client: command(client)(float(speed)))

    def _extrusion_guard_error(self) -> str:
        if self._extrusion_status_provider is None:
            return ""
        klippy_state, webhooks_state, extruder_can_extrude = self._extrusion_status_provider()
        klippy_state = klippy_state.strip().lower()
        webhooks_state = webhooks_state.strip().lower()
        if klippy_state != "ready" or webhooks_state != "ready":
            return "Printer not ready"
        if not extruder_can_extrude:
            return "Heat nozzle first"
        return ""

    def _run_control(
        self,
        label: str,
        command: Callable[[JobControlClient], dict[str, object]],
        requested_print_state: str = "",
        on_success: Callable[[], None] | None = None,
    ) -> None:
        if self._client is None:
            self._set_error("Job control client is unavailable")
            return
        client = self._client
        self._command_queue.append(
            _PendingJobCommand(
                label=label,
                command=lambda: command(client),
                requested_print_state=requested_print_state,
                on_success=on_success,
            )
        )
        self._start_next_control()

    def _start_next_control(self) -> None:
        if self._command_future is not None or not self._command_queue:
            return
        pending = self._command_queue.pop(0)
        self._active_command = pending
        self._command_future = self._command_executor.submit(_execute_job_command, pending.command)
        self._command_poll_timer.start()

    def stop(self, timeout_ms: int = 5000) -> None:
        self._command_queue.clear()
        self._command_poll_timer.stop()
        future = self._command_future
        if future is not None and not future.done():
            future.cancel()
        self._command_future = None
        self._active_command = None
        self._command_executor.shutdown(wait=False, cancel_futures=True)

    def _handle_control_success(
        self,
        label: str,
        requested_print_state: str,
        on_success: Callable[[], None] | None,
    ) -> None:
        if requested_print_state:
            self._set_requested_print_state(requested_print_state)
        if on_success is not None:
            on_success()
        self._set_status(f"{label} sent")

    def _set_status(self, value: str) -> None:
        self._last_status = value
        self._last_error = ""
        self.statusChanged.emit()
        self.errorChanged.emit()

    def _set_error(self, value: str) -> None:
        self._last_error = value
        self._last_status = ""
        self.errorChanged.emit()
        self.statusChanged.emit()

    def _set_requested_print_state(self, value: str) -> None:
        self._requested_print_state = value
        self.requestedPrintStateChanged.emit()

    @Slot()
    def _poll_command_future(self) -> None:
        future = self._command_future
        pending = self._active_command
        if future is None or pending is None or not future.done():
            return
        self._command_poll_timer.stop()
        self._command_future = None
        self._active_command = None
        ok, error = future.result()
        if ok:
            self._handle_control_success(
                pending.label,
                pending.requested_print_state,
                pending.on_success,
            )
        else:
            self._set_error(error)
        self._start_next_control()


def _normalize_gcode_filename(filename: str) -> str:
    clean_filename = filename.strip().replace("\\", "/")
    marker = "/gcodes/"
    if marker in clean_filename:
        clean_filename = clean_filename.rsplit(marker, 1)[1]
    return clean_filename.strip("/")


def _execute_job_command(command: Callable[[], dict[str, object]]) -> tuple[bool, str]:
    try:
        command()
    except Exception as exc:
        return False, str(exc)
    return True, ""
