"""Notification configuration loading."""

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ChannelConfig(BaseModel):
    """A single notification channel."""

    type: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class NotificationsConfig(BaseModel):
    """Top-level notification configuration."""

    channels: list[ChannelConfig] = Field(default_factory=list)


def load_notifications(path: Path | None = None) -> NotificationsConfig:
    """Load notification config from ``path`` or the bundled default."""
    raw = _read_raw(path)
    data = yaml.safe_load(raw) or {}
    return NotificationsConfig.model_validate(data)


def _read_raw(path: Path | None) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")

    resource = files("job_agent.config").joinpath("notifications.yaml")
    return resource.read_text(encoding="utf-8")
