from job_agent.models import RankedJob
from job_agent.repositories import SqliteRankingRepository


def make_ranked(job_id: int, rank_score: float, rank: int) -> RankedJob:
    return RankedJob(
        job_id=job_id,
        rank_score=rank_score,
        match_score=0.5,
        freshness_score=0.5,
        platform_score=1.0,
        rank=rank,
    )


async def test_save_all_and_get_all_ordered(database):
    repo = SqliteRankingRepository(database)
    await repo.save_all([make_ranked(1, 0.7, 2), make_ranked(2, 0.9, 1)])

    assert await repo.count() == 2
    assert [r.job_id for r in await repo.get_all()] == [2, 1]


async def test_save_all_upserts(database):
    repo = SqliteRankingRepository(database)
    await repo.save_all([make_ranked(1, 0.7, 1)])

    await repo.save_all([make_ranked(1, 0.5, 3)])

    assert await repo.count() == 1


async def test_clear(database):
    repo = SqliteRankingRepository(database)
    await repo.save_all([make_ranked(1, 0.9, 1), make_ranked(2, 0.8, 2)])
    assert await repo.count() == 2

    await repo.clear()
    assert await repo.count() == 0
