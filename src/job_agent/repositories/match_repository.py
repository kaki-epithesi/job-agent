from sqlalchemy import delete, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from job_agent.models import MatchResult
from job_agent.repositories.tables import job_matches
from job_agent.services.database import Database
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class SqliteMatchRepository:
    """SQLite-backed implementation of ``MatchRepository``."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def save_all(self, results: list[MatchResult]) -> int:
        rows = [
            {
                "job_id": result.job_id,
                "score": result.score,
                "matched_skills": result.matched_skills,
                "matched_roles": result.matched_roles,
                "matched_keywords": result.matched_keywords,
                "location_match": int(result.location_match),
            }
            for result in results
            if result.job_id is not None
        ]
        if not rows:
            return 0

        statement = sqlite_insert(job_matches).values(rows)
        statement = statement.on_conflict_do_update(
            index_elements=["job_id"],
            set_={
                "score": statement.excluded.score,
                "matched_skills": statement.excluded.matched_skills,
                "matched_roles": statement.excluded.matched_roles,
                "matched_keywords": statement.excluded.matched_keywords,
                "location_match": statement.excluded.location_match,
            },
        )

        async with self._db.session_factory() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount or 0

    async def count(self) -> int:
        async with self._db.session_factory() as session:
            result = await session.execute(select(func.count()).select_from(job_matches))
            return result.scalar_one()

    async def clear(self) -> None:
        async with self._db.session_factory() as session:
            await session.execute(delete(job_matches))
            await session.commit()

    async def get_all(self) -> list[MatchResult]:
        async with self._db.session_factory() as session:
            result = await session.execute(select(job_matches).order_by(job_matches.c.job_id))
            rows = result.mappings().all()

        return [
            MatchResult(
                job_id=row["job_id"],
                score=row["score"],
                matched_skills=row["matched_skills"] or [],
                matched_roles=row["matched_roles"] or [],
                matched_keywords=row["matched_keywords"] or [],
                location_match=bool(row["location_match"]),
            )
            for row in rows
        ]
