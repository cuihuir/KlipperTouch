# KlipperTouch 部署说明

本部署不改动原有的 `device-gui.service`，而是新增独立的 `klippertouch.service` 和 `klippertouch-eglfs.service`。这样可以保留原服务作为外部回退路径，也避免影响其它正在进行的主线开发会话。

## 目标目录

- 应用目录：`/home/tope/klippertouch`
- Python 虚拟环境：`/home/tope/klippertouch/venv`
- 应用配置：`/home/tope/printer_data/config/KlipperTouch.conf`
- X11 启动脚本：`/usr/local/bin/klippertouch-start.sh`
- X11 systemd 服务：`/etc/systemd/system/klippertouch.service`
- EGLFS 启动脚本：`/usr/local/bin/klippertouch-eglfs-start.sh`
- EGLFS systemd 服务：`/etc/systemd/system/klippertouch-eglfs.service`
- EGLFS KMS 配置：`/home/tope/printer_data/config/klippertouch-eglfs-kms.json`

## 系统依赖

系统依赖记录在 `deploy/system-packages.txt`。当前目标环境至少需要：

- `python3.11-venv`：创建运行虚拟环境
- `xinit`、`x11-xserver-utils`、`xserver-xorg`：X11 回退服务
- `libxcb-cursor0`：PySide6 `xcb` 平台插件运行依赖

从仓库 checkout 里安装或更新 systemd 资产：

```bash
sudo deploy/install-systemd.sh eglfs
```

该命令会安装 EGLFS 和 X11 两套服务文件、启用 EGLFS 服务、禁用 X11 服务、安装 KMS 配置。已有的 `KlipperTouch.conf` 默认不会被覆盖；只有设置 `KLIPPERTOUCH_OVERWRITE_CONFIG=1` 时才会重写配置。需要回退到 X11 服务时执行：

```bash
sudo deploy/install-systemd.sh x11
```

## X11 回退服务

`klippertouch.service` 采用类似 KlipperScreen 的 systemd 启动方式：systemd 启动 shell launcher，launcher 通过 `xinit` 启动 Xorg，然后在 X client 阶段旋转 HDMI 输出并启动 GUI。

目标屏幕在系统里上报为 `440x1920`，实际期望 GUI 方向是 `1920x440`，因此 X11 服务执行：

```bash
xrandr --output HDMI-1 --preferred --rotate right
```

GUI 启动命令为：

```bash
/home/tope/klippertouch/venv/bin/klippertouch \
  --config /home/tope/printer_data/config/KlipperTouch.conf \
  --allow-controls \
  --fullscreen
```

当前部署已经启用真实打印机控制模式。需要保证 `/home/tope/printer_data/config/KlipperTouch.conf` 中为：

```ini
read_only = false
```

或者保留服务命令里的显式参数：

```bash
--allow-controls
```

X11 服务默认使用 Qt Quick 软件渲染：

```ini
Environment=QT_QUICK_BACKEND=software
Environment=KLIPPERTOUCH_RENDER_BACKEND=software
```

这个路径稳定可用，但在 RK3566 目标硬件上 CPU 占用偏高，因此主要作为保守回退方案。

## EGLFS 硬件加速服务

`klippertouch-eglfs.service` 是 RK3566 目标环境上验证通过的生产服务。它使用 EGLFS/GBM 直接走 DRM/KMS，不启动 Xorg。它与 `klippertouch.service` 冲突，因为 EGLFS 需要直接占用 `/dev/dri/card0` 和显示输出，不能和 Xorg 同时拥有显示设备。

关键环境变量：

```ini
Environment=QT_QPA_PLATFORM=eglfs
Environment=QT_QPA_EGLFS_INTEGRATION=eglfs_kms
Environment=QT_QPA_EGLFS_KMS_CONFIG=/home/tope/printer_data/config/klippertouch-eglfs-kms.json
Environment=QSG_RHI_BACKEND=opengl
Environment=KLIPPERTOUCH_DISPLAY_ROTATION=right
```

KMS 配置位于 `deploy/klippertouch-eglfs-kms.json`，使用 `/dev/dri/card0`，并关闭硬件光标：

```json
{
  "device": "/dev/dri/card0",
  "hwcursor": false,
  "pbuffers": true
}
```

该路径已在 RK3566 + Mali-G52 目标环境验证通过。日志中能看到 HDMI 屏幕几何为 `440x1920`，并创建了 OpenGL ES 上下文：

```text
RENDERER: Mali-G52
```

Qt Quick 场景由 QML 自己旋转。原因是 `QT_QPA_EGLFS_ROTATION` 对 OpenGL/Qt Quick 场景不可靠，不能完整解决画面方向问题。

Qt scenegraph 和 KMS 详细日志默认关闭。只有排查渲染问题时，才在服务环境中临时设置 `QSG_INFO=1` 或 `QT_LOGGING_RULES`。

## 已遇到的问题和处理方案

- X11 软件渲染：界面稳定可显示，但 CPU 占用高。保留为回退方案。
- X11 `xcb_egl`：可以创建 Mali-G52 OpenGL 上下文，但目标机器出现灰屏，说明渲染结果没有可靠提交到 HDMI plane。该路径不作为默认方案。
- EGLFS/GBM：绕过 Xorg，直接 DRM/KMS 输出，Mali-G52 渲染正常，是当前验证通过的硬件加速方案。
- 屏幕方向：系统上报 `440x1920`，而 GUI 需要 `1920x440`。应用通过 `KLIPPERTOUCH_DISPLAY_ROTATION=right` 交换逻辑视口，并旋转 QML `sceneRoot`。
- 数字键盘方向和出屏：Qt Quick Controls `Popup` 可能走 window overlay 渲染路径，不能可靠继承 `sceneRoot` 的旋转，导致温度数字键盘方向错误、位置出屏。现在温度和挤出相关数字编辑器改为普通 `Item`/`Rectangle`，挂到 `sceneRoot` 内的全屏 `scenePopupLayer`，因此能跟随主界面旋转并保持在屏幕内。

## 当前运行状态

当前目标环境已验证：

- `klippertouch-eglfs.service` 可以启动并保持 `active`
- 进程参数为 `--allow-controls --fullscreen`
- 配置为 `read_only = false`
- OpenGL ES 渲染器为 Mali-G52
- 主界面方向正常
- 温度设置数字键盘方向和位置正常

## 控制验证清单

当前部署已经启用真实打印机控制模式，因此验收前需要在空闲或可控状态下验证每类命令：

- 设置一个低风险温度目标，确认 Moonraker 收到的是目标设备的预期温度目标。
- 只在轴已归零时验证运动控制，确认方向和距离正确。
- 只在挤出保护允许时验证挤出/回抽；禁止挤出时应显示错误，不应发送 G-code。
- 使用安全测试文件验证打印控制，包括选择文件、暂停、恢复、取消。
- 确认急停入口可达，并发送预期 Moonraker emergency stop 命令。
- 验证 Z offset、speed factor、extrusion factor 等调节项，最好使用空闲状态或一次可丢弃的验证任务。
- 临时断开或阻断 Moonraker 一次，确认 UI 能报告命令失败，且不会静默重试状态改变请求。

## 设为开机默认

当前 `klippertouch-eglfs.service` 已支持作为开机默认服务安装。最终验收后使用安装脚本切换：

```bash
sudo deploy/install-systemd.sh eglfs
```

回退到 X11 服务时执行：

```bash
sudo deploy/install-systemd.sh x11
```

切换开机默认后，还需要在操作者确认后做一次真实 reboot 验证，确认重启后 `klippertouch-eglfs.service` 能自动回到 `active`，不需要手动启动。
