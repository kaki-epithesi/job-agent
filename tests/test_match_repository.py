from job_agent.models import MatchResult
from job_agent.repositories import SqliteMatchRepository


async def test_save_all_and_count(database):
    repo = SqliteMatchRepository(database)
    results = [
        MatchResult(job_id=1, score=0.8, matched_skills=["python"]),
        MatchResult(job_id=2, score=0.2),
    ]
    assert await repo.save_all(results) == 2
    assert await repo.count() == 2


async def test_save_all_upserts(database):
    repo = SqliteMatchRepository(database)
    await repo.save_all([MatchResult(job_id=1, score=0.8, matched_skills=["python"])])

    await repo.save_all([MatchResult(job_id=1, score=0.9, matched_skills=["python", "docker"])])

    assert await repo.count() == 1


async def test_save_all_skips_none_job_id(database):
    repo = SqliteMatchRepository(database)
    assert await repo.save_all([MatchResult(score=0.5)]) == 0
    assert await repo.count() == 0
