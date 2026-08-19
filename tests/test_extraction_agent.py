import json

from job_agent.agents.job_extraction import JobExtractionAgent
from job_agent.models import RawDocument, SourcePlatform
from job_agent.repositories import (
    SqliteJobRepository,
    SqliteRawDocumentRepository,
)


def greenhouse_doc() -> RawDocument:
    return RawDocument(
        platform=SourcePlatform.GREENHOUSE,
        source="greenhouse:databricks",
        url="https://databricks.com/jobs/1",
        raw_content=json.dumps(
            {
                "title": "Software Engineer",
                "company_name": "Databricks",
                "location": {"name": "Tokyo, Japan"},
                "absolute_url": "https://databricks.com/jobs/1",
            }
        ),
    )


async def test_extract_end_to_end(database):
    raw_repo = SqliteRawDocumentRepository(database)
    job_repo = SqliteJobRepository(database)
    await raw_repo.save_all([greenhouse_doc()])

    agent = JobExtractionAgent(raw_repo, job_repo)
    jobs = await agent.run()

    assert len(jobs) == 1
    assert jobs[0].title == "Software Engineer"
    assert str(jobs[0].raw_url) == "https://databricks.com/jobs/1"
    assert await job_repo.count() == 1
    assert await raw_repo.get_unprocessed() == []


async def test_extract_skips_missing_parser(database):
    raw_repo = SqliteRawDocumentRepository(database)
    job_repo = SqliteJobRepository(database)
    doc = RawDocument(
        platform=SourcePlatform.LINKEDIN,
        source="linkedin",
        url="https://www.linkedin.com/posts/abc-activity-1",
    )
    await raw_repo.save_all([doc])

    agent = JobExtractionAgent(raw_repo, job_repo)
    jobs = await agent.run()

    assert jobs == []
    assert await job_repo.count() == 0
    assert await raw_repo.get_unprocessed() == []


async def test_extract_no_unprocessed_documents(database):
    raw_repo = SqliteRawDocumentRepository(database)
    job_repo = SqliteJobRepository(database)

    agent = JobExtractionAgent(raw_repo, job_repo)
    assert await agent.run() == []


async def test_extract_leaves_doc_unprocessed_on_parser_error(database, monkeypatch):
    import job_agent.agents.job_extraction.agent as agent_module

    class ThrowingParser:
        def parse(self, document):
            raise RuntimeError("boom")

    monkeypatch.setattr(agent_module, "get_parser", lambda ct: ThrowingParser())

    raw_repo = SqliteRawDocumentRepository(database)
    job_repo = SqliteJobRepository(database)
    await raw_repo.save_all([greenhouse_doc()])

    agent = JobExtractionAgent(raw_repo, job_repo)
    jobs = await agent.run()

    assert jobs == []
    assert await job_repo.count() == 0
    # document should remain unprocessed for a later retry
    assert len(await raw_repo.get_unprocessed()) == 1
