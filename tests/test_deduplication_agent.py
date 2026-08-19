from sqlalchemy import select

from job_agent.agents.deduplication import DeduplicationAgent
from job_agent.models import DedupReport, Job
from job_agent.repositories import SqliteDedupRepository, SqliteJobRepository
from job_agent.repositories.tables import job_dedup


async def test_dedup_groups_duplicates(database):
    job_repo = SqliteJobRepository(database)
    dedup_repo = SqliteDedupRepository(database)
    await job_repo.save_all(
        [
            Job(
                title="Software Engineer",
                company="Acme",
                location="San Francisco, CA",
                raw_url="https://a.example/jobs/1",
            ),
            Job(
                title="Software Engineer",
                company="Acme",
                location="San Francisco, CA",
                raw_url="https://b.example/jobs/1",
            ),
            Job(
                title="Data Scientist",
                company="Acme",
                location="Remote",
                raw_url="https://a.example/jobs/2",
            ),
        ]
    )

    agent = DeduplicationAgent(job_repo, dedup_repo)
    report = await agent.run()

    assert report.total == 3
    assert report.canonical == 2
    assert report.duplicates == 1
    assert await dedup_repo.count() == 3


async def test_dedup_prefers_job_with_apply_url(database):
    job_repo = SqliteJobRepository(database)
    dedup_repo = SqliteDedupRepository(database)
    await job_repo.save_all(
        [
            Job(
                title="SWE",
                company="Acme",
                location="Remote",
                raw_url="https://a.example/1",
            ),
            Job(
                title="SWE",
                company="Acme",
                location="Remote",
                raw_url="https://b.example/1",
                apply_url="https://apply.example/1",
                description="Full job description",
            ),
        ]
    )

    agent = DeduplicationAgent(job_repo, dedup_repo)
    await agent.run()

    all_jobs = await job_repo.get_all()
    by_raw_url = {str(j.raw_url): j for j in all_jobs}
    plain = by_raw_url["https://a.example/1"]
    complete = by_raw_url["https://b.example/1"]

    async with database.session_factory() as session:
        rows = (await session.execute(select(job_dedup))).mappings().all()

    by_id = {row["job_id"]: row for row in rows}
    assert by_id[complete.id]["canonical_job_id"] == complete.id
    assert by_id[complete.id]["is_duplicate"] == 0
    assert by_id[plain.id]["is_duplicate"] == 1


async def test_dedup_no_jobs(database):
    job_repo = SqliteJobRepository(database)
    dedup_repo = SqliteDedupRepository(database)

    agent = DeduplicationAgent(job_repo, dedup_repo)
    report = await agent.run()

    assert report == DedupReport(total=0, canonical=0, duplicates=0, groups=0)
