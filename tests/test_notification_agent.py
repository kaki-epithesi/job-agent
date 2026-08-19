from job_agent.agents.notification import NotificationAgent
from job_agent.models import Job, MatchResult, RankedJob
from job_agent.repositories import (
    SqliteJobRepository,
    SqliteMatchRepository,
    SqliteRankingRepository,
)


class RecordingNotifier:
    channel = "recording"

    def __init__(self, config=None):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


class FailingNotifier:
    channel = "failing"

    async def send(self, message):
        raise RuntimeError("boom")


async def test_agent_sends_top_jobs(database):
    job_repo = SqliteJobRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    await job_repo.save_all(
        [
            Job(
                title="Backend Engineer",
                company="Acme",
                location="Remote",
                raw_url="https://a.example/1",
            ),
            Job(
                title="Accountant",
                company="Acme",
                location="Onsite",
                raw_url="https://a.example/2",
            ),
        ]
    )
    jobs_by_title = {job.title: job for job in await job_repo.get_all()}
    backend = jobs_by_title["Backend Engineer"]

    await match_repo.save_all(
        [MatchResult(job_id=backend.id, score=0.8, matched_skills=["python"])]
    )
    await ranking_repo.save_all(
        [
            RankedJob(
                job_id=backend.id,
                rank_score=0.9,
                match_score=0.8,
                freshness_score=0.5,
                platform_score=1.0,
                rank=1,
            )
        ]
    )

    notifier = RecordingNotifier()
    agent = NotificationAgent([notifier], ranking_repo, job_repo, match_repo, top_n=1)
    report = await agent.run()

    assert report.delivered == 1
    assert report.channels == ["recording"]
    assert notifier.sent[0].job_count == 1
    assert "Backend Engineer" in notifier.sent[0].body


async def test_agent_no_rankings_returns_empty(database):
    job_repo = SqliteJobRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    notifier = RecordingNotifier()
    agent = NotificationAgent([notifier], ranking_repo, job_repo, match_repo)
    report = await agent.run()

    assert report.delivered == 0
    assert notifier.sent == []


async def test_agent_tolerates_failing_notifier(database):
    job_repo = SqliteJobRepository(database)
    match_repo = SqliteMatchRepository(database)
    ranking_repo = SqliteRankingRepository(database)

    await job_repo.save_all([Job(title="SDE", company="Acme", raw_url="https://a.example/1")])
    job = (await job_repo.get_all())[0]
    await ranking_repo.save_all(
        [
            RankedJob(
                job_id=job.id,
                rank_score=0.5,
                match_score=0.5,
                freshness_score=0.5,
                platform_score=1.0,
                rank=1,
            )
        ]
    )

    agent = NotificationAgent([FailingNotifier()], ranking_repo, job_repo, match_repo, top_n=10)
    report = await agent.run()

    assert report.delivered == 0
    assert report.failed == 1
