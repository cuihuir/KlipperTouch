from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QSettings,
    Qt,
    Signal,
    Slot,
)

from klippertouch.domain.printer import PrinterStatus, TemperatureDeviceStatus

EMPTY_INDEX = QModelIndex()


class TemperatureDeviceListModel(QAbstractListModel):
    historyChanged = Signal()
    graphSelectionChanged = Signal()
    graphSeriesChanged = Signal()

    NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    DISPLAY_NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 2
    ICON_ROLE = int(Qt.ItemDataRole.UserRole) + 3
    TEMPERATURE_ROLE = int(Qt.ItemDataRole.UserRole) + 4
    TARGET_ROLE = int(Qt.ItemDataRole.UserRole) + 5
    GRAPH_VISIBLE_ROLE = int(Qt.ItemDataRole.UserRole) + 6

    def __init__(self, settings: QSettings | None = None) -> None:
        super().__init__()
        self._devices: tuple[TemperatureDeviceStatus, ...] = ()
        self._history: dict[str, list[float]] = {}
        self._graph_visible: dict[str, bool] = {}
        self._history_limit = 60
        self._settings = (
            settings if settings is not None else QSettings("KlipperTouch", "KlipperTouch")
        )
        self._settings_scope: str | None = None

    def set_status(self, status: PrinterStatus) -> None:
        scope = _graph_scope_for_status(status)
        if scope != self._settings_scope:
            self._settings_scope = scope
            self._graph_visible = self._load_graph_visibility()
        self.beginResetModel()
        self._devices = status.temperature_devices
        self.endResetModel()
        history_changed = False
        for device in self._devices:
            self._ensure_graph_visibility_default(device.name)
            values = self._history.setdefault(device.name, [])
            if device.temperature is None:
                continue
            values.append(float(device.temperature))
            del values[:-self._history_limit]
            history_changed = True
        if history_changed:
            self.historyChanged.emit()
            self.graphSeriesChanged.emit()

    @Property(list, notify=historyChanged)
    def extruderSeries(self) -> list[float]:
        return list(self._first_series_for_name("extruder"))

    @Property(list, notify=historyChanged)
    def bedSeries(self) -> list[float]:
        return list(self._history.get("heater_bed", []))

    @Property(list, notify=graphSeriesChanged)
    def graphSeriesModel(self) -> list[dict[str, object]]:
        series: list[dict[str, object]] = []
        for index, device in enumerate(self._devices):
            if not self._graph_visible.get(device.name, True):
                continue
            points = self._history.get(device.name, [])
            if not points:
                continue
            series.append(
                {
                    "name": device.name,
                    "displayName": device.display_name,
                    "icon": device.icon,
                    "color": _graph_color_for_device(device.name, index),
                    "series": list(points),
                }
            )
        return series

    def initialize_history(self, temperature_store: dict[str, object]) -> None:
        history: dict[str, list[float]] = {}
        max_length = 0
        for name, values in temperature_store.items():
            if not isinstance(name, str) or not isinstance(values, dict):
                continue
            temperatures = values.get("temperatures")
            if not isinstance(temperatures, list):
                continue
            normalized = [float(value) for value in temperatures if isinstance(value, (int, float))]
            if not normalized:
                continue
            history[name] = normalized
            max_length = max(max_length, len(normalized))

        if history:
            self._history.update(history)
            self._history_limit = max(self._history_limit, max_length)
            self.historyChanged.emit()
            self.graphSelectionChanged.emit()
            self.graphSeriesChanged.emit()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = EMPTY_INDEX,
    ) -> int:
        if parent is not None and parent.isValid():
            return 0
        return len(self._devices)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object:
        if not index.isValid() or not 0 <= index.row() < len(self._devices):
            return None

        device = self._devices[index.row()]
        if role == self.NAME_ROLE:
            return device.name
        if role == self.DISPLAY_NAME_ROLE:
            return device.display_name
        if role == self.ICON_ROLE:
            return device.icon
        if role == self.TEMPERATURE_ROLE:
            return device.temperature
        if role == self.TARGET_ROLE:
            return device.target
        if role == self.GRAPH_VISIBLE_ROLE:
            return self._graph_visible.get(device.name, True)
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.NAME_ROLE: QByteArray(b"name"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.ICON_ROLE: QByteArray(b"icon"),
            self.TEMPERATURE_ROLE: QByteArray(b"temperature"),
            self.TARGET_ROLE: QByteArray(b"target"),
            self.GRAPH_VISIBLE_ROLE: QByteArray(b"graphVisible"),
        }

    @Slot(str)
    def toggleGraphDevice(self, name: str) -> None:
        row = next((index for index, device in enumerate(self._devices) if device.name == name), -1)
        if row < 0:
            return
        self._graph_visible[name] = not self._graph_visible.get(name, True)
        self._persist_graph_visibility(name)
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [self.GRAPH_VISIBLE_ROLE])
        self.graphSelectionChanged.emit()
        self.graphSeriesChanged.emit()

    def _first_series_for_name(self, prefix: str) -> list[float]:
        for device in self._devices:
            if device.name == prefix:
                return self._history.get(device.name, [])
        for device in self._devices:
            if device.name.startswith(prefix):
                return self._history.get(device.name, [])
        return []

    def _ensure_graph_visibility_default(self, name: str) -> None:
        if name in self._graph_visible:
            return
        self._graph_visible[name] = True
        self._persist_graph_visibility(name)

    def _load_graph_visibility(self) -> dict[str, bool]:
        if self._settings_scope is None:
            return {}
        self._settings.beginGroup(f"temperature_graph/{self._settings_scope}")
        values: dict[str, bool] = {}
        for key in self._settings.childKeys():
            values[key] = bool(self._settings.value(key, True, type=bool))
        self._settings.endGroup()
        return values

    def _persist_graph_visibility(self, name: str) -> None:
        if self._settings_scope is None:
            return
        self._settings.beginGroup(f"temperature_graph/{self._settings_scope}")
        self._settings.setValue(name, self._graph_visible.get(name, True))
        self._settings.endGroup()
        self._settings.sync()


def _graph_color_for_device(name: str, index: int) -> str:
    if name == "extruder" or name.startswith("extruder"):
        return "#ed3c63"
    if name == "heater_bed":
        return "#d46900"
    palette = ("#007db4", "#849900", "#7f5af0", "#26a69a", "#f4b400", "#ef6c00")
    return palette[index % len(palette)]


def _graph_scope_for_status(status: PrinterStatus) -> str | None:
    hostname = status.hostname.strip()
    if not hostname or hostname == "unknown":
        return None
    return hostname


class StatusModel(QObject):
    statusChanged = Signal()

    def __init__(
        self,
        temperature_device_model: TemperatureDeviceListModel | None = None,
    ) -> None:
        super().__init__()
        self._status = PrinterStatus()
        self._temperature_device_model = temperature_device_model

    def set_status(self, status: PrinterStatus) -> None:
        self._status = status
        if self._temperature_device_model is not None:
            self._temperature_device_model.set_status(status)
        self.statusChanged.emit()

    @Property(str, notify=statusChanged)
    def hostname(self) -> str:
        return self._status.hostname

    @Property(str, notify=statusChanged)
    def klippyState(self) -> str:
        return self._status.klippy_state

    @Property(str, notify=statusChanged)
    def klipperVersion(self) -> str:
        return self._status.klipper_version

    @Property(str, notify=statusChanged)
    def moonrakerVersion(self) -> str:
        return self._status.moonraker_version

    @Property(int, notify=statusChanged)
    def mcuCount(self) -> int:
        return self._status.mcu_count

    @Property(list, notify=statusChanged)
    def mcuInfos(self) -> list[dict[str, str]]:
        return [
            {
                "name": item.name,
                "version": item.version,
                "build_versions": item.build_versions,
            }
            for item in self._status.mcu_statuses
        ]

    @Property(int, notify=statusChanged)
    def serviceVersionCount(self) -> int:
        return self._status.service_version_count

    @Property(list, notify=statusChanged)
    def serviceVersions(self) -> list[dict[str, str]]:
        return [
            {
                "name": item.name,
                "version": item.version,
                "configured_type": item.configured_type,
            }
            for item in self._status.service_versions
        ]

    @Property(int, notify=statusChanged)
    def objectCount(self) -> int:
        return self._status.object_count

    @Property(list, notify=statusChanged)
    def objectNames(self) -> list[str]:
        return list(self._status.objects)

    @Property(int, notify=statusChanged)
    def temperatureDeviceCount(self) -> int:
        return self._status.temperature_device_count

    @Property(str, notify=statusChanged)
    def printState(self) -> str:
        return self._status.print_state

    @Property(str, notify=statusChanged)
    def printFilename(self) -> str:
        return self._status.print_filename

    @Property(float, notify=statusChanged)
    def printProgress(self) -> float:
        return self._status.print_progress

    @Property(str, notify=statusChanged)
    def printMessage(self) -> str:
        return self._status.print_message

    @Property(float, notify=statusChanged)
    def printDuration(self) -> float:
        return self._status.print_duration

    @Property(float, notify=statusChanged)
    def totalDuration(self) -> float:
        return self._status.total_duration

    @Property(float, notify=statusChanged)
    def filamentUsed(self) -> float:
        return self._status.filament_used

    @Property(int, notify=statusChanged)
    def currentLayer(self) -> int:
        return self._status.current_layer

    @Property(int, notify=statusChanged)
    def totalLayers(self) -> int:
        return self._status.total_layers

    @Property(float, notify=statusChanged)
    def positionX(self) -> float:
        return self._status.position_x

    @Property(float, notify=statusChanged)
    def positionY(self) -> float:
        return self._status.position_y

    @Property(float, notify=statusChanged)
    def positionZ(self) -> float:
        return self._status.position_z

    @Property(float, notify=statusChanged)
    def positionE(self) -> float:
        return self._status.position_e

    @Property(str, notify=statusChanged)
    def homedAxes(self) -> str:
        return self._status.homed_axes

    @Property(float, notify=statusChanged)
    def requestedSpeed(self) -> float:
        return self._status.requested_speed

    @Property(float, notify=statusChanged)
    def speedFactor(self) -> float:
        return self._status.speed_factor

    @Property(float, notify=statusChanged)
    def extrudeFactor(self) -> float:
        return self._status.extrude_factor

    @Property(float, notify=statusChanged)
    def zOffset(self) -> float:
        return self._status.z_offset

    @Property(float, notify=statusChanged)
    def maxAccel(self) -> float:
        return self._status.max_accel

    @Property(float, notify=statusChanged)
    def maxVelocity(self) -> float:
        return self._status.max_velocity

    @Property(float, notify=statusChanged)
    def extruderTemperature(self) -> float:
        return self._status.primary_extruder_temperature

    @Property(float, notify=statusChanged)
    def extruderTarget(self) -> float:
        return self._status.primary_extruder_target
