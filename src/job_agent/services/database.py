"""Async SQLAlchemy database service."""

from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from job_agent.config import settings


def _ensure_parent_dir(url: str) -> None:
    """Create the parent directory for a file-based SQLite URL."""
    if not url.startswith("sqlite") or ":memory:" in url:
        return

    path = url.split("///", 1)[-1]
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)


def _normalize_url(url: str) -> str:
    """Upgrade a sync ``sqlite://`` URL to the async driver we require."""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


class Database:
    """Owns the async engine and session factory."""

    def __init__(self, url: str | None = None) -> None:
        self._url = _normalize_url(url or settings.database_url)
        _ensure_parent_dir(self._url)
        connect_args = {"timeout": 30} if self._url.startswith("sqlite") else {}
        self._engine = create_async_engine(
            self._url,
            echo=False,
            connect_args=connect_args,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    @property
    def session_factory(self) -> async_sessionmaker:
        return self._session_factory

    async def initialize(self) -> None:
        """Create tables if they do not exist."""
        from job_agent.repositories.tables import metadata

        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()
