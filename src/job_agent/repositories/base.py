from typing import Protocol

from job_agent.models import DedupRecord, Job, MatchResult, RankedJob, RawDocument


class RawDocumentRepository(Protocol):
    """Persistence contract for discovered raw documents."""

    async def save_all(self, documents: list[RawDocument]) -> int:
        """Persist documents, returning the number inserted."""
        ...

    async def get_unprocessed(self, limit: int | None = None) -> list[RawDocument]:
        """Return documents not yet processed by Agent 2."""
        ...

    async def mark_processed(self, ids: list[int]) -> None:
        """Mark documents as processed."""
        ...

    async def count(self) -> int:
        """Return the number of stored documents."""
        ...


class JobRepository(Protocol):
    """Persistence contract for extracted jobs."""

    async def save_all(self, jobs: list[Job]) -> int:
        """Persist jobs, returning the number inserted."""
        ...

    async def get_all(self) -> list[Job]:
        """Return all stored jobs, ordered by id."""
        ...

    async def count(self) -> int:
        """Return the number of stored jobs."""
        ...


class DedupRepository(Protocol):
    """Persistence contract for deduplication results."""

    async def save_all(self, records: list[DedupRecord]) -> int:
        """Upsert dedup records, returning the number written."""
        ...

    async def get_canonical_job_ids(self) -> list[int]:
        """Return ids of jobs that are canonical (not duplicates)."""
        ...

    async def count(self) -> int:
        """Return the number of stored dedup records."""
        ...


class MatchRepository(Protocol):
    """Persistence contract for resume-match results."""

    async def save_all(self, results: list[MatchResult]) -> int:
        """Upsert match results, returning the number written."""
        ...

    async def clear(self) -> None:
        """Remove all existing match results."""
        ...

    async def get_all(self) -> list[MatchResult]:
        """Return all stored match results."""
        ...

    async def count(self) -> int:
        """Return the number of stored match results."""
        ...


class RankingRepository(Protocol):
    """Persistence contract for ranking results."""

    async def save_all(self, ranked: list[RankedJob]) -> int:
        """Upsert ranked jobs, returning the number written."""
        ...

    async def clear(self) -> None:
        """Remove all existing ranking rows."""
        ...

    async def get_all(self) -> list[RankedJob]:
        """Return all ranked jobs, ordered by rank."""
        ...

    async def count(self) -> int:
        """Return the number of stored ranked jobs."""
        ...
