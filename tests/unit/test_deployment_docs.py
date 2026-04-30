from pathlib import Path


def test_deployment_docs_prefer_direct_venv_launcher() -> None:
    docs = Path("docs/deployment.md").read_text(encoding="utf-8")

    assert ".venv/bin/klippertouch" in docs
    assert "uv run" not in docs.partition("## Production Launch")[2]
    assert "UV_INDEX_URL=https://pypi.org/simple uv sync --locked" in docs
    assert "deploy/install-systemd.sh eglfs" in docs
    assert "deploy/install-systemd.sh x11" in docs


def test_stale_wayland_systemd_example_is_removed() -> None:
    assert not Path("deploy/systemd/klippertouch.service.example").exists()


def test_deployment_docs_include_control_validation_checklist() -> None:
    docs = Path("docs/deployment.md").read_text(encoding="utf-8")
    docs_cn = Path("docs/deployment_cn.md").read_text(encoding="utf-8")

    for content in (docs, docs_cn):
        assert "Control Validation Checklist" in content or "控制验证清单" in content
        assert "temperature target" in content or "温度目标" in content
        assert "motion" in content or "运动" in content
        assert "extrusion" in content or "挤出" in content
        assert "print control" in content or "打印控制" in content
        assert "emergency stop" in content or "急停" in content
        assert "Z offset" in content or "Z offset" in content
