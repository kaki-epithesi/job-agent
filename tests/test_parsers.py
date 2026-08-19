import json

from job_agent.agents.job_extraction.parsers import get_parser
from job_agent.models import JobType, RawDocument, SourcePlatform, WorkMode


def make_doc(source: str, payload, platform=SourcePlatform.COMPANY_CAREERS) -> RawDocument:
    return RawDocument(
        platform=platform,
        source=source,
        url="https://example.com/jobs/1",
        raw_content=json.dumps(payload),
    )


def test_greenhouse_parser():
    parser = get_parser("greenhouse")
    job = parser.parse(
        make_doc(
            "greenhouse:databricks",
            {
                "title": "Software Engineer",
                "company_name": "Databricks",
                "location": {"name": "Tokyo, Japan"},
                "absolute_url": "https://databricks.com/jobs/1",
                "updated_at": "2026-01-01T00:00:00Z",
            },
            platform=SourcePlatform.GREENHOUSE,
        )
    )
    assert job is not None
    assert job.title == "Software Engineer"
    assert job.company == "Databricks"
    assert job.location == "Tokyo, Japan"
    assert str(job.apply_url) == "https://databricks.com/jobs/1"


def test_greenhouse_parser_falls_back_to_instance():
    parser = get_parser("greenhouse")
    job = parser.parse(
        make_doc(
            "greenhouse:databricks",
            {"title": "Software Engineer"},
            platform=SourcePlatform.GREENHOUSE,
        )
    )
    assert job is not None
    assert job.company == "databricks"


def test_lever_parser():
    parser = get_parser("lever")
    job = parser.parse(
        make_doc(
            "lever:palantir",
            {
                "text": "Backend Engineer",
                "hostedUrl": "https://jobs.lever.co/palantir/1",
                "applyUrl": "https://jobs.lever.co/palantir/1/apply",
                "categories": {"location": "Remote", "commitment": "Full-time"},
                "workplaceType": "Remote",
            },
            platform=SourcePlatform.LEVER,
        )
    )
    assert job is not None
    assert job.title == "Backend Engineer"
    assert job.company == "palantir"
    assert job.job_type == JobType.FULL_TIME
    assert job.work_mode == WorkMode.REMOTE
    assert str(job.apply_url) == "https://jobs.lever.co/palantir/1/apply"


def test_ashby_parser():
    parser = get_parser("ashby")
    job = parser.parse(
        make_doc(
            "ashby:openai",
            {
                "title": "SWE",
                "jobUrl": "https://jobs.ashbyhq.com/openai/abc",
                "applyUrl": "https://jobs.ashbyhq.com/openai/abc/application",
                "location": "San Francisco",
                "employmentType": "FullTime",
                "workplaceType": "Remote",
                "publishedAt": "2026-03-12T16:38:15.322+00:00",
            },
            platform=SourcePlatform.ASHBY,
        )
    )
    assert job is not None
    assert job.title == "SWE"
    assert job.job_type == JobType.FULL_TIME
    assert job.work_mode == WorkMode.REMOTE
    assert job.location == "San Francisco"


def test_amazon_parser():
    parser = get_parser("amazon")
    job = parser.parse(
        make_doc(
            "amazon",
            {
                "title": "SDE",
                "normalized_location": "US, WA, Seattle",
                "url_next_step": "https://account.amazon.jobs/jobs/1/apply",
                "posted_date": "August  6, 2026",
            },
        )
    )
    assert job is not None
    assert job.title == "SDE"
    assert job.company == "Amazon"
    assert job.location == "US, WA, Seattle"
    assert job.posted_at is not None and job.posted_at.month == 8


def test_parser_returns_none_on_invalid_content():
    parser = get_parser("greenhouse")
    doc = RawDocument(
        platform=SourcePlatform.GREENHOUSE,
        source="greenhouse:databricks",
        url="https://example.com/jobs/1",
        raw_content="not-json",
    )
    assert parser.parse(doc) is None


def test_get_parser_unknown_returns_none():
    assert get_parser("linkedin") is None
    assert get_parser("does-not-exist") is None
