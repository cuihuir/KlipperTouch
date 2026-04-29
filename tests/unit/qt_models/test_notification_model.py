from klippertouch.qt_models.notification_model import NotificationModel


def test_notification_model_adds_unread_notification(qtbot) -> None:
    model = NotificationModel()
    unread_counts: list[int] = []
    model.unreadCountChanged.connect(lambda: unread_counts.append(model.unreadCount))

    model.addNotification(
        "error",
        "Delete failed",
        "Moonraker refused delete",
        "files",
        True,
        "print",
    )

    assert model.rowCount() == 1
    assert model.count == 1
    assert model.unreadCount == 1
    assert unread_counts == [1]
    index = model.index(0, 0)
    assert model.data(index, model.LevelRole) == "error"
    assert model.data(index, model.TitleRole) == "Delete failed"
    assert model.data(index, model.MessageRole) == "Moonraker refused delete"
    assert model.data(index, model.SourceRole) == "files"
    assert model.data(index, model.ReadRole) is False
    assert model.data(index, model.StickyRole) is True
    assert model.data(index, model.ActionPanelRole) == "print"


def test_notification_model_marks_all_read_and_clears(qtbot) -> None:
    model = NotificationModel()
    model.addNotification("info", "Print sent", "cube.gcode", "job", False, "job_status")
    model.addNotification("error", "Cancel failed", "bad state", "job", True, "job_status")

    model.markAllRead()

    assert model.unreadCount == 0
    assert model.data(model.index(0, 0), model.ReadRole) is True
    assert model.data(model.index(1, 0), model.ReadRole) is True

    model.clear()

    assert model.rowCount() == 0
    assert model.count == 0
    assert model.unreadCount == 0


def test_notification_model_trims_old_history(qtbot) -> None:
    model = NotificationModel(max_items=2)

    model.addNotification("info", "one", "", "", False, "")
    model.addNotification("info", "two", "", "", False, "")
    model.addNotification("info", "three", "", "", False, "")

    assert model.rowCount() == 2
    assert model.data(model.index(0, 0), model.TitleRole) == "three"
    assert model.data(model.index(1, 0), model.TitleRole) == "two"
    assert model.unreadCount == 2


def test_notification_model_adds_moonraker_warnings_as_sticky_items(qtbot) -> None:
    model = NotificationModel()

    model.addMoonrakerWarnings(
        [
            "[update_manager]: Failed to load extension fluidd",
            "[update_manager]: Failed to load extension fluidd",
            "MCU 'cartographer' has deprecated code",
            "",
        ]
    )

    assert model.rowCount() == 2
    assert model.unreadCount == 2
    newest = model.index(0, 0)
    older = model.index(1, 0)
    assert model.data(newest, model.LevelRole) == "warning"
    assert model.data(newest, model.TitleRole) == "Moonraker warning"
    assert model.data(newest, model.MessageRole) == "MCU 'cartographer' has deprecated code"
    assert model.data(newest, model.SourceRole) == "moonraker"
    assert model.data(newest, model.StickyRole) is True
    assert (
        model.data(older, model.MessageRole)
        == "[update_manager]: Failed to load extension fluidd"
    )


def test_notification_model_requests_transient_toast_without_history(qtbot) -> None:
    model = NotificationModel()
    toasts: list[tuple[str, str, str]] = []
    model.toastRequested.connect(
        lambda level, title, message: toasts.append((level, title, message))
    )

    model.showToast("info", "Printer message", "M118 filament runout soon")

    assert toasts == [("info", "Printer message", "M118 filament runout soon")]
    assert model.rowCount() == 0
    assert model.unreadCount == 0
