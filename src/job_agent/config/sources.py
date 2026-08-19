"""Source configuration loading.

Source connectors are declared in a YAML file. Each entry maps a connector
``type`` (see ``job_agent.agents.source_discovery.connectors``) to a concrete
instance ``id`` and its connection ``config``.
"""

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from job_agent.config import settings


class SourceConfig(BaseModel):
    """A single configured source instance."""

    id: str
    type: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class SourcesConfig(BaseModel):
    """Top-level sources configuration."""

    sources: list[SourceConfig] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)


def load_sources(path: Path | None = None) -> SourcesConfig:
    """Load source configuration from ``path``, the configured file, or bundled."""
    raw = _read_raw(path)
    data = yaml.safe_load(raw) or {}
    return SourcesConfig.model_validate(data)


def _read_raw(path: Path | None) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")

    if settings.sources_file:
        return Path(settings.sources_file).read_text(encoding="utf-8")

    resource = files("job_agent.config").joinpath("sources.yaml")
    return resource.read_text(encoding="utf-8")
