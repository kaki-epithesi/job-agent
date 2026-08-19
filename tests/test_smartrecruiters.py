import json

from job_agent.agents.job_extraction.parsers import get_parser
from job_agent.agents.source_discovery.connectors.smartrecruiters import (
    SmartRecruitersConnector,
)
from job_agent.models import (
    DiscoveryRequest,
    JobType,
    RawDocument,
    SourcePlatform,
    WorkMode,
)

POSTING = {
    "id": "123",
    "name": "Software Engineer",
    "company": {"name": "Freshworks"},
    "location": {
        "city": "Bengaluru",
        "fullLocation": "Bengaluru, Karnataka, India",
        "remote": False,
        "hybrid": True,
    },
    "typeOfEmployment": {"label": "Full-time"},
    "releasedDate": "2026-08-19T11:53:03.107Z",
}

POSTINGS = {"totalFound": 1, "content": [POSTING]}


async def test_smartrecruiters_connector(fake_http):
    connector = SmartRecruitersConnector(
        http=fake_http(POSTINGS),
        config={"company": "freshworks"},
    )
    docs = await connector.discover(DiscoveryRequest(source="smartrecruiters:freshworks"))

    assert len(docs) == 1
    doc = docs[0]
    assert doc.platform == SourcePlatform.SMARTRECRUITERS
    assert doc.title == "Software Engineer"
    assert doc.metadata["location"] == "Bengaluru, Karnataka, India"
    assert str(doc.url).startswith("https://jobs.smartrecruiters.com/freshworks/")


def test_smartrecruiters_parser():
    doc = RawDocument(
        platform=SourcePlatform.SMARTRECRUITERS,
        source="smartrecruiters:freshworks",
        url="https://jobs.smartrecruiters.com/freshworks/123",
        raw_content=json.dumps(POSTING),
    )
    job = get_parser("smartrecruiters").parse(doc)

    assert job is not None
    assert job.title == "Software Engineer"
    assert job.company == "Freshworks"
    assert job.location == "Bengaluru, Karnataka, India"
    assert job.job_type == JobType.FULL_TIME
    assert job.work_mode == WorkMode.HYBRID
