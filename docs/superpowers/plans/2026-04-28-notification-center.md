# Notification Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a global notification center with a status-bar badge, full-screen history page, and job/file command event ingestion.

**Architecture:** A Python `NotificationModel` owns notification history and unread state, exposed to QML as `notificationModel`. `StatusBar` displays an unread badge and emits a global open request, while `NotificationCenterPanel` renders the list and mark-read/clear controls. `main.qml` bridges command success/error events from `JobControlModel` into notifications.

**Tech Stack:** PySide6 `QAbstractListModel`, QML panels/components, pytest, qml source-load tests, ruff, mypy.

---

### Task 1: Notification Model

**Files:**
- Create: `src/klippertouch/qt_models/notification_model.py`
- Test: `tests/unit/qt_models/test_notification_model.py`

- [ ] Add tests for append, unread count, mark-all-read, clear, and max history trimming.
- [ ] Implement `NotificationModel` roles: `level`, `title`, `message`, `source`, `timestamp`, `read`, `sticky`, `actionPanel`.
- [ ] Expose slots: `addNotification`, `markAllRead`, `clear`.

### Task 2: Application Wiring

**Files:**
- Modify: `src/klippertouch/app.py`
- Test: `tests/unit/test_app_entry.py`

- [ ] Create the model during `run_app`.
- [ ] Expose it through `setContextProperty("notificationModel", notification_model)`.
- [ ] Store it on the engine for lifetime management.

### Task 3: Global QML Entry

**Files:**
- Modify: `src/klippertouch/qml/components/StatusBar.qml`
- Modify: `src/klippertouch/qml/components/BaseShell.qml`
- Modify: `src/klippertouch/qml/main.qml`
- Test: `tests/qml/test_qml_loads.py`

- [ ] Add `notificationUnreadCount` to `StatusBar` and show a compact badge near the clock.
- [ ] Add `notificationsRequested` signal to `BaseShell`.
- [ ] Add `notifications` panel title/icon and route it in `main.qml`.

### Task 4: Notification Center Page

**Files:**
- Create: `src/klippertouch/qml/panels/NotificationCenterPanel.qml`
- Modify: `src/klippertouch/qml/models/MoreMenuModel.qml`
- Test: `tests/qml/test_qml_loads.py`

- [ ] Render notification rows with level, title, message, source, and timestamp.
- [ ] Add `Mark read` and `Clear` actions using global back for navigation.
- [ ] Add a More-menu entry for secondary access.

### Task 5: Job/File Event Ingestion

**Files:**
- Modify: `src/klippertouch/qml/main.qml`
- Test: `tests/qml/test_qml_loads.py`

- [ ] Add `notify(level, title, message, source, sticky, actionPanel)` helper.
- [ ] Subscribe to `jobControlModel.statusChanged` and `errorChanged`.
- [ ] Send success events as non-sticky info notifications and failures as sticky error notifications.

### Task 6: Verification

**Files:**
- All touched files

- [ ] Run `.venv/bin/pytest -q`.
- [ ] Run `.venv/bin/ruff check src tests tools`.
- [ ] Run `.venv/bin/mypy src/klippertouch`.
- [ ] Commit with `feat: add notification center`.
