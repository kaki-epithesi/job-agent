from job_agent.models import RawDocument, SourcePlatform
from job_agent.repositories import SqliteRawDocumentRepository


def make_doc(url: str) -> RawDocument:
    return RawDocument(
        platform=SourcePlatform.GREENHOUSE,
        source="greenhouse:databricks",
        url=url,
        title="Software Engineer",
    )


async def test_save_all_and_count(database):
    repo = SqliteRawDocumentRepository(database)
    docs = [
        make_doc("https://example.com/jobs/1"),
        make_doc("https://example.com/jobs/2"),
    ]
    saved = await repo.save_all(docs)
    assert saved == 2
    assert await repo.count() == 2


async def test_save_all_dedupes_on_url(database):
    repo = SqliteRawDocumentRepository(database)
    docs = [
        make_doc("https://example.com/jobs/1"),
        make_doc("https://example.com/jobs/1"),
    ]
    saved = await repo.save_all(docs)
    assert saved == 1
    assert await repo.count() == 1


async def test_save_all_empty(database):
    repo = SqliteRawDocumentRepository(database)
    assert await repo.save_all([]) == 0
    assert await repo.count() == 0


async def test_get_unprocessed_and_mark_processed(database):
    repo = SqliteRawDocumentRepository(database)
    await repo.save_all([make_doc("https://example.com/jobs/1")])

    documents = await repo.get_unprocessed()
    assert len(documents) == 1
    assert documents[0].id is not None

    await repo.mark_processed([documents[0].id])
    assert await repo.get_unprocessed() == []
    assert await repo.count() == 1
