from datetime import datetime

from pydantic import BaseModel, HttpUrl

from job_agent.models.enums import (
    ExperienceLevel,
    JobStatus,
    JobType,
    SourcePlatform,
    WorkMode,
)


class Job(BaseModel):
    """Structured job extracted from a raw document (Agent 2 output)."""

    title: str
    company: str

    location: str | None = None
    description: str | None = None
    apply_url: HttpUrl | None = None

    job_type: JobType = JobType.UNKNOWN
    work_mode: WorkMode = WorkMode.UNKNOWN
    experience_level: ExperienceLevel = ExperienceLevel.UNKNOWN

    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None

    posted_at: datetime | None = None
    source: str | None = None
    platform: SourcePlatform | None = None
    status: JobStatus = JobStatus.DISCOVERED
    raw_url: HttpUrl | None = None
    id: int | None = None
