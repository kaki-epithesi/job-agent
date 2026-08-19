import pytest

from job_agent.agents.source_discovery.connectors.workday import WorkdayConnector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, SourcePlatform


async def test_workday_connector_parses_postings(fake_http):
    payload = {
        "jobPostings": [
            {
                "title": "Software Engineer",
                "externalUrl": ("https://acme.wd1.myworkdayjobs.com/en-US/External/job/SWE_JR1"),
                "locationsText": "Bengaluru, India",
                "jobId": "JR-1",
            }
        ]
    }
    connector = WorkdayConnector(
        http=fake_http(payload),
        config={"host": "acme.wd1.myworkdayjobs.com", "tenant": "acme"},
    )
    docs = await connector.discover(DiscoveryRequest(source="workday:acme"))

    assert len(docs) == 1
    doc = docs[0]
    assert doc.platform == SourcePlatform.WORKDAY
    assert doc.source == "workday:acme"
    assert doc.title == "Software Engineer"
    assert doc.metadata["location"] == "Bengaluru, India"
    assert str(doc.url).startswith("https://acme.wd1")


async def test_workday_connector_requires_host_and_tenant(fake_http):
    connector = WorkdayConnector(http=fake_http({}), config={})

    with pytest.raises(DiscoveryError):
        await connector.discover(DiscoveryRequest(source="workday:x"))
