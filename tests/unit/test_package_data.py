import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import tomllib


def test_qml_package_data_is_explicitly_declared() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    wheel_config = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]

    assert "src/klippertouch/qml/**/*" in wheel_config["artifacts"]


def test_built_wheel_contains_qml_package_data(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    assert uv is not None

    env = os.environ.copy()
    env["UV_INDEX_URL"] = "https://pypi.org/simple"

    subprocess.run(
        [uv, "build", "--out-dir", str(tmp_path)],
        check=True,
        env=env,
        text=True,
        capture_output=True,
    )

    wheel = next(tmp_path.glob("klippertouch-*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    assert "klippertouch/qml/main.qml" in names
    assert "klippertouch/qml/Theme.js" in names
    assert "klippertouch/qml/models/MainMenuModel.qml" in names
    assert "klippertouch/qml/models/TemperatureDeviceModel.qml" in names
    assert "klippertouch/qml/assets/material-dark/images/printer.svg" in names
