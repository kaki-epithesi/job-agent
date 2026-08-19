from job_agent.agents.source_discovery import SourceDiscoveryAgent
from job_agent.config.sources import SourceConfig
from job_agent.repositories import SqliteRawDocumentRepository

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


def greenhouse_source() -> SourceConfig:
    return SourceConfig(
        id="greenhouse:databricks",
        type="greenhouse",
        enabled=True,
        config={"board": "databricks"},
    )


async def test_agent_discovers_and_persists(database, fake_http):
    agent = SourceDiscoveryAgent(
        http=fake_http(GH_JOBS),
        repository=SqliteRawDocumentRepository(database),
    )
    documents = await agent.run([greenhouse_source()])

    assert len(documents) == 1
    assert await SqliteRawDocumentRepository(database).count() == 1


async def test_agent_deduplicates_across_sources(database, fake_http):
    agent = SourceDiscoveryAgent(
        http=fake_http(GH_JOBS),
        repository=SqliteRawDocumentRepository(database),
    )
    documents = await agent.run([greenhouse_source(), greenhouse_source()])

    assert len(documents) == 1


async def test_agent_tolerates_failing_source(database, fake_http):
    agent = SourceDiscoveryAgent(
        http=fake_http(GH_JOBS),
        repository=SqliteRawDocumentRepository(database),
    )
    sources = [
        greenhouse_source(),
        SourceConfig(id="bad", type="does-not-exist", enabled=True),
    ]
    documents = await agent.run(sources)

    assert len(documents) == 1
    assert await SqliteRawDocumentRepository(database).count() == 1


async def test_agent_filters_by_location(database, fake_http):
    payload = {
        "jobs": [
            {
                "id": 1,
                "title": "SWE",
                "absolute_url": "https://x.example/1",
                "location": {"name": "Bengaluru, India"},
            },
            {
                "id": 2,
                "title": "SWE",
                "absolute_url": "https://x.example/2",
                "location": {"name": "San Francisco, USA"},
            },
        ]
    }
    agent = SourceDiscoveryAgent(
        http=fake_http(payload),
        repository=SqliteRawDocumentRepository(database),
        locations=["india"],
    )
    documents = await agent.run([greenhouse_source()])

    assert len(documents) == 1
    assert "Bengaluru" in documents[0].metadata["location"]


async def test_agent_no_location_filter_keeps_all(database, fake_http):
    payload = {
        "jobs": [
            {
                "id": 1,
                "title": "SWE",
                "absolute_url": "https://x.example/1",
                "location": {"name": "Bengaluru, India"},
            },
            {
                "id": 2,
                "title": "SWE",
                "absolute_url": "https://x.example/2",
                "location": {"name": "San Francisco, USA"},
            },
        ]
    }
    agent = SourceDiscoveryAgent(
        http=fake_http(payload),
        repository=SqliteRawDocumentRepository(database),
    )
    documents = await agent.run([greenhouse_source()])

    assert len(documents) == 2
