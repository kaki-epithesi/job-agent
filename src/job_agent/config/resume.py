"""Resume loading."""

from importlib.resources import files
from pathlib import Path

import yaml

from job_agent.config import settings
from job_agent.models import Resume


def load_resume(path: Path | None = None) -> Resume:
    """Load the resume from ``path``, the configured file, or the bundled default."""
    raw = _read_raw(path)
    data = yaml.safe_load(raw) or {}
    return Resume.model_validate(data)


def _read_raw(path: Path | None) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")

    if settings.resume_file:
        return Path(settings.resume_file).read_text(encoding="utf-8")

    resource = files("job_agent.config").joinpath("resume.yaml")
    return resource.read_text(encoding="utf-8")
