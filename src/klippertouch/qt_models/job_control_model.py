from collections.abc import Callable
from typing import Protocol

from PySide6.QtCore import Property, QObject, Signal, Slot


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


class JobControlModel(QObject):
    statusChanged = Signal()
    errorChanged = Signal()
    requestedPrintStateChanged = Signal()

    def __init__(self, client: JobControlClient | None = None) -> None:
        super().__init__()
        self._client = client
        self._last_status = ""
        self._last_error = ""
        self._requested_print_state = ""

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
        self._run_control("Print", lambda client: client.start_print(filename), "printing")

    @Slot(str)
    def requestDeleteFile(self, filename: str) -> None:  # noqa: N802
        clean_filename = filename.strip().strip("/")
        if not clean_filename:
            self._set_error("Filename is required")
            return
        self._run_control("Delete", lambda client: client.delete_gcode_file(clean_filename))

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

    def _run_control(
        self,
        label: str,
        command: Callable[[JobControlClient], dict[str, object]],
        requested_print_state: str = "",
    ) -> None:
        if self._client is None:
            self._set_error("Job control client is unavailable")
            return
        try:
            command(self._client)
        except Exception as exc:
            self._set_error(str(exc))
            return
        if requested_print_state:
            self._set_requested_print_state(requested_print_state)
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
        if value == self._requested_print_state:
            return
        self._requested_print_state = value
        self.requestedPrintStateChanged.emit()
