from job_agent.agents.source_discovery.connectors.amazon import AmazonConnector
from job_agent.agents.source_discovery.connectors.ashby import AshbyConnector
from job_agent.agents.source_discovery.connectors.greenhouse import (
    GreenhouseConnector,
)
from job_agent.agents.source_discovery.connectors.lever import LeverConnector
from job_agent.models import DiscoveryRequest, SourcePlatform

GH_JOBS = {
    "jobs": [
        {
            "id": 1,
            "title": "Software Engineer",
            "absolute_url": "https://databricks.com/jobs/1",
            "location": {"name": "Tokyo, Japan"},
            "updated_at": "2026-01-01T00:00:00Z",
        }
    ]
}

LEVER_POSTINGS = [
    {
        "id": "1",
        "text": "Backend Engineer",
        "hostedUrl": "https://jobs.lever.co/palantir/1",
        "applyUrl": "https://jobs.lever.co/palantir/1/apply",
        "categories": {"location": "Remote", "team": "Eng", "commitment": "Full-time"},
    }
]

ASHBY_JOBS = {
    "jobs": [
        {
            "id": "abc",
            "title": "SWE",
            "jobUrl": "https://jobs.ashbyhq.com/openai/abc",
            "applyUrl": "https://jobs.ashbyhq.com/openai/abc/application",
            "location": "San Francisco",
            "department": "Engineering",
            "team": "Core",
            "employmentType": "FullTime",
            "workplaceType": "Remote",
            "publishedAt": "2026-03-12T16:38:15Z",
        }
    ]
}

AMAZON_JOBS = {
    "jobs": [
        {
            "title": "SDE",
            "job_path": "/en/jobs/1/sde",
            "url_next_step": "https://account.amazon.jobs/jobs/1/apply",
            "id_icims": 1,
            "normalized_location": "US, WA, Seattle",
            "posted_date": "Aug 6, 2026",
            "job_category": "Software",
        }
    ]
}


async def test_greenhouse_connector(fake_http):
    connector = GreenhouseConnector(
        http=fake_http(GH_JOBS),
        config={"board": "databricks"},
    )
    docs = await connector.discover(DiscoveryRequest(source="greenhouse:databricks"))

    assert len(docs) == 1
    doc = docs[0]
    assert doc.platform == SourcePlatform.GREENHOUSE
    assert doc.source == "greenhouse:databricks"
    assert str(doc.url) == "https://databricks.com/jobs/1"
    assert doc.title == "Software Engineer"
    assert doc.metadata["location"] == "Tokyo, Japan"
    assert doc.raw_content is not None


async def test_lever_connector(fake_http):
    connector = LeverConnector(
        http=fake_http(LEVER_POSTINGS),
        config={"company": "palantir"},
    )
    docs = await connector.discover(DiscoveryRequest(source="lever:palantir"))

    assert len(docs) == 1
    doc = docs[0]
    assert doc.platform == SourcePlatform.LEVER
    assert doc.title == "Backend Engineer"
    assert doc.metadata["location"] == "Remote"
    assert doc.metadata["apply_url"] == "https://jobs.lever.co/palantir/1/apply"


async def test_ashby_connector(fake_http):
    connector = AshbyConnector(
        http=fake_http(ASHBY_JOBS),
        config={"board": "openai"},
    )
    docs = await connector.discover(DiscoveryRequest(source="ashby:openai"))

    assert len(docs) == 1
    doc = docs[0]
    assert doc.platform == SourcePlatform.ASHBY
    assert str(doc.url) == "https://jobs.ashbyhq.com/openai/abc"
    assert doc.metadata["employment_type"] == "FullTime"


async def test_amazon_connector(fake_http):
    connector = AmazonConnector(
        http=fake_http(AMAZON_JOBS),
        config={"query": "software engineer"},
    )
    docs = await connector.discover(DiscoveryRequest(source="amazon"))

    assert len(docs) == 1
    doc = docs[0]
    assert doc.source == "amazon"
    assert str(doc.url) == "https://www.amazon.jobs/en/jobs/1/sde"
    assert doc.title == "SDE"
