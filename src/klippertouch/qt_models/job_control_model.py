from collections.abc import Callable
from typing import Protocol

from PySide6.QtCore import Property, QObject, Signal, Slot


class JobControlClient(Protocol):
    def start_print(self, filename: str) -> dict[str, object]: ...

    def pause_print(self) -> dict[str, object]: ...

    def resume_print(self) -> dict[str, object]: ...

    def cancel_print(self) -> dict[str, object]: ...


class JobControlModel(QObject):
    statusChanged = Signal()
    errorChanged = Signal()

    def __init__(self, client: JobControlClient | None = None) -> None:
        super().__init__()
        self._client = client
        self._last_status = ""
        self._last_error = ""

    @Property(str, notify=statusChanged)
    def lastStatus(self) -> str:  # noqa: N802
        return self._last_status

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:  # noqa: N802
        return self._last_error

    @Slot()
    def requestPause(self) -> None:  # noqa: N802
        self._run_control("Pause", lambda client: client.pause_print())

    @Slot()
    def requestResume(self) -> None:  # noqa: N802
        self._run_control("Resume", lambda client: client.resume_print())

    @Slot()
    def requestCancel(self) -> None:  # noqa: N802
        self._run_control("Cancel", lambda client: client.cancel_print())

    @Slot(str)
    def requestStartPrint(self, filename: str) -> None:  # noqa: N802
        self._run_control("Print", lambda client: client.start_print(filename))

    @Slot(str)
    def requestDeleteFile(self, _filename: str) -> None:  # noqa: N802
        self._set_error("File delete control is not implemented yet")

    @Slot(str)
    def requestSkipObject(self, _object_name: str) -> None:  # noqa: N802
        self._set_error("Object exclusion control is not implemented yet")

    def _run_control(
        self,
        label: str,
        command: Callable[[JobControlClient], dict[str, object]],
    ) -> None:
        if self._client is None:
            self._set_error("Job control client is unavailable")
            return
        try:
            command(self._client)
        except Exception as exc:
            self._set_error(str(exc))
            return
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
