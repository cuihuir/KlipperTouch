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
GRAPH_HISTORY_LIMIT = 240
GRAPH_ACTIVE_PANELS = {"main", "temperature"}


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
    TARGET_PENDING_ROLE = int(Qt.ItemDataRole.UserRole) + 7
    TARGET_STATE_ROLE = int(Qt.ItemDataRole.UserRole) + 8
    TARGET_SETTABLE_ROLE = int(Qt.ItemDataRole.UserRole) + 9

    def __init__(self, settings: QSettings | None = None) -> None:
        super().__init__()
        self._devices: tuple[TemperatureDeviceStatus, ...] = ()
        self._history: dict[str, list[float]] = {}
        self._target_history: dict[str, list[float]] = {}
        self._graph_visible: dict[str, bool] = {}
        self._graph_series_cache: list[dict[str, object]] = []
        self._graph_series_dirty = True
        self._graph_active = True
        self._graph_signal_pending = False
        self._local_targets: dict[str, tuple[float, str]] = {}
        self._history_limit = GRAPH_HISTORY_LIMIT
        self._settings = (
            settings if settings is not None else QSettings("KlipperTouch", "KlipperTouch")
        )
        self._settings_scope: str | None = None

    def set_status(self, status: PrinterStatus) -> None:
        scope = _graph_scope_for_status(status)
        scope_changed = scope != self._settings_scope
        new_devices = status.temperature_devices
        if scope != self._settings_scope:
            self._settings_scope = scope
            self._graph_visible = self._load_graph_visibility()
            self._migrate_graph_visibility_defaults(new_devices)

        old_names = tuple(device.name for device in self._devices)
        new_names = tuple(device.name for device in new_devices)
        structure_changed = scope_changed or old_names != new_names

        if structure_changed:
            self.beginResetModel()
            self._devices = new_devices
            self._prune_local_targets(new_names)
            self.endResetModel()
            self._invalidate_graph_series()
            changed_rows: list[tuple[int, list[int]]] = []
        else:
            old_rows = [self._role_values_for_device(device) for device in self._devices]
            self._devices = new_devices
            self._prune_local_targets(new_names)
            changed_rows = []

        history_changed = False
        for device in self._devices:
            self._ensure_graph_visibility_default(device)
            if device.name in self._local_targets and device.target is not None:
                del self._local_targets[device.name]
            values = self._history.setdefault(device.name, [])
            if device.temperature is None:
                pass
            else:
                values.append(float(device.temperature))
                del values[:-self._history_limit]
                history_changed = True
            target_values = self._target_history.setdefault(device.name, [])
            if device.target is None:
                continue
            target_values.append(float(device.target))
            del target_values[:-self._history_limit]
            history_changed = True
        if not structure_changed:
            for row, (old_values, device) in enumerate(zip(old_rows, self._devices, strict=True)):
                changed_roles = self._changed_roles(
                    old_values,
                    self._role_values_for_device(device),
                )
                if changed_roles:
                    changed_rows.append((row, changed_roles))
            for row, roles in changed_rows:
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, roles)
        if history_changed:
            self._invalidate_graph_series()
            self.historyChanged.emit()
            self._emit_or_defer_graph_series_changed()

    @Property(list, notify=historyChanged)
    def extruderSeries(self) -> list[float]:
        return list(self._first_series_for_name("extruder"))

    @Property(list, notify=historyChanged)
    def bedSeries(self) -> list[float]:
        return list(self._history.get("heater_bed", []))

    @Property(list, notify=graphSeriesChanged)
    def graphSeriesModel(self) -> list[dict[str, object]]:
        if not self._graph_series_dirty:
            return self._graph_series_cache
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
                    "dashed": False,
                    "legendVisible": True,
                }
            )
            target_points = self._target_history.get(device.name, [])
            effective_target = self._effective_target(device)
            if (
                device.target_settable
                and target_points
                and effective_target is not None
                and effective_target > 0
            ):
                active_target_points = _active_target_series(target_points)
                series.append(
                    {
                        "name": f"{device.name}_target",
                        "displayName": f"{device.display_name} Target",
                        "icon": device.icon,
                        "color": _graph_color_for_device(device.name, index),
                        "series": active_target_points,
                        "dashed": True,
                        "legendVisible": False,
                    }
                )
        self._graph_series_cache = series
        self._graph_series_dirty = False
        return self._graph_series_cache

    def initialize_history(self, temperature_store: dict[str, object]) -> None:
        history: dict[str, list[float]] = {}
        target_history: dict[str, list[float]] = {}
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
            history[name] = _resample_series(normalized, GRAPH_HISTORY_LIMIT)
            max_length = max(max_length, len(normalized))
            targets = values.get("targets")
            if isinstance(targets, list):
                normalized_targets = [
                    float(value) for value in targets if isinstance(value, (int, float))
                ]
                if normalized_targets:
                    target_history[name] = _resample_series(
                        normalized_targets,
                        GRAPH_HISTORY_LIMIT,
                    )
                    max_length = max(max_length, len(normalized_targets))

        if history:
            self._history.update(history)
            self._target_history.update(target_history)
            self._history_limit = min(
                GRAPH_HISTORY_LIMIT,
                max(self._history_limit, max_length),
            )
            self._invalidate_graph_series()
            self.historyChanged.emit()
            self.graphSelectionChanged.emit()
            self._emit_or_defer_graph_series_changed()

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
            return self._effective_target(device)
        if role == self.GRAPH_VISIBLE_ROLE:
            return self._graph_visible.get(device.name, True)
        if role == self.TARGET_PENDING_ROLE:
            return self._target_state(device.name) == "pending"
        if role == self.TARGET_STATE_ROLE:
            return self._target_state(device.name)
        if role == self.TARGET_SETTABLE_ROLE:
            return bool(device.target_settable)
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.NAME_ROLE: QByteArray(b"name"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.ICON_ROLE: QByteArray(b"icon"),
            self.TEMPERATURE_ROLE: QByteArray(b"temperature"),
            self.TARGET_ROLE: QByteArray(b"target"),
            self.GRAPH_VISIBLE_ROLE: QByteArray(b"graphVisible"),
            self.TARGET_PENDING_ROLE: QByteArray(b"targetPending"),
            self.TARGET_STATE_ROLE: QByteArray(b"targetState"),
            self.TARGET_SETTABLE_ROLE: QByteArray(b"targetSettable"),
        }

    @Slot(int, result="QVariantMap")
    def rowData(self, row: int) -> dict[str, object]:
        if not 0 <= row < len(self._devices):
            return {}
        device = self._devices[row]
        return {
            "name": device.name,
            "displayName": device.display_name,
            "icon": device.icon,
            "temperature": device.temperature,
            "target": self._effective_target(device),
            "graphVisible": self._graph_visible.get(device.name, True),
            "targetPending": self._target_state(device.name) == "pending",
            "targetState": self._target_state(device.name),
            "targetSettable": bool(device.target_settable),
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
        self._invalidate_graph_series()
        self.graphSelectionChanged.emit()
        self._emit_or_defer_graph_series_changed()

    def set_graph_active(self, active: bool) -> None:
        if active == self._graph_active:
            return
        self._graph_active = active
        if active and self._graph_signal_pending:
            self._graph_signal_pending = False
            self.graphSeriesChanged.emit()

    @Slot(str, float)
    def setPendingTarget(self, name: str, target: float) -> None:  # noqa: N802
        self._set_local_target(name, target, "pending")

    @Slot(str, float)
    def setFailedTarget(self, name: str, target: float) -> None:  # noqa: N802
        self._set_local_target(name, target, "failed")

    def _set_local_target(self, name: str, target: float, state: str) -> None:
        row = next(
            (
                index
                for index, device in enumerate(self._devices)
                if device.name == name and device.target_settable
            ),
            -1,
        )
        if row < 0:
            return
        self._local_targets[name] = (float(target), state)
        index = self.index(row, 0)
        self.dataChanged.emit(
            index,
            index,
            [self.TARGET_ROLE, self.TARGET_PENDING_ROLE, self.TARGET_STATE_ROLE],
        )

    def _first_series_for_name(self, prefix: str) -> list[float]:
        for device in self._devices:
            if device.name == prefix:
                return self._history.get(device.name, [])
        for device in self._devices:
            if device.name.startswith(prefix):
                return self._history.get(device.name, [])
        return []

    def _effective_target(self, device: TemperatureDeviceStatus) -> float | None:
        if device.name in self._local_targets:
            return self._local_targets[device.name][0]
        if not device.target_settable:
            return None
        if device.target is not None and device.target > 0:
            return device.target
        target_history = self._target_history.get(device.name, [])
        if target_history and target_history[-1] > 0:
            return target_history[-1]
        return device.target

    def _target_state(self, name: str) -> str:
        if name in self._local_targets:
            return self._local_targets[name][1]
        return "actual"

    def _invalidate_graph_series(self) -> None:
        self._graph_series_dirty = True

    def _emit_or_defer_graph_series_changed(self) -> None:
        if self._graph_active:
            self.graphSeriesChanged.emit()
            return
        self._graph_signal_pending = True

    def _role_values_for_device(self, device: TemperatureDeviceStatus) -> dict[int, object]:
        return {
            self.NAME_ROLE: device.name,
            self.DISPLAY_NAME_ROLE: device.display_name,
            self.ICON_ROLE: device.icon,
            self.TEMPERATURE_ROLE: device.temperature,
            self.TARGET_ROLE: self._effective_target(device),
            self.GRAPH_VISIBLE_ROLE: self._graph_visible.get(device.name, True),
            self.TARGET_PENDING_ROLE: self._target_state(device.name) == "pending",
            self.TARGET_STATE_ROLE: self._target_state(device.name),
            self.TARGET_SETTABLE_ROLE: bool(device.target_settable),
        }

    def _changed_roles(
        self,
        old_values: dict[int, object],
        new_values: dict[int, object],
    ) -> list[int]:
        return [
            role
            for role in (
                self.NAME_ROLE,
                self.DISPLAY_NAME_ROLE,
                self.ICON_ROLE,
                self.TEMPERATURE_ROLE,
                self.TARGET_ROLE,
                self.GRAPH_VISIBLE_ROLE,
                self.TARGET_PENDING_ROLE,
                self.TARGET_STATE_ROLE,
                self.TARGET_SETTABLE_ROLE,
            )
            if old_values.get(role) != new_values.get(role)
        ]

    def _prune_local_targets(self, names: tuple[str, ...]) -> None:
        valid_names = set(names)
        for name in tuple(self._local_targets):
            if name not in valid_names:
                del self._local_targets[name]

    def _ensure_graph_visibility_default(self, device: TemperatureDeviceStatus) -> None:
        if device.name in self._graph_visible:
            return
        self._graph_visible[device.name] = bool(device.target_settable)

    def _load_graph_visibility(self) -> dict[str, bool]:
        if self._settings_scope is None:
            return {}
        self._settings.beginGroup(f"temperature_graph/{self._settings_scope}")
        values: dict[str, bool] = {}
        for key in self._settings.childKeys():
            if key.startswith("_"):
                continue
            values[key] = bool(self._settings.value(key, True, type=bool))
        self._settings.endGroup()
        return values

    def _migrate_graph_visibility_defaults(
        self,
        devices: tuple[TemperatureDeviceStatus, ...],
    ) -> None:
        if self._settings_scope is None:
            return
        self._settings.beginGroup(f"temperature_graph/{self._settings_scope}")
        raw_version = self._settings.value("_defaults_version", 0, type=int)
        version = raw_version if isinstance(raw_version, int) else 0
        if version < 2:
            for device in devices:
                if device.target_settable:
                    continue
                self._graph_visible[device.name] = False
                self._settings.setValue(device.name, False)
            self._settings.setValue("_defaults_version", 2)
        self._settings.endGroup()
        self._settings.sync()

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


def _active_target_series(points: list[float]) -> list[float | None]:
    return [point if point > 0 else None for point in points]


def _resample_series(points: list[float], limit: int) -> list[float]:
    if len(points) <= limit:
        return points
    if limit <= 1:
        return points[-limit:]
    step = (len(points) - 1) / (limit - 1)
    return [points[round(index * step)] for index in range(limit)]


def _graph_scope_for_status(status: PrinterStatus) -> str | None:
    hostname = status.hostname.strip()
    if not hostname or hostname == "unknown":
        return None
    return hostname


class StatusModel(QObject):
    statusChanged = Signal()
    activePanelChanged = Signal()
    hostChanged = Signal()
    infoChanged = Signal()
    objectsChanged = Signal()
    printChanged = Signal()
    excludeObjectChanged = Signal()
    toolheadChanged = Signal()
    extruderTemperatureChanged = Signal()
    filamentSensorChanged = Signal()

    def __init__(
        self,
        temperature_device_model: TemperatureDeviceListModel | None = None,
    ) -> None:
        super().__init__()
        self._status = PrinterStatus()
        self._temperature_device_model = temperature_device_model
        self._active_panel = "main"
        if self._temperature_device_model is not None:
            self._temperature_device_model.set_graph_active(
                _panel_has_temperature_graph(self._active_panel)
            )

    def set_status(self, status: PrinterStatus) -> None:
        previous = self._status
        self._status = status
        if self._temperature_device_model is not None:
            self._temperature_device_model.set_status(status)
        if _host_fields_changed(previous, status):
            self.hostChanged.emit()
        if _info_fields_changed(previous, status):
            self.infoChanged.emit()
        if _object_fields_changed(previous, status):
            self.objectsChanged.emit()
        if _print_fields_changed(previous, status):
            self.printChanged.emit()
        if _exclude_object_fields_changed(previous, status):
            self.excludeObjectChanged.emit()
        if _toolhead_fields_changed(previous, status) and _panel_needs_toolhead(self._active_panel):
            self.toolheadChanged.emit()
        if _primary_extruder_fields_changed(previous, status):
            self.extruderTemperatureChanged.emit()
        if _filament_sensor_fields_changed(previous, status):
            self.filamentSensorChanged.emit()
        if previous != status:
            self.statusChanged.emit()

    @Property(str, notify=activePanelChanged)
    def activePanel(self) -> str:
        return self._active_panel

    @property
    def active_panel_name(self) -> str:
        return self._active_panel

    @Slot(str)
    def setActivePanel(self, panel: str) -> None:  # noqa: N802
        next_panel = str(panel or "main")
        if next_panel == self._active_panel:
            return
        previous_panel = self._active_panel
        self._active_panel = next_panel
        if self._temperature_device_model is not None:
            self._temperature_device_model.set_graph_active(
                _panel_has_temperature_graph(next_panel)
            )
        self.activePanelChanged.emit()
        if not _panel_needs_toolhead(previous_panel) and _panel_needs_toolhead(next_panel):
            self.toolheadChanged.emit()

    @Property(str, notify=hostChanged)
    def hostname(self) -> str:
        return self._status.hostname

    @Property(str, notify=hostChanged)
    def klippyState(self) -> str:
        return self._status.klippy_state

    @Property(str, notify=hostChanged)
    def webhooksState(self) -> str:
        return self._status.webhooks_state

    @Property(str, notify=hostChanged)
    def webhooksMessage(self) -> str:
        return self._status.webhooks_message

    @Property(str, notify=infoChanged)
    def klipperVersion(self) -> str:
        return self._status.klipper_version

    @Property(str, notify=infoChanged)
    def moonrakerVersion(self) -> str:
        return self._status.moonraker_version

    @Property(int, notify=infoChanged)
    def mcuCount(self) -> int:
        return self._status.mcu_count

    @Property(list, notify=infoChanged)
    def mcuInfos(self) -> list[dict[str, str]]:
        return [
            {
                "name": item.name,
                "version": item.version,
                "build_versions": item.build_versions,
            }
            for item in self._status.mcu_statuses
        ]

    @Property(int, notify=infoChanged)
    def serviceVersionCount(self) -> int:
        return self._status.service_version_count

    @Property(list, notify=infoChanged)
    def serviceVersions(self) -> list[dict[str, str]]:
        return [
            {
                "name": item.name,
                "version": item.version,
                "configured_type": item.configured_type,
            }
            for item in self._status.service_versions
        ]

    @Property(int, notify=objectsChanged)
    def objectCount(self) -> int:
        return self._status.object_count

    @Property(list, notify=objectsChanged)
    def objectNames(self) -> list[str]:
        return list(self._status.objects)

    @Property(int, notify=objectsChanged)
    def temperatureDeviceCount(self) -> int:
        return self._status.temperature_device_count

    @Property(int, notify=filamentSensorChanged)
    def filamentSensorCount(self) -> int:  # noqa: N802
        return self._status.filament_sensor_count

    @Property(list, notify=filamentSensorChanged)
    def filamentSensors(self) -> list[dict[str, object]]:  # noqa: N802
        return [
            {
                "name": sensor.name,
                "display_name": sensor.display_name,
                "sensor_type": sensor.sensor_type,
                "enabled": sensor.enabled,
                "filament_detected": sensor.filament_detected,
            }
            for sensor in self._status.filament_sensors
        ]

    @Property(str, notify=printChanged)
    def printState(self) -> str:
        return self._status.print_state

    @Property(str, notify=printChanged)
    def printFilename(self) -> str:
        return self._status.print_filename

    @Property(float, notify=printChanged)
    def printProgress(self) -> float:
        return self._status.print_progress

    @Property(str, notify=printChanged)
    def printMessage(self) -> str:
        return self._status.print_message

    @Property(float, notify=printChanged)
    def printDuration(self) -> float:
        return self._status.print_duration

    @Property(float, notify=printChanged)
    def totalDuration(self) -> float:
        return self._status.total_duration

    @Property(float, notify=printChanged)
    def filamentUsed(self) -> float:
        return self._status.filament_used

    @Property(int, notify=printChanged)
    def currentLayer(self) -> int:
        return self._status.current_layer

    @Property(int, notify=printChanged)
    def totalLayers(self) -> int:
        return self._status.total_layers

    @Property(list, notify=excludeObjectChanged)
    def excludeObjectNames(self) -> list[str]:
        return list(self._status.exclude_object_names)

    @Property(list, notify=excludeObjectChanged)
    def excludedObjectNames(self) -> list[str]:
        return list(self._status.excluded_object_names)

    @Property(str, notify=excludeObjectChanged)
    def currentObject(self) -> str:
        return self._status.current_object

    @Property(int, notify=excludeObjectChanged)
    def excludeObjectCount(self) -> int:
        return self._status.exclude_object_count

    @Property(int, notify=excludeObjectChanged)
    def excludedObjectCount(self) -> int:
        return self._status.excluded_object_count

    @Property(float, notify=toolheadChanged)
    def positionX(self) -> float:
        return self._status.position_x

    @Property(float, notify=toolheadChanged)
    def positionY(self) -> float:
        return self._status.position_y

    @Property(float, notify=toolheadChanged)
    def positionZ(self) -> float:
        return self._status.position_z

    @Property(float, notify=toolheadChanged)
    def positionE(self) -> float:
        return self._status.position_e

    @Property(float, notify=toolheadChanged)
    def positionU(self) -> float:
        return self._status.position_u

    @Property(float, notify=toolheadChanged)
    def positionV(self) -> float:
        return self._status.position_v

    @Property(float, notify=toolheadChanged)
    def positionW(self) -> float:
        return self._status.position_w

    @Property(bool, notify=objectsChanged)
    def fiveAxisAvailable(self) -> bool:
        return "independent_3z" in self._status.objects

    @Property(bool, notify=objectsChanged)
    def acceleratorLevelAvailable(self) -> bool:
        return "accelerator_level" in self._status.objects

    @Property(bool, notify=objectsChanged)
    def zTiltAvailable(self) -> bool:
        return "z_tilt" in self._status.objects

    @Property(str, notify=toolheadChanged)
    def homedAxes(self) -> str:
        return self._status.homed_axes

    @Property(float, notify=toolheadChanged)
    def requestedSpeed(self) -> float:
        return self._status.requested_speed

    @Property(float, notify=toolheadChanged)
    def speedFactor(self) -> float:
        return self._status.speed_factor

    @Property(float, notify=toolheadChanged)
    def extrudeFactor(self) -> float:
        return self._status.extrude_factor

    @Property(float, notify=toolheadChanged)
    def zOffset(self) -> float:
        return self._status.z_offset

    @Property(float, notify=toolheadChanged)
    def maxAccel(self) -> float:
        return self._status.max_accel

    @Property(float, notify=toolheadChanged)
    def maxVelocity(self) -> float:
        return self._status.max_velocity

    @Property(float, notify=extruderTemperatureChanged)
    def extruderTemperature(self) -> float:
        return self._status.primary_extruder_temperature

    @Property(float, notify=extruderTemperatureChanged)
    def extruderTarget(self) -> float:
        return self._status.primary_extruder_target

    @Property(bool, notify=extruderTemperatureChanged)
    def extruderCanExtrude(self) -> bool:  # noqa: N802
        return self._status.extruder_can_extrude

    @Property(float, notify=extruderTemperatureChanged)
    def extruderPressureAdvance(self) -> float:  # noqa: N802
        return self._status.extruder_pressure_advance

    @Property(float, notify=extruderTemperatureChanged)
    def extruderSmoothTime(self) -> float:  # noqa: N802
        return self._status.extruder_smooth_time


def _host_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return (
        previous.hostname,
        previous.klippy_state,
        previous.webhooks_state,
        previous.webhooks_message,
    ) != (
        current.hostname,
        current.klippy_state,
        current.webhooks_state,
        current.webhooks_message,
    )


def _info_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return (
        previous.klipper_version,
        previous.moonraker_version,
        previous.mcu_statuses,
        previous.service_versions,
    ) != (
        current.klipper_version,
        current.moonraker_version,
        current.mcu_statuses,
        current.service_versions,
    )


def _object_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    previous_device_names = tuple(device.name for device in previous.temperature_devices)
    current_device_names = tuple(device.name for device in current.temperature_devices)
    return (previous.objects, previous_device_names) != (
        current.objects,
        current_device_names,
    )


def _filament_sensor_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return previous.filament_sensors != current.filament_sensors


def _print_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return (
        previous.print_state,
        previous.print_filename,
        previous.print_progress,
        previous.print_message,
        previous.print_duration,
        previous.total_duration,
        previous.filament_used,
        previous.current_layer,
        previous.total_layers,
    ) != (
        current.print_state,
        current.print_filename,
        current.print_progress,
        current.print_message,
        current.print_duration,
        current.total_duration,
        current.filament_used,
        current.current_layer,
        current.total_layers,
    )


def _exclude_object_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return (
        previous.exclude_object_names,
        previous.excluded_object_names,
        previous.current_object,
    ) != (
        current.exclude_object_names,
        current.excluded_object_names,
        current.current_object,
    )


def _toolhead_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return (
        previous.position_x,
        previous.position_y,
        previous.position_z,
        previous.position_e,
        previous.position_u,
        previous.position_v,
        previous.position_w,
        previous.homed_axes,
        previous.requested_speed,
        previous.speed_factor,
        previous.extrude_factor,
        previous.z_offset,
        previous.max_accel,
        previous.max_velocity,
    ) != (
        current.position_x,
        current.position_y,
        current.position_z,
        current.position_e,
        current.position_u,
        current.position_v,
        current.position_w,
        current.homed_axes,
        current.requested_speed,
        current.speed_factor,
        current.extrude_factor,
        current.z_offset,
        current.max_accel,
        current.max_velocity,
    )


def _primary_extruder_fields_changed(previous: PrinterStatus, current: PrinterStatus) -> bool:
    return (
        previous.primary_extruder_temperature,
        previous.primary_extruder_target,
        previous.extruder_can_extrude,
        previous.extruder_pressure_advance,
        previous.extruder_smooth_time,
    ) != (
        current.primary_extruder_temperature,
        current.primary_extruder_target,
        current.extruder_can_extrude,
        current.extruder_pressure_advance,
        current.extruder_smooth_time,
    )


def _panel_needs_toolhead(panel: str) -> bool:
    return panel in {"move", "extrude", "job_status"}


def _panel_has_temperature_graph(panel: str) -> bool:
    return panel in GRAPH_ACTIVE_PANELS
