# KlipperTouch Clean Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clean, production-oriented PySide6/QML project skeleton that can start locally, load configuration, render a non-controlling shell, and perform read-only Moonraker probes.

**Architecture:** Python owns configuration, Moonraker IO, domain state, safety gates, and Qt model bridges. QML owns presentation only and receives data through focused `QObject` models. The Moonraker layer defaults to read-only mode and rejects state-changing commands before they can leave the process.

**Tech Stack:** Python 3.10+, PySide6, QML, pytest, pytest-qt, ruff, mypy, websockets or Qt WebSocket in a later phase, requests/httpx for REST.

---

## File Structure

Create these files in the first implementation phase:

- `pyproject.toml`: package metadata, dependencies, pytest, ruff, and mypy settings.
- `src/klippertouch/__init__.py`: package version.
- `src/klippertouch/__main__.py`: `python -m klippertouch` entry.
- `src/klippertouch/app.py`: Qt application bootstrap and QML engine setup.
- `src/klippertouch/cli.py`: argument parsing.
- `src/klippertouch/config/models.py`: typed configuration dataclasses.
- `src/klippertouch/config/loader.py`: KlipperScreen-compatible INI subset loading.
- `src/klippertouch/moonraker/client.py`: read-only REST client.
- `src/klippertouch/moonraker/safety.py`: command policy and denylist.
- `src/klippertouch/domain/printer.py`: minimal printer status model.
- `src/klippertouch/qt_models/status_model.py`: Qt bridge exposed to QML.
- `src/klippertouch/qml/main.qml`: initial shell.
- `src/klippertouch/qml/components/StatusBar.qml`: top status component.
- `src/klippertouch/qml/components/ActionBar.qml`: non-functional navigation bar.
- `config/KlipperTouch.conf.example`: safe example config.
- `tests/unit/...`: unit tests for config, safety, domain, and client URL behavior.
- `tests/qml/test_qml_loads.py`: smoke test that loads QML offscreen.

## Task 1: Project Tooling Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/klippertouch/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write the failing package import test**

Create `tests/unit/test_package_metadata.py`:

```python
from klippertouch import __version__


def test_package_version_is_defined() -> None:
    assert __version__ == "0.1.0"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/unit/test_package_metadata.py -v`

Expected: `ModuleNotFoundError: No module named 'klippertouch'`.

- [ ] **Step 3: Add project metadata and package version**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "klippertouch"
version = "0.1.0"
description = "PySide6/QML touchscreen UI for Klipper printers"
readme = "README.md"
requires-python = ">=3.10"
license = "GPL-3.0-or-later"
dependencies = [
  "PySide6>=6.5",
  "requests>=2.31",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pytest-qt>=4.4",
  "ruff>=0.4",
  "mypy>=1.8",
  "types-requests>=2.31",
]

[project.scripts]
klippertouch = "klippertouch.__main__:main"

[tool.hatch.build.targets.wheel]
packages = ["src/klippertouch"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.ruff]
line-length = 100
target-version = "py310"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.10"
strict = true
packages = ["klippertouch"]
```

Create `src/klippertouch/__init__.py`:

```python
__version__ = "0.1.0"
```

Create `tests/conftest.py`:

```python
import os


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/unit/test_package_metadata.py -v`

Expected: one passing test.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/klippertouch/__init__.py tests/conftest.py tests/unit/test_package_metadata.py
git commit -m "build: add python project scaffold"
```

## Task 2: CLI And Application Bootstrap

**Files:**
- Create: `src/klippertouch/__main__.py`
- Create: `src/klippertouch/cli.py`
- Create: `src/klippertouch/app.py`
- Create: `tests/unit/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Create `tests/unit/test_cli.py`:

```python
from pathlib import Path

from klippertouch.cli import parse_args


def test_parse_args_defaults_to_read_only() -> None:
    args = parse_args([])
    assert args.read_only is True
    assert args.config is None
    assert args.debug is False


def test_parse_args_accepts_config_and_debug() -> None:
    args = parse_args(["--config", "/tmp/KlipperTouch.conf", "--debug"])
    assert args.config == Path("/tmp/KlipperTouch.conf")
    assert args.debug is True
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/unit/test_cli.py -v`

Expected: import failure for `klippertouch.cli`.

- [ ] **Step 3: Implement CLI and bootstrap stubs**

Create `src/klippertouch/cli.py`:

```python
from argparse import ArgumentParser, Namespace
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(prog="klippertouch")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--read-only", action="store_true", default=True)
    return parser.parse_args(argv)
```

Create `src/klippertouch/app.py`:

```python
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication


def run_app(argv: list[str] | None = None) -> int:
    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()
```

Create `src/klippertouch/__main__.py`:

```python
import sys

from klippertouch.app import run_app
from klippertouch.cli import parse_args


def main() -> int:
    args = parse_args()
    if args.debug:
        print("Debug logging enabled")
    return run_app(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the CLI tests**

Run: `pytest tests/unit/test_cli.py -v`

Expected: two passing tests.

- [ ] **Step 5: Commit**

```bash
git add src/klippertouch/__main__.py src/klippertouch/cli.py src/klippertouch/app.py tests/unit/test_cli.py
git commit -m "feat: add cli and qt bootstrap"
```

## Task 3: Safe Configuration Loader

**Files:**
- Create: `src/klippertouch/config/__init__.py`
- Create: `src/klippertouch/config/models.py`
- Create: `src/klippertouch/config/loader.py`
- Create: `config/KlipperTouch.conf.example`
- Create: `tests/unit/config/test_loader.py`

- [ ] **Step 1: Write failing config tests**

Create `tests/unit/config/test_loader.py`:

```python
from pathlib import Path

from klippertouch.config.loader import load_config


def test_load_config_reads_default_printer(tmp_path: Path) -> None:
    config = tmp_path / "KlipperTouch.conf"
    config.write_text(
        "[main]\n"
        "default_printer = TestPrinter\n"
        "\n"
        "[printer TestPrinter]\n"
        "moonraker_host = 192.168.123.117\n"
        "moonraker_port = 7125\n",
        encoding="utf-8",
    )

    settings = load_config(config)

    assert settings.default_printer == "TestPrinter"
    assert settings.printers["TestPrinter"].moonraker_host == "192.168.123.117"
    assert settings.printers["TestPrinter"].moonraker_port == 7125
    assert settings.read_only is True


def test_load_config_provides_local_default_when_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.conf"

    settings = load_config(missing)

    assert settings.default_printer == "Printer"
    assert settings.printers["Printer"].moonraker_host == "127.0.0.1"
    assert settings.printers["Printer"].moonraker_port == 7125
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/config/test_loader.py -v`

Expected: import failure for `klippertouch.config`.

- [ ] **Step 3: Implement config models and loader**

Create `src/klippertouch/config/__init__.py`:

```python
from klippertouch.config.loader import load_config
from klippertouch.config.models import AppSettings, PrinterConfig

__all__ = ["AppSettings", "PrinterConfig", "load_config"]
```

Create `src/klippertouch/config/models.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PrinterConfig:
    name: str
    moonraker_host: str = "127.0.0.1"
    moonraker_port: int = 7125
    moonraker_path: str = ""
    moonraker_ssl: bool = False
    moonraker_api_key: str = ""


@dataclass(frozen=True)
class AppSettings:
    default_printer: str
    printers: dict[str, PrinterConfig]
    read_only: bool = True
```

Create `src/klippertouch/config/loader.py`:

```python
from configparser import ConfigParser
from pathlib import Path

from klippertouch.config.models import AppSettings, PrinterConfig


def load_config(path: Path) -> AppSettings:
    parser = ConfigParser()
    if path.exists():
        parser.read(path, encoding="utf-8")

    printer_sections = [section for section in parser.sections() if section.startswith("printer ")]
    if not printer_sections:
        default = PrinterConfig(name="Printer")
        return AppSettings(default_printer="Printer", printers={"Printer": default})

    printers: dict[str, PrinterConfig] = {}
    for section in printer_sections:
        name = section.removeprefix("printer ").strip()
        printers[name] = PrinterConfig(
            name=name,
            moonraker_host=parser.get(section, "moonraker_host", fallback="127.0.0.1"),
            moonraker_port=parser.getint(section, "moonraker_port", fallback=7125),
            moonraker_path=parser.get(section, "moonraker_path", fallback="").strip("/"),
            moonraker_ssl=parser.getboolean(section, "moonraker_ssl", fallback=False),
            moonraker_api_key=parser.get(section, "moonraker_api_key", fallback="").replace('"', ""),
        )

    default_printer = parser.get("main", "default_printer", fallback=next(iter(printers)))
    if default_printer not in printers:
        default_printer = next(iter(printers))

    return AppSettings(default_printer=default_printer, printers=printers)
```

Create `config/KlipperTouch.conf.example`:

```ini
[main]
default_printer = MyPrinter

[printer MyPrinter]
moonraker_host = 127.0.0.1
moonraker_port = 7125
moonraker_path =
moonraker_ssl = false
moonraker_api_key =
```

- [ ] **Step 4: Run config tests**

Run: `pytest tests/unit/config/test_loader.py -v`

Expected: two passing tests.

- [ ] **Step 5: Commit**

```bash
git add src/klippertouch/config config/KlipperTouch.conf.example tests/unit/config/test_loader.py
git commit -m "feat: add safe config loader"
```

## Task 4: Read-Only Moonraker Client And Safety Gate

**Files:**
- Create: `src/klippertouch/moonraker/__init__.py`
- Create: `src/klippertouch/moonraker/safety.py`
- Create: `src/klippertouch/moonraker/client.py`
- Create: `tests/unit/moonraker/test_safety.py`
- Create: `tests/unit/moonraker/test_client.py`

- [ ] **Step 1: Write failing safety and client tests**

Create `tests/unit/moonraker/test_safety.py`:

```python
import pytest

from klippertouch.moonraker.safety import CommandPolicy, UnsafeCommandError


def test_read_only_policy_allows_get_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "server/info")
    policy.validate_http("GET", "printer/info")
    policy.validate_http("GET", "printer/objects/list")


def test_read_only_policy_blocks_control_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("printer.gcode.script")
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("printer.print.start")
```

Create `tests/unit/moonraker/test_client.py`:

```python
from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.client import MoonrakerClient


def test_client_builds_plain_http_endpoint() -> None:
    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host", moonraker_port=7125))
    assert client.endpoint == "http://host:7125"


def test_client_builds_path_and_ssl_endpoint() -> None:
    client = MoonrakerClient(
        PrinterConfig(
            name="p",
            moonraker_host="host",
            moonraker_port=7130,
            moonraker_path="printer",
            moonraker_ssl=True,
        )
    )
    assert client.endpoint == "https://host:7130/printer"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/moonraker -v`

Expected: import failure for `klippertouch.moonraker`.

- [ ] **Step 3: Implement safety and read-only client**

Create `src/klippertouch/moonraker/__init__.py`:

```python
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.safety import CommandPolicy, UnsafeCommandError

__all__ = ["CommandPolicy", "MoonrakerClient", "UnsafeCommandError"]
```

Create `src/klippertouch/moonraker/safety.py`:

```python
class UnsafeCommandError(RuntimeError):
    pass


class CommandPolicy:
    def __init__(self, read_only: bool = True) -> None:
        self.read_only = read_only
        self.allowed_gets = {
            "server/info",
            "printer/info",
            "printer/objects/list",
            "printer/objects/query",
        }
        self.blocked_jsonrpc_prefixes = (
            "printer.gcode.",
            "printer.print.",
            "printer.emergency_stop",
            "printer.restart",
            "printer.firmware_restart",
            "machine.device_power.",
            "machine.services.",
        )

    def validate_http(self, method: str, endpoint: str) -> None:
        normalized = endpoint.strip("/")
        if self.read_only and method.upper() != "GET":
            raise UnsafeCommandError(f"Blocked non-GET request in read-only mode: {method} {endpoint}")
        if self.read_only and normalized not in self.allowed_gets:
            raise UnsafeCommandError(f"Blocked endpoint in read-only mode: {endpoint}")

    def validate_jsonrpc(self, method: str) -> None:
        if not self.read_only:
            return
        if method.startswith(self.blocked_jsonrpc_prefixes):
            raise UnsafeCommandError(f"Blocked JSON-RPC method in read-only mode: {method}")
```

Create `src/klippertouch/moonraker/client.py`:

```python
from typing import Any

import requests

from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.safety import CommandPolicy


class MoonrakerClient:
    def __init__(self, config: PrinterConfig, policy: CommandPolicy | None = None) -> None:
        self.config = config
        self.policy = policy or CommandPolicy(read_only=True)

    @property
    def endpoint(self) -> str:
        proto = "https" if self.config.moonraker_ssl else "http"
        path = f"/{self.config.moonraker_path}" if self.config.moonraker_path else ""
        return f"{proto}://{self.config.moonraker_host}:{self.config.moonraker_port}{path}"

    def get(self, endpoint: str, timeout: float = 4.0) -> dict[str, Any]:
        self.policy.validate_http("GET", endpoint)
        headers = {"x-api-key": self.config.moonraker_api_key} if self.config.moonraker_api_key else {}
        response = requests.get(f"{self.endpoint}/{endpoint.strip('/')}", headers=headers, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        return payload["result"] if isinstance(payload, dict) and "result" in payload else payload

    def get_server_info(self) -> dict[str, Any]:
        return self.get("server/info")

    def get_printer_info(self) -> dict[str, Any]:
        return self.get("printer/info")

    def get_objects_list(self) -> dict[str, Any]:
        return self.get("printer/objects/list")
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/moonraker -v`

Expected: four passing tests.

- [ ] **Step 5: Commit**

```bash
git add src/klippertouch/moonraker tests/unit/moonraker
git commit -m "feat: add read-only moonraker client"
```

## Task 5: Domain Model And Qt Status Bridge

**Files:**
- Create: `src/klippertouch/domain/__init__.py`
- Create: `src/klippertouch/domain/printer.py`
- Create: `src/klippertouch/qt_models/__init__.py`
- Create: `src/klippertouch/qt_models/status_model.py`
- Create: `tests/unit/domain/test_printer_status.py`
- Create: `tests/unit/qt_models/test_status_model.py`

- [ ] **Step 1: Write failing model tests**

Create `tests/unit/domain/test_printer_status.py`:

```python
from klippertouch.domain.printer import PrinterStatus


def test_printer_status_from_probe_payloads() -> None:
    status = PrinterStatus.from_probe(
        server_info={"moonraker_version": "v0.10.0", "klippy_state": "ready"},
        printer_info={"state": "ready", "hostname": "orangepi3b", "software_version": "v0.13.0"},
        objects={"objects": ["extruder", "heater_bed", "controller_fan 驱动"]},
    )

    assert status.hostname == "orangepi3b"
    assert status.klippy_state == "ready"
    assert status.object_count == 3
    assert "controller_fan 驱动" in status.objects
```

Create `tests/unit/qt_models/test_status_model.py`:

```python
from klippertouch.domain.printer import PrinterStatus
from klippertouch.qt_models.status_model import StatusModel


def test_status_model_exposes_printer_status(qtbot) -> None:
    model = StatusModel()
    status = PrinterStatus(
        hostname="orangepi3b",
        klippy_state="ready",
        klipper_version="v0.13.0",
        moonraker_version="v0.10.0",
        objects=("extruder",),
    )

    with qtbot.waitSignal(model.statusChanged, timeout=1000):
        model.set_status(status)

    assert model.hostname == "orangepi3b"
    assert model.klippyState == "ready"
    assert model.objectCount == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/domain tests/unit/qt_models -v`

Expected: import failures for `domain` and `qt_models`.

- [ ] **Step 3: Implement domain and Qt bridge**

Create `src/klippertouch/domain/__init__.py`:

```python
from klippertouch.domain.printer import PrinterStatus

__all__ = ["PrinterStatus"]
```

Create `src/klippertouch/domain/printer.py`:

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PrinterStatus:
    hostname: str = "unknown"
    klippy_state: str = "disconnected"
    klipper_version: str = "unknown"
    moonraker_version: str = "unknown"
    objects: tuple[str, ...] = ()

    @property
    def object_count(self) -> int:
        return len(self.objects)

    @classmethod
    def from_probe(
        cls,
        server_info: dict[str, Any],
        printer_info: dict[str, Any],
        objects: dict[str, Any],
    ) -> "PrinterStatus":
        return cls(
            hostname=str(printer_info.get("hostname", "unknown")),
            klippy_state=str(server_info.get("klippy_state", printer_info.get("state", "unknown"))),
            klipper_version=str(printer_info.get("software_version", "unknown")),
            moonraker_version=str(server_info.get("moonraker_version", "unknown")),
            objects=tuple(str(item) for item in objects.get("objects", ())),
        )
```

Create `src/klippertouch/qt_models/__init__.py`:

```python
from klippertouch.qt_models.status_model import StatusModel

__all__ = ["StatusModel"]
```

Create `src/klippertouch/qt_models/status_model.py`:

```python
from PySide6.QtCore import Property, QObject, Signal

from klippertouch.domain.printer import PrinterStatus


class StatusModel(QObject):
    statusChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = PrinterStatus()

    def set_status(self, status: PrinterStatus) -> None:
        self._status = status
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
    def objectCount(self) -> int:
        return self._status.object_count
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/domain tests/unit/qt_models -v`

Expected: two passing tests.

- [ ] **Step 5: Commit**

```bash
git add src/klippertouch/domain src/klippertouch/qt_models tests/unit/domain tests/unit/qt_models
git commit -m "feat: add printer status model"
```

## Task 6: Initial QML Shell

**Files:**
- Create: `src/klippertouch/qml/main.qml`
- Create: `src/klippertouch/qml/components/StatusBar.qml`
- Create: `src/klippertouch/qml/components/ActionBar.qml`
- Modify: `src/klippertouch/app.py`
- Create: `tests/qml/test_qml_loads.py`

- [ ] **Step 1: Write failing QML smoke test**

Create `tests/qml/test_qml_loads.py`:

```python
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


def test_main_qml_loads(qapp) -> None:
    engine = QQmlApplicationEngine()
    qml_path = Path("src/klippertouch/qml/main.qml").resolve()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    assert engine.rootObjects()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/qml/test_qml_loads.py -v`

Expected: QML load failure because `main.qml` does not exist.

- [ ] **Step 3: Create QML shell**

Create `src/klippertouch/qml/components/StatusBar.qml`:

```qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    required property string hostname
    required property string state
    required property int objectCount

    color: "#1f252b"
    height: 56

    Row {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 18

        Label {
            color: "white"
            text: "KlipperTouch"
            font.pixelSize: 22
            font.bold: true
        }

        Label {
            color: "#d8dee9"
            text: root.hostname + " | " + root.state + " | objects: " + root.objectCount
            font.pixelSize: 16
        }
    }
}
```

Create `src/klippertouch/qml/components/ActionBar.qml`:

```qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 92
    color: "#2b3138"

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Repeater {
            model: ["Back", "Home", "Status", "Files", "Temp", "Move"]

            Button {
                enabled: false
                text: modelData
                height: 52
                width: parent.width
            }
        }
    }
}
```

Create `src/klippertouch/qml/main.qml`:

```qml
import QtQuick
import QtQuick.Controls
import "components"

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
    title: "KlipperTouch"

    property var bridgeModel: typeof statusModel === "undefined" ? null : statusModel
    property string hostname: bridgeModel ? bridgeModel.hostname : "offline"
    property string klippyState: bridgeModel ? bridgeModel.klippyState : "disconnected"
    property int objectCount: bridgeModel ? bridgeModel.objectCount : 0

    Rectangle {
        anchors.fill: parent
        color: "#11161a"

        StatusBar {
            id: statusBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            hostname: window.hostname
            state: window.klippyState
            objectCount: window.objectCount
        }

        ActionBar {
            id: actionBar
            anchors.top: statusBar.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
        }

        Rectangle {
            anchors.top: statusBar.bottom
            anchors.left: actionBar.right
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 18
            radius: 18
            color: "#202830"

            Label {
                anchors.centerIn: parent
                color: "#d8dee9"
                text: "Read-only skeleton. Printer controls are disabled."
                font.pixelSize: 24
            }
        }
    }
}
```

Modify `src/klippertouch/app.py` to expose `statusModel`:

```python
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from klippertouch.qt_models.status_model import StatusModel


def run_app(argv: list[str] | None = None) -> int:
    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    status_model = StatusModel()
    engine.rootContext().setContextProperty("statusModel", status_model)
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()
```

- [ ] **Step 4: Run QML smoke test**

Run: `pytest tests/qml/test_qml_loads.py -v`

Expected: one passing test.

- [ ] **Step 5: Commit**

```bash
git add src/klippertouch/qml src/klippertouch/app.py tests/qml/test_qml_loads.py
git commit -m "feat: add read-only qml shell"
```

## Task 7: Read-Only Probe Command

**Files:**
- Modify: `src/klippertouch/__main__.py`
- Modify: `src/klippertouch/cli.py`
- Create: `src/klippertouch/probe.py`
- Create: `tests/unit/test_probe.py`

- [ ] **Step 1: Write failing probe test**

Create `tests/unit/test_probe.py`:

```python
from klippertouch.domain.printer import PrinterStatus
from klippertouch.probe import build_status_from_client


class FakeClient:
    def get_server_info(self):
        return {"moonraker_version": "v0.10.0", "klippy_state": "ready"}

    def get_printer_info(self):
        return {"hostname": "orangepi3b", "software_version": "v0.13.0", "state": "ready"}

    def get_objects_list(self):
        return {"objects": ["extruder", "heater_bed"]}


def test_build_status_from_client() -> None:
    status = build_status_from_client(FakeClient())
    assert isinstance(status, PrinterStatus)
    assert status.hostname == "orangepi3b"
    assert status.object_count == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_probe.py -v`

Expected: import failure for `klippertouch.probe`.

- [ ] **Step 3: Implement probe helper and CLI flag**

Create `src/klippertouch/probe.py`:

```python
from typing import Any, Protocol

from klippertouch.domain.printer import PrinterStatus


class ReadOnlyProbeClient(Protocol):
    def get_server_info(self) -> dict[str, Any]: ...
    def get_printer_info(self) -> dict[str, Any]: ...
    def get_objects_list(self) -> dict[str, Any]: ...


def build_status_from_client(client: ReadOnlyProbeClient) -> PrinterStatus:
    return PrinterStatus.from_probe(
        server_info=client.get_server_info(),
        printer_info=client.get_printer_info(),
        objects=client.get_objects_list(),
    )
```

Modify `src/klippertouch/cli.py`:

```python
from argparse import ArgumentParser, Namespace
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(prog="klippertouch")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--read-only", action="store_true", default=True)
    parser.add_argument("--probe", action="store_true", help="Run read-only Moonraker probe and exit")
    return parser.parse_args(argv)
```

Modify `src/klippertouch/__main__.py`:

```python
import json
import sys
from pathlib import Path

from klippertouch.app import run_app
from klippertouch.cli import parse_args
from klippertouch.config.loader import load_config
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.probe import build_status_from_client


def main() -> int:
    args = parse_args()
    config_path = args.config or Path.home() / "printer_data" / "config" / "KlipperTouch.conf"
    settings = load_config(config_path)

    if args.probe:
        printer = settings.printers[settings.default_printer]
        status = build_status_from_client(MoonrakerClient(printer))
        print(json.dumps(status.__dict__, ensure_ascii=False, indent=2))
        return 0

    if args.debug:
        print("Debug logging enabled")
    return run_app(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_probe.py tests/unit/test_cli.py -v`

Expected: `test_probe.py` passes, and `test_cli.py` fails because the default CLI test has not asserted the new `probe` field yet.

- [ ] **Step 5: Update CLI test for probe default**

Modify `tests/unit/test_cli.py`:

```python
from pathlib import Path

from klippertouch.cli import parse_args


def test_parse_args_defaults_to_read_only() -> None:
    args = parse_args([])
    assert args.read_only is True
    assert args.config is None
    assert args.debug is False
    assert args.probe is False


def test_parse_args_accepts_config_and_debug() -> None:
    args = parse_args(["--config", "/tmp/KlipperTouch.conf", "--debug"])
    assert args.config == Path("/tmp/KlipperTouch.conf")
    assert args.debug is True
```

- [ ] **Step 6: Run updated probe and CLI tests**

Run: `pytest tests/unit/test_probe.py tests/unit/test_cli.py -v`

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/klippertouch/__main__.py src/klippertouch/cli.py src/klippertouch/probe.py tests/unit/test_probe.py tests/unit/test_cli.py
git commit -m "feat: add read-only probe command"
```

## Task 8: Verification And Documentation Update

**Files:**
- Modify: `README.md`
- Modify: `docs/roadmap.md`

- [ ] **Step 1: Run full local verification**

Run:

```bash
pytest
ruff check src tests
mypy src/klippertouch
```

Expected: all commands pass.

- [ ] **Step 2: Run safe real-printer probe**

Create a local config file outside git, then run:

```bash
python -m klippertouch --config /tmp/KlipperTouch.conf --probe
```

Expected: JSON output containing `hostname`, `klippy_state`, `klipper_version`, `moonraker_version`, and `objects`. This command must only use `GET /server/info`, `GET /printer/info`, and `GET /printer/objects/list`.

- [ ] **Step 3: Update README with development commands**

Add this section to `README.md`:

```markdown
## Development Commands

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
ruff check src tests
mypy src/klippertouch
python -m klippertouch --probe
```

Real-printer probes are read-only. Do not enable command execution without a separate reviewed plan.
```

- [ ] **Step 4: Mark roadmap Phase 2 as implemented**

Update `docs/roadmap.md` Phase 2 status to `implemented skeleton` and Phase 3 status to `ready for read-only integration expansion`.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/roadmap.md
git commit -m "docs: add skeleton verification workflow"
```

## Self-Review

Spec coverage:

- The plan creates a clean PySide6/QML skeleton from the research-first spec.
- It preserves read-only mode as the default and adds explicit safety policy tests.
- It includes configuration compatibility for the `[main]` and `[printer ...]` subset.
- It adds a QML shell with disabled controls, matching the safety boundary.
- It adds a real-printer probe path that uses only read-only Moonraker endpoints.

Known deferred work:

- WebSocket subscriptions are deferred to a later Phase 3 expansion.
- KlipperScreen panel recreation is deferred until the shell and read-only state contracts are stable.
- State-changing controls remain out of scope.
