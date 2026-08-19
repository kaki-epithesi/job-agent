from job_agent.models import Job
from job_agent.repositories import SqliteJobRepository


def make_job(raw_url: str) -> Job:
    return Job(title="Software Engineer", company="Acme", raw_url=raw_url)


async def test_save_all_and_count(database):
    repo = SqliteJobRepository(database)
    saved = await repo.save_all(
        [
            make_job("https://example.com/jobs/1"),
            make_job("https://example.com/jobs/2"),
        ]
    )
    assert saved == 2
    assert await repo.count() == 2


async def test_save_all_dedupes_on_raw_url(database):
    repo = SqliteJobRepository(database)
    saved = await repo.save_all(
        [
            make_job("https://example.com/jobs/1"),
            make_job("https://example.com/jobs/1"),
        ]
    )
    assert saved == 1
    assert await repo.count() == 1


async def test_save_all_empty(database):
    repo = SqliteJobRepository(database)
    assert await repo.save_all([]) == 0
    assert await repo.count() == 0
