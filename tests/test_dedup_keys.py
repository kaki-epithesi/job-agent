from job_agent.agents.deduplication.keys import dedup_key, normalize
from job_agent.models import Job


def make_job(company="Acme", title="Software Engineer", location="San Francisco, CA"):
    return Job(title=title, company=company, location=location)


def test_normalize():
    assert normalize("  San Francisco, CA ") == "san francisco ca"
    assert normalize(None) == ""
    assert normalize("Software-Engineer!") == "software engineer"


def test_dedup_key_normalizes():
    a = make_job(company="Acme Corp.", title="Software Engineer", location="San Francisco, CA")
    b = make_job(company="acme corp", title="software engineer", location="san francisco ca")
    assert dedup_key(a) == dedup_key(b)


def test_dedup_key_differs_by_location():
    assert dedup_key(make_job(location="San Francisco, CA")) != dedup_key(
        make_job(location="New York, NY")
    )


def test_dedup_key_differs_by_title():
    assert dedup_key(make_job(title="Software Engineer")) != dedup_key(
        make_job(title="Senior Software Engineer")
    )
