from job_agent.repositories.base import (
    DedupRepository,
    JobRepository,
    MatchRepository,
    RankingRepository,
    RawDocumentRepository,
)
from job_agent.repositories.dedup_repository import SqliteDedupRepository
from job_agent.repositories.job_repository import SqliteJobRepository
from job_agent.repositories.match_repository import SqliteMatchRepository
from job_agent.repositories.ranking_repository import SqliteRankingRepository
from job_agent.repositories.raw_document_repository import (
    SqliteRawDocumentRepository,
)

__all__ = [
    "DedupRepository",
    "JobRepository",
    "MatchRepository",
    "RankingRepository",
    "RawDocumentRepository",
    "SqliteDedupRepository",
    "SqliteJobRepository",
    "SqliteMatchRepository",
    "SqliteRankingRepository",
    "SqliteRawDocumentRepository",
]
