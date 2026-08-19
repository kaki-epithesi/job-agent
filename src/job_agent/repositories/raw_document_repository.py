from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from job_agent.models import RawDocument, SourcePlatform
from job_agent.repositories.tables import raw_documents
from job_agent.services.database import Database
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class SqliteRawDocumentRepository:
    """SQLite-backed implementation of ``RawDocumentRepository``."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def save_all(self, documents: list[RawDocument]) -> int:
        if not documents:
            return 0

        rows = [
            {
                "platform": doc.platform.value,
                "source": doc.source,
                "url": str(doc.url),
                "title": doc.title,
                "raw_content": doc.raw_content,
                "metadata": doc.metadata,
                "discovered_at": doc.discovered_at.isoformat(),
                "processed": 0,
            }
            for doc in documents
        ]

        statement = sqlite_insert(raw_documents).values(rows)
        statement = statement.on_conflict_do_nothing(index_elements=["url"])

        async with self._db.session_factory() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount or 0

    async def get_unprocessed(self, limit: int | None = None) -> list[RawDocument]:
        statement = (
            select(raw_documents).where(raw_documents.c.processed == 0).order_by(raw_documents.c.id)
        )
        if limit is not None:
            statement = statement.limit(limit)

        async with self._db.session_factory() as session:
            result = await session.execute(statement)
            rows = result.mappings().all()

        return [self._row_to_document(row) for row in rows]

    async def mark_processed(self, ids: list[int]) -> None:
        if not ids:
            return

        statement = update(raw_documents).where(raw_documents.c.id.in_(ids)).values(processed=1)

        async with self._db.session_factory() as session:
            await session.execute(statement)
            await session.commit()

    async def count(self) -> int:
        async with self._db.session_factory() as session:
            result = await session.execute(select(func.count()).select_from(raw_documents))
            return result.scalar_one()

    @staticmethod
    def _row_to_document(row) -> RawDocument:
        return RawDocument(
            id=row["id"],
            platform=SourcePlatform(row["platform"]),
            source=row["source"],
            url=row["url"],
            title=row["title"],
            raw_content=row["raw_content"],
            metadata=row["metadata"] or {},
            discovered_at=datetime.fromisoformat(row["discovered_at"]),
        )
