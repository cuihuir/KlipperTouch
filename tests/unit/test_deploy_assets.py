import os
import subprocess
from pathlib import Path


def test_klippertouch_service_is_independent_systemd_unit() -> None:
    service = Path("deploy/klippertouch.service").read_text(encoding="utf-8")

    assert "Description=KlipperTouch Touchscreen GUI" in service
    assert "User=tope" in service
    assert "ExecStart=/usr/local/bin/klippertouch-start.sh" in service
    assert "Environment=QT_QPA_PLATFORM=xcb" in service
    assert "Environment=QT_QUICK_BACKEND=software" in service
    assert "Environment=KLIPPERTOUCH_RENDER_BACKEND=software" in service
    assert "Environment=QT_XCB_GL_INTEGRATION=xcb_egl" not in service
    assert "Environment=QSG_RHI_BACKEND=opengl" not in service
    assert "Environment=QSG_INFO=1" not in service
    assert "Environment=KLIPPERTOUCH_DISPLAY=:0" in service
    assert "Environment=KLIPPERTOUCH_OUTPUT=HDMI-1" in service
    assert "Environment=KLIPPERTOUCH_ROTATE=right" in service
    assert "Environment=KLIPPERTOUCH_LOG=/home/tope/printer_data/logs/klippertouch.log" in service
    assert "--config /home/tope/printer_data/config/KlipperTouch.conf" in service
    assert "--debug" not in service
    assert "--read-only" not in service
    assert "--allow-controls" in service
    assert "--fullscreen" in service
    assert "device-gui.service" not in service


def test_klippertouch_start_script_uses_xinit_and_xrandr_rotation() -> None:
    script_path = Path("deploy/klippertouch-start.sh")
    script = script_path.read_text(encoding="utf-8")

    subprocess.run(["bash", "-n", str(script_path)], check=True)
    assert os.access(script_path, os.X_OK)
    assert 'exec /usr/bin/xinit "$0" --xclient -- "$display"' in script
    assert 'xrandr --output "$output" --preferred --rotate "$rotation"' in script
    assert "xset s off -dpms" in script
    assert "KLIPPERTOUCH_RESET_OUTPUT" in script
    assert "KLIPPERTOUCH_TOUCH_HID_PATTERN" in script
    assert "KLIPPERTOUCH_LOG" in script
    assert 'export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"' in script
    assert 'export QT_QUICK_BACKEND="${QT_QUICK_BACKEND:-software}"' in script
    assert 'unset QT_XCB_GL_INTEGRATION' in script
    assert 'unset QSG_RHI_BACKEND' in script
    assert 'export QSG_INFO="${QSG_INFO:-0}"' in script
    assert "--debug" not in script
    assert "--read-only" not in script
    assert "--allow-controls" in script
    assert 'exec /bin/bash -c "$xclient" >> "$log_file" 2>&1' in script


def test_klippertouch_eglfs_service_is_boot_default_capable() -> None:
    service = Path("deploy/klippertouch-eglfs.service").read_text(encoding="utf-8")

    assert "Description=KlipperTouch EGLFS Touchscreen GUI" in service
    assert "Experiment" not in service
    assert "User=tope" in service
    assert "Conflicts=klippertouch.service" in service
    assert "ExecStart=/usr/local/bin/klippertouch-eglfs-start.sh" in service
    assert "Restart=always" in service
    assert "RestartSec=2" in service
    assert "Environment=QT_QPA_PLATFORM=eglfs" in service
    assert "Environment=QT_QPA_EGLFS_INTEGRATION=eglfs_kms" in service
    assert (
        "Environment=QT_QPA_EGLFS_KMS_CONFIG="
        "/home/tope/printer_data/config/klippertouch-eglfs-kms.json"
    ) in service
    assert "Environment=QSG_RHI_BACKEND=opengl" in service
    assert "Environment=QSG_INFO=1" not in service
    assert "QT_LOGGING_RULES" not in service
    assert "--debug" not in service
    assert "--read-only" not in service
    assert "--allow-controls" in service
    assert "--fullscreen" in service
    assert "[Install]" in service
    assert "WantedBy=multi-user.target" in service
    assert "xinit" not in service
    assert "xrandr" not in service


def test_klippertouch_eglfs_start_script_runs_without_xorg() -> None:
    script_path = Path("deploy/klippertouch-eglfs-start.sh")
    script = script_path.read_text(encoding="utf-8")

    subprocess.run(["bash", "-n", str(script_path)], check=True)
    assert os.access(script_path, os.X_OK)
    assert "xinit" not in script
    assert "xrandr" not in script
    assert 'export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-eglfs}"' in script
    assert 'export QT_QPA_EGLFS_INTEGRATION="${QT_QPA_EGLFS_INTEGRATION:-eglfs_kms}"' in script
    assert 'export QSG_RHI_BACKEND="${QSG_RHI_BACKEND:-opengl}"' in script
    assert 'export QSG_INFO="${QSG_INFO:-0}"' in script
    assert "QT_LOGGING_RULES" not in script
    assert "--debug" not in script
    assert "--read-only" not in script
    assert "--allow-controls" in script
    assert 'exec /bin/bash -c "$eglfs_client" >> "$log_file" 2>&1' in script


def test_klippertouch_eglfs_kms_config_targets_rockchip_drm() -> None:
    config = Path("deploy/klippertouch-eglfs-kms.json").read_text(encoding="utf-8")

    assert '"/dev/dri/card0"' in config
    assert '"hwcursor": false' in config
    assert '"mode": "preferred"' in config


def test_deployment_config_enables_real_printer_controls() -> None:
    config = Path("deploy/KlipperTouch.conf").read_text(encoding="utf-8")

    assert "[main]" in config
    assert "read_only = false" in config
    assert "[printer LocalPrinter]" in config
    assert "moonraker_host = 127.0.0.1" in config
    assert "moonraker_port = 7125" in config


def test_deployment_system_packages_include_qt_xcb_runtime_deps() -> None:
    packages = Path("deploy/system-packages.txt").read_text(encoding="utf-8").splitlines()

    assert "python3.11-venv" in packages
    assert "xinit" in packages
    assert "x11-xserver-utils" in packages
    assert "libxcb-cursor0" in packages


def test_systemd_installer_switches_between_eglfs_and_x11_modes() -> None:
    script_path = Path("deploy/install-systemd.sh")
    script = script_path.read_text(encoding="utf-8")

    subprocess.run(["bash", "-n", str(script_path)], check=True)
    assert os.access(script_path, os.X_OK)
    assert 'mode="${1:-eglfs}"' in script
    assert 'install -m 0755 "$asset_dir/klippertouch-start.sh"' in script
    assert 'install -m 0755 "$asset_dir/klippertouch-eglfs-start.sh"' in script
    assert 'install -m 0644 "$asset_dir/klippertouch.service"' in script
    assert 'install -m 0644 "$asset_dir/klippertouch-eglfs.service"' in script
    assert 'install -m 0644 "$asset_dir/klippertouch-eglfs-kms.json"' in script
    assert "systemctl daemon-reload" in script
    assert "systemctl disable klippertouch.service" in script
    assert "systemctl enable klippertouch-eglfs.service" in script
    assert "systemctl disable klippertouch-eglfs.service" in script
    assert "systemctl enable klippertouch.service" in script
    assert "KLIPPERTOUCH_OVERWRITE_CONFIG" in script
    assert "KLIPPERTOUCH_START_AFTER_INSTALL" in script
