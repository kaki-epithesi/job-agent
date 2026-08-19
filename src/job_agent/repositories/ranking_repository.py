from sqlalchemy import delete, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from job_agent.models import RankedJob
from job_agent.repositories.tables import job_rankings
from job_agent.services.database import Database
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class SqliteRankingRepository:
    """SQLite-backed implementation of ``RankingRepository``."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def save_all(self, ranked: list[RankedJob]) -> int:
        if not ranked:
            return 0

        rows = [
            {
                "job_id": item.job_id,
                "rank_score": item.rank_score,
                "match_score": item.match_score,
                "freshness_score": item.freshness_score,
                "platform_score": item.platform_score,
                "rank": item.rank,
            }
            for item in ranked
        ]

        statement = sqlite_insert(job_rankings).values(rows)
        statement = statement.on_conflict_do_update(
            index_elements=["job_id"],
            set_={
                "rank_score": statement.excluded.rank_score,
                "match_score": statement.excluded.match_score,
                "freshness_score": statement.excluded.freshness_score,
                "platform_score": statement.excluded.platform_score,
                "rank": statement.excluded.rank,
            },
        )

        async with self._db.session_factory() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount or 0

    async def clear(self) -> None:
        async with self._db.session_factory() as session:
            await session.execute(delete(job_rankings))
            await session.commit()

    async def get_all(self) -> list[RankedJob]:
        async with self._db.session_factory() as session:
            result = await session.execute(select(job_rankings).order_by(job_rankings.c.rank))
            rows = result.mappings().all()

        return [
            RankedJob(
                job_id=row["job_id"],
                rank_score=row["rank_score"],
                match_score=row["match_score"],
                freshness_score=row["freshness_score"],
                platform_score=row["platform_score"],
                rank=row["rank"],
            )
            for row in rows
        ]

    async def count(self) -> int:
        async with self._db.session_factory() as session:
            result = await session.execute(select(func.count()).select_from(job_rankings))
            return result.scalar_one()
