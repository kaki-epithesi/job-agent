from job_agent.agents.job_extraction.parsers.mappings import (
    map_job_type,
    map_work_mode,
    parse_datetime,
)
from job_agent.models import JobType, WorkMode


def test_parse_datetime_iso_offset():
    parsed = parse_datetime("2026-03-12T16:38:15.322+00:00")
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 3


def test_parse_datetime_z_suffix():
    assert parse_datetime("2026-01-01T00:00:00Z") is not None


def test_parse_datetime_amazon_format():
    parsed = parse_datetime("August  6, 2026")
    assert parsed is not None
    assert parsed.month == 8
    assert parsed.day == 6


def test_parse_datetime_invalid():
    assert parse_datetime(None) is None
    assert parse_datetime("") is None
    assert parse_datetime("not a date") is None


def test_parse_datetime_epoch_milliseconds():
    # Lever createdAt: 1735830000000 -> 2025-01-02T15:00:00Z
    parsed = parse_datetime(1735830000000)
    assert parsed is not None
    assert parsed.year == 2025


def test_parse_datetime_epoch_seconds():
    parsed = parse_datetime(1735830000)
    assert parsed is not None
    assert parsed.year == 2025


def test_map_job_type():
    assert map_job_type("FullTime") == JobType.FULL_TIME
    assert map_job_type("full-time") == JobType.FULL_TIME
    assert map_job_type("Internship") == JobType.INTERNSHIP
    assert map_job_type(None) == JobType.UNKNOWN
    assert map_job_type("weird") == JobType.UNKNOWN


def test_map_work_mode():
    assert map_work_mode("Remote") == WorkMode.REMOTE
    assert map_work_mode("hybrid") == WorkMode.HYBRID
    assert map_work_mode("Onsite") == WorkMode.ONSITE
    assert map_work_mode("in-person") == WorkMode.ONSITE
    assert map_work_mode(None) == WorkMode.UNKNOWN
