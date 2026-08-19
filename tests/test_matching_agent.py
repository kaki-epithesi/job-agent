from job_agent.agents.deduplication import DeduplicationAgent
from job_agent.agents.resume_matching import ResumeMatchingAgent
from job_agent.models import Job, Resume
from job_agent.repositories import (
    SqliteDedupRepository,
    SqliteJobRepository,
    SqliteMatchRepository,
)


def make_resume() -> Resume:
    return Resume(
        skills=["python", "docker"],
        roles=["backend engineer"],
        keywords=[],
        locations=["remote"],
    )


async def test_agent_matches_canonical_jobs(database):
    job_repo = SqliteJobRepository(database)
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)

    await job_repo.save_all(
        [
            Job(
                title="Backend Engineer",
                company="Acme",
                location="Remote",
                description="python docker",
                raw_url="https://a.example/1",
            ),
            Job(
                title="Backend Engineer",
                company="Acme",
                location="Remote",
                description="python docker",
                raw_url="https://b.example/1",
            ),
            Job(
                title="Accountant",
                company="Acme",
                location="Onsite",
                description="tax",
                raw_url="https://a.example/2",
            ),
        ]
    )
    await DeduplicationAgent(job_repo, dedup_repo).run()

    agent = ResumeMatchingAgent(job_repo, dedup_repo, match_repo, make_resume())
    results = await agent.run()

    assert len(results) == 2
    assert results[0].score > results[1].score
    assert await match_repo.count() == 2


async def test_agent_filters_by_target_roles(database):
    job_repo = SqliteJobRepository(database)
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)

    await job_repo.save_all(
        [
            Job(
                title="Software Engineer",
                company="A",
                description="python",
                raw_url="https://a.example/1",
            ),
            Job(
                title="Account Executive",
                company="B",
                description="sales",
                raw_url="https://a.example/2",
            ),
        ]
    )
    await DeduplicationAgent(job_repo, dedup_repo).run()

    resume = Resume(
        skills=["python"],
        roles=["backend engineer"],
        target_roles=["engineer"],
    )
    agent = ResumeMatchingAgent(job_repo, dedup_repo, match_repo, resume)
    results = await agent.run()

    assert len(results) == 1
    assert await match_repo.count() == 1


async def test_agent_matches_all_when_no_dedup(database):
    job_repo = SqliteJobRepository(database)
    dedup_repo = SqliteDedupRepository(database)
    match_repo = SqliteMatchRepository(database)

    await job_repo.save_all(
        [
            Job(
                title="Backend Engineer",
                company="Acme",
                location="Remote",
                description="python",
                raw_url="https://a.example/1",
            ),
            Job(
                title="Accountant",
                company="Acme",
                location="Onsite",
                description="tax",
                raw_url="https://a.example/2",
            ),
        ]
    )

    agent = ResumeMatchingAgent(job_repo, dedup_repo, match_repo, make_resume())
    results = await agent.run()

    assert len(results) == 2
