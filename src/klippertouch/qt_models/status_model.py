from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
)

from klippertouch.domain.printer import PrinterStatus, TemperatureDeviceStatus

EMPTY_INDEX = QModelIndex()


class TemperatureDeviceListModel(QAbstractListModel):
    historyChanged = Signal()

    NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    DISPLAY_NAME_ROLE = int(Qt.ItemDataRole.UserRole) + 2
    ICON_ROLE = int(Qt.ItemDataRole.UserRole) + 3
    TEMPERATURE_ROLE = int(Qt.ItemDataRole.UserRole) + 4
    TARGET_ROLE = int(Qt.ItemDataRole.UserRole) + 5

    def __init__(self) -> None:
        super().__init__()
        self._devices: tuple[TemperatureDeviceStatus, ...] = ()
        self._history: dict[str, list[float]] = {"extruder": [], "heater_bed": []}

    def set_status(self, status: PrinterStatus) -> None:
        self.beginResetModel()
        self._devices = status.temperature_devices
        self.endResetModel()
        history_changed = False
        for device in self._devices:
            key = _history_key_for_device(device.name)
            if key is None or device.temperature is None:
                continue
            values = self._history[key]
            values.append(float(device.temperature))
            del values[:-60]
            history_changed = True
        if history_changed:
            self.historyChanged.emit()

    @Property(list, notify=historyChanged)
    def extruderSeries(self) -> list[float]:
        return list(self._history["extruder"])

    @Property(list, notify=historyChanged)
    def bedSeries(self) -> list[float]:
        return list(self._history["heater_bed"])

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
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.NAME_ROLE: QByteArray(b"name"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.ICON_ROLE: QByteArray(b"icon"),
            self.TEMPERATURE_ROLE: QByteArray(b"temperature"),
            self.TARGET_ROLE: QByteArray(b"target"),
        }


def _history_key_for_device(name: str) -> str | None:
    if name == "extruder" or name.startswith("extruder"):
        return "extruder"
    if name == "heater_bed":
        return "heater_bed"
    return None


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
