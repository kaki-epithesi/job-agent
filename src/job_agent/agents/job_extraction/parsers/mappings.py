"""Shared mapping helpers for job parsers."""

from datetime import UTC, datetime

from job_agent.models import JobType, WorkMode

_JOB_TYPE_MAP: dict[str, JobType] = {
    "fulltime": JobType.FULL_TIME,
    "full_time": JobType.FULL_TIME,
    "full-time": JobType.FULL_TIME,
    "parttime": JobType.PART_TIME,
    "part_time": JobType.PART_TIME,
    "part-time": JobType.PART_TIME,
    "internship": JobType.INTERNSHIP,
    "contract": JobType.CONTRACT,
    "contractor": JobType.CONTRACT,
    "temporary": JobType.TEMPORARY,
    "freelance": JobType.FREELANCE,
    "apprenticeship": JobType.APPRENTICESHIP,
}

_WORK_MODE_MAP: dict[str, WorkMode] = {
    "remote": WorkMode.REMOTE,
    "hybrid": WorkMode.HYBRID,
    "onsite": WorkMode.ONSITE,
    "on-site": WorkMode.ONSITE,
    "on_site": WorkMode.ONSITE,
    "in-person": WorkMode.ONSITE,
    "in_person": WorkMode.ONSITE,
}

_DATETIME_FORMATS = [
    "%B %d, %Y",
    "%b %d, %Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
]


def map_job_type(value: str | None) -> JobType:
    if not value:
        return JobType.UNKNOWN
    return _JOB_TYPE_MAP.get(value.strip().lower(), JobType.UNKNOWN)


def map_work_mode(value: str | None) -> WorkMode:
    if not value:
        return WorkMode.UNKNOWN
    return _WORK_MODE_MAP.get(value.strip().lower(), WorkMode.UNKNOWN)


def parse_datetime(value) -> datetime | None:
    """Leniently parse a datetime, returning None on failure.

    Accepts ISO-8601 strings, common date strings, and numeric epoch values
    (seconds or milliseconds).
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        epoch = value / 1000 if value > 1e12 else value
        return datetime.fromtimestamp(epoch, tz=UTC)

    if not isinstance(value, str):
        return None

    value = " ".join(value.split())

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass

    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None
