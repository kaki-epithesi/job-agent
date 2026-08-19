from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from job_agent.models import DedupRecord
from job_agent.repositories.tables import job_dedup
from job_agent.services.database import Database
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class SqliteDedupRepository:
    """SQLite-backed implementation of ``DedupRepository``."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def save_all(self, records: list[DedupRecord]) -> int:
        if not records:
            return 0

        rows = [
            {
                "job_id": record.job_id,
                "dedup_key": record.dedup_key,
                "canonical_job_id": record.canonical_job_id,
                "is_duplicate": int(record.is_duplicate),
            }
            for record in records
        ]

        statement = sqlite_insert(job_dedup).values(rows)
        statement = statement.on_conflict_do_update(
            index_elements=["job_id"],
            set_={
                "dedup_key": statement.excluded.dedup_key,
                "canonical_job_id": statement.excluded.canonical_job_id,
                "is_duplicate": statement.excluded.is_duplicate,
            },
        )

        async with self._db.session_factory() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount or 0

    async def count(self) -> int:
        async with self._db.session_factory() as session:
            result = await session.execute(select(func.count()).select_from(job_dedup))
            return result.scalar_one()

    async def get_canonical_job_ids(self) -> list[int]:
        async with self._db.session_factory() as session:
            result = await session.execute(
                select(job_dedup.c.job_id).where(job_dedup.c.is_duplicate == 0)
            )
            return list(result.scalars().all())
