from pathlib import Path

from job_agent.config.notifications import load_notifications


def test_load_from_file(tmp_path: Path):
    path = tmp_path / "notifications.yaml"
    path.write_text(
        "channels:\n  - type: console\n    enabled: true\n",
        encoding="utf-8",
    )

    config = load_notifications(path)

    assert len(config.channels) == 1
    assert config.channels[0].type == "console"
    assert config.channels[0].enabled is True


def test_load_default_has_console():
    config = load_notifications()
    assert any(c.type == "console" and c.enabled for c in config.channels)
