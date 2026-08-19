import asyncio

from job_agent.models import DedupRecord, Job, MatchResult, RankedJob
from job_agent.repositories import (
    SqliteDedupRepository,
    SqliteJobRepository,
    SqliteMatchRepository,
    SqliteRankingRepository,
)
from job_agent.web import queries


async def _seed(database):
    job_repo = SqliteJobRepository(database)
    await job_repo.save_all(
        [
            Job(
                title="Software Engineer",
                company="Acme",
                location="Bengaluru",
                apply_url="https://apply.example/1",
                raw_url="https://a.example/1",
            ),
            Job(title="Account Executive", company="Acme", raw_url="https://a.example/2"),
        ]
    )
    swe, account = await job_repo.get_all()

    await SqliteRankingRepository(database).save_all(
        [
            RankedJob(
                job_id=swe.id,
                rank_score=0.5,
                match_score=0.4,
                freshness_score=0.6,
                platform_score=1.0,
                rank=1,
            )
        ]
    )
    await SqliteMatchRepository(database).save_all(
        [MatchResult(job_id=swe.id, score=0.4, matched_skills=["python"])]
    )
    await SqliteDedupRepository(database).save_all(
        [
            DedupRecord(job_id=swe.id, dedup_key="k1", canonical_job_id=swe.id, is_duplicate=False),
            DedupRecord(
                job_id=account.id, dedup_key="k2", canonical_job_id=account.id, is_duplicate=False
            ),
        ]
    )


async def test_fetch_jobs_all(database):
    await _seed(database)
    async with database.session_factory() as session:
        rows = await queries.fetch_jobs(session, ranked_only=False)

    assert len(rows) == 2


async def test_fetch_jobs_ranked_only(database):
    await _seed(database)
    async with database.session_factory() as session:
        rows = await queries.fetch_jobs(session, ranked_only=True)

    assert len(rows) == 1
    assert rows[0]["title"] == "Software Engineer"
    assert rows[0]["rank"] == 1
    assert rows[0]["matched_skills"] == ["python"]


async def test_fetch_stats(database):
    await _seed(database)
    async with database.session_factory() as session:
        stats = await queries.fetch_stats(session)

    assert stats == {"jobs": 2, "ranked": 1, "matched": 1, "duplicates": 0}


async def test_fetch_jobs_empty(database):
    async with database.session_factory() as session:
        assert await queries.fetch_jobs(session) == []
        assert await queries.fetch_stats(session) == {
            "jobs": 0,
            "ranked": 0,
            "matched": 0,
            "duplicates": 0,
        }


async def test_trigger_run_starts_pipeline(monkeypatch):
    import job_agent.web.app as web

    async def fake_run():
        return None

    monkeypatch.setattr(web, "_default_run", fake_run)
    web._run_state.update(status="idle", started_at=None, finished_at=None, error=None)

    result = await web.trigger_run()
    assert result["status"] == "running"

    await asyncio.sleep(0.1)
    assert web._run_state["status"] == "completed"
