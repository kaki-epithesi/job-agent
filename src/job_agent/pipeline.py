"""Full pipeline orchestrator (composition root).

Wires concrete repositories and services to the agents and runs them in
sequence: discover -> extract -> dedupe -> match -> rank -> notify.
"""

from pathlib import Path

from job_agent.agents.deduplication import DeduplicationAgent
from job_agent.agents.job_extraction import JobExtractionAgent
from job_agent.agents.notification import NotificationAgent
from job_agent.agents.notification.notifiers import build_notifier
from job_agent.agents.ranking import RankingAgent
from job_agent.agents.resume_matching import ResumeMatchingAgent
from job_agent.agents.source_discovery import SourceDiscoveryAgent
from job_agent.config.notifications import load_notifications
from job_agent.config.resume import load_resume
from job_agent.config.sources import load_sources
from job_agent.models import PipelineReport
from job_agent.repositories import (
    SqliteDedupRepository,
    SqliteJobRepository,
    SqliteMatchRepository,
    SqliteRankingRepository,
    SqliteRawDocumentRepository,
)
from job_agent.services.database import Database
from job_agent.services.http import HttpClient
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class Pipeline:
    """Runs the full agent pipeline end-to-end."""

    def __init__(
        self,
        *,
        sources_file: str | None = None,
        resume_file: str | None = None,
        notifications_file: str | None = None,
        database_url: str | None = None,
        top_n: int = 10,
    ) -> None:
        self._sources_file = Path(sources_file) if sources_file else None
        self._resume_file = Path(resume_file) if resume_file else None
        self._notifications_file = Path(notifications_file) if notifications_file else None
        self._database_url = database_url
        self._top_n = top_n

    async def run(self) -> PipelineReport:
        """Run every agent in sequence and return a summary."""
        async with HttpClient() as http:
            db = Database(self._database_url)
            await db.initialize()
            try:
                return await self._run_agents(http, db)
            finally:
                await db.close()

    async def _run_agents(
        self,
        http: HttpClient,
        db: Database,
    ) -> PipelineReport:
        raw_repo = SqliteRawDocumentRepository(db)
        job_repo = SqliteJobRepository(db)
        dedup_repo = SqliteDedupRepository(db)
        match_repo = SqliteMatchRepository(db)
        ranking_repo = SqliteRankingRepository(db)

        # Agent 1 — Source Discovery
        config = load_sources(self._sources_file)
        sources = [source for source in config.sources if source.enabled]
        documents = await SourceDiscoveryAgent(http, raw_repo, locations=config.locations).run(
            sources
        )

        # Agent 2 — Job Extraction
        jobs = await JobExtractionAgent(raw_repo, job_repo).run()

        # Agent 3 — Deduplication
        dedup_report = await DeduplicationAgent(job_repo, dedup_repo).run()

        # Agent 4 — Resume Matching
        resume = load_resume(self._resume_file)
        matches = await ResumeMatchingAgent(job_repo, dedup_repo, match_repo, resume).run()

        # Agent 5 — Ranking
        ranked = await RankingAgent(job_repo, dedup_repo, match_repo, ranking_repo).run()

        # Agent 6 — Notification
        notifiers = self._build_notifiers()
        notify_report = await NotificationAgent(
            notifiers, ranking_repo, job_repo, match_repo, self._top_n
        ).run()

        logger.info(
            "Pipeline complete: %d discovered, %d extracted, %d canonical, "
            "%d matched, %d ranked, %d notified.",
            len(documents),
            len(jobs),
            dedup_report.canonical,
            len(matches),
            len(ranked),
            notify_report.delivered,
        )
        return PipelineReport(
            discovered=len(documents),
            extracted=len(jobs),
            canonical=dedup_report.canonical,
            matched=len(matches),
            ranked=len(ranked),
            notified=notify_report.delivered,
        )

    def _build_notifiers(self):
        config = load_notifications(self._notifications_file)
        return [
            build_notifier(channel.type, channel.config)
            for channel in config.channels
            if channel.enabled
        ]
