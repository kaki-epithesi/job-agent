from datetime import UTC, datetime

from job_agent.agents.deduplication import DeduplicationAgent
from job_agent.agents.ranking import RankingAgent
from job_agent.models import Job, MatchResult
from job_agent.repositories import (
    SqliteDedupRepository,
    SqliteJobRepository,
    SqliteMatchRepository,
    SqliteRankingRepository,
)


async def _seed(database, jobs):
    job_repo = SqliteJobRepository(database)
    await job_repo.save_all(jobs)
    await DeduplicationAgent(job_repo, SqliteDedupRepository(database)).run()
    return job_repo


async def test_ranking_orders_by_combined_score(database):
    posted = datetime(2026, 8, 1, tzinfo=UTC)
    job_repo = await _seed(
        database,
        [
            Job(
                title="Backend Engineer",
                company="Acme",
                location="Remote",
                posted_at=posted,
                raw_url="https://a.example/1",
            ),
            Job(
                title="Accountant",
                company="Acme",
                location="Onsite",
                posted_at=posted,
                raw_url="https://a.example/2",
            ),
        ],
    )
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    jobs_by_title = {job.title: job for job in await job_repo.get_all()}
    await match_repo.save_all(
        [
            MatchResult(job_id=jobs_by_title["Backend Engineer"].id, score=0.8),
            MatchResult(job_id=jobs_by_title["Accountant"].id, score=0.1),
        ]
    )

    results = await RankingAgent(job_repo, dedup_repo, match_repo, ranking_repo).run()

    assert results[0].job_id == jobs_by_title["Backend Engineer"].id
    assert results[0].rank == 1
    assert results[1].rank == 2
    assert await ranking_repo.count() == 2


async def test_ranking_without_matches_returns_empty(database):
    job_repo = await _seed(
        database, [Job(title="Backend Engineer", company="Acme", raw_url="https://a.example/1")]
    )
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    results = await RankingAgent(job_repo, dedup_repo, match_repo, ranking_repo).run()

    assert results == []
    assert await ranking_repo.count() == 0


async def test_ranking_only_ranks_matched_jobs(database):
    job_repo = await _seed(
        database,
        [
            Job(title="Software Engineer", company="A", raw_url="https://a.example/1"),
            Job(title="Data Engineer", company="B", raw_url="https://a.example/2"),
        ],
    )
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    jobs_by_title = {job.title: job for job in await job_repo.get_all()}
    await match_repo.save_all(
        [MatchResult(job_id=jobs_by_title["Software Engineer"].id, score=0.7)]
    )

    results = await RankingAgent(job_repo, dedup_repo, match_repo, ranking_repo).run()

    assert len(results) == 1
    assert results[0].job_id == jobs_by_title["Software Engineer"].id


async def test_ranking_replaces_stale_rows(database):
    job_repo = await _seed(
        database,
        [
            Job(title="Software Engineer", company="A", raw_url="https://a.example/1"),
            Job(title="Account Executive", company="B", raw_url="https://a.example/2"),
        ],
    )
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    jobs_by_title = {job.title: job for job in await job_repo.get_all()}
    await match_repo.save_all(
        [
            MatchResult(job_id=jobs_by_title["Software Engineer"].id, score=0.8),
            MatchResult(job_id=jobs_by_title["Account Executive"].id, score=0.1),
        ]
    )

    # First rank -> both jobs.
    assert len(await RankingAgent(job_repo, dedup_repo, match_repo, ranking_repo).run()) == 2

    # Re-match with only the engineer -> re-rank leaves only one row (stale cleared).
    await match_repo.clear()
    await match_repo.save_all(
        [MatchResult(job_id=jobs_by_title["Software Engineer"].id, score=0.8)]
    )
    assert len(await RankingAgent(job_repo, dedup_repo, match_repo, ranking_repo).run()) == 1
    assert await ranking_repo.count() == 1
