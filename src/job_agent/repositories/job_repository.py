from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from job_agent.models import (
    ExperienceLevel,
    Job,
    JobStatus,
    JobType,
    SourcePlatform,
    WorkMode,
)
from job_agent.repositories.tables import jobs
from job_agent.services.database import Database
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class SqliteJobRepository:
    """SQLite-backed implementation of ``JobRepository``."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def save_all(self, job_list: list[Job]) -> int:
        if not job_list:
            return 0

        rows = [self._to_row(job) for job in job_list]

        statement = sqlite_insert(jobs).values(rows)
        statement = statement.on_conflict_do_nothing(index_elements=["raw_url"])

        async with self._db.session_factory() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount or 0

    async def count(self) -> int:
        async with self._db.session_factory() as session:
            result = await session.execute(select(func.count()).select_from(jobs))
            return result.scalar_one()

    async def get_all(self) -> list[Job]:
        async with self._db.session_factory() as session:
            result = await session.execute(select(jobs).order_by(jobs.c.id))
            rows = result.mappings().all()

        return [self._row_to_job(row) for row in rows]

    @staticmethod
    def _to_row(job: Job) -> dict:
        return {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "apply_url": str(job.apply_url) if job.apply_url else None,
            "job_type": job.job_type.value,
            "work_mode": job.work_mode.value,
            "experience_level": job.experience_level.value,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            "source": job.source,
            "platform": job.platform.value if job.platform else None,
            "status": job.status.value,
            "raw_url": str(job.raw_url) if job.raw_url else None,
        }

    @staticmethod
    def _row_to_job(row) -> Job:
        return Job(
            id=row["id"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            description=row["description"],
            apply_url=row["apply_url"],
            job_type=JobType(row["job_type"]),
            work_mode=WorkMode(row["work_mode"]),
            experience_level=ExperienceLevel(row["experience_level"]),
            salary_min=row["salary_min"],
            salary_max=row["salary_max"],
            salary_currency=row["salary_currency"],
            posted_at=datetime.fromisoformat(row["posted_at"]) if row["posted_at"] else None,
            source=row["source"],
            platform=SourcePlatform(row["platform"]) if row["platform"] else None,
            status=JobStatus(row["status"]),
            raw_url=row["raw_url"],
        )
