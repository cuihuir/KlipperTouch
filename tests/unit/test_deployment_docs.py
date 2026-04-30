from pathlib import Path


def test_deployment_docs_prefer_direct_venv_launcher() -> None:
    docs = Path("docs/deployment.md").read_text(encoding="utf-8")

    assert ".venv/bin/klippertouch" in docs
    assert "uv run" not in docs.partition("## Production Launch")[2]
    assert "UV_INDEX_URL=https://pypi.org/simple uv sync --locked" in docs


def test_systemd_example_uses_direct_console_script() -> None:
    service = Path("deploy/systemd/klippertouch.service.example").read_text(
        encoding="utf-8"
    )

    assert "ExecStart=/home/orangepi/KlipperTouch/.venv/bin/klippertouch" in service
    assert "uv run" not in service
    assert "--config /home/orangepi/printer_data/config/KlipperTouch.conf" in service
