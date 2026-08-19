from job_agent.models import DedupRecord
from job_agent.repositories import SqliteDedupRepository


async def test_save_all_and_count(database):
    repo = SqliteDedupRepository(database)
    records = [
        DedupRecord(job_id=1, dedup_key="k", canonical_job_id=1, is_duplicate=False),
        DedupRecord(job_id=2, dedup_key="k", canonical_job_id=1, is_duplicate=True),
    ]
    assert await repo.save_all(records) == 2
    assert await repo.count() == 2


async def test_save_all_upserts(database):
    repo = SqliteDedupRepository(database)
    await repo.save_all(
        [DedupRecord(job_id=1, dedup_key="k", canonical_job_id=1, is_duplicate=False)]
    )

    await repo.save_all(
        [DedupRecord(job_id=1, dedup_key="k2", canonical_job_id=2, is_duplicate=True)]
    )

    assert await repo.count() == 1
