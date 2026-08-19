from job_agent.agents.notification.formatter import format_notification
from job_agent.agents.notification.notifiers import Notifier
from job_agent.models import NotificationReport
from job_agent.repositories import (
    JobRepository,
    MatchRepository,
    RankingRepository,
)
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationAgent:
    """Agent 6: delivers the top-ranked jobs to configured notifier channels."""

    def __init__(
        self,
        notifiers: list[Notifier],
        ranking_repository: RankingRepository,
        job_repository: JobRepository,
        match_repository: MatchRepository,
        top_n: int = 10,
    ) -> None:
        self._notifiers = notifiers
        self._ranking_repository = ranking_repository
        self._job_repository = job_repository
        self._match_repository = match_repository
        self._top_n = top_n

    async def run(self) -> NotificationReport:
        """Format the top-ranked jobs and send them to every notifier."""
        ranked = await self._ranking_repository.get_all()
        top = ranked[: self._top_n]

        if not top:
            logger.info("No ranked jobs to notify.")
            return NotificationReport()

        jobs_by_id = {job.id: job for job in await self._job_repository.get_all()}
        matches_by_id = {result.job_id: result for result in await self._match_repository.get_all()}

        message = format_notification(top, jobs_by_id, matches_by_id)

        delivered = 0
        failed = 0
        channels: list[str] = []

        for notifier in self._notifiers:
            channels.append(notifier.channel)
            try:
                await notifier.send(message)
                delivered += 1
            except Exception:
                logger.exception("Notifier '%s' failed.", notifier.channel)
                failed += 1

        logger.info(
            "Notified %d channel(s) about %d jobs.",
            delivered,
            message.job_count,
        )
        return NotificationReport(
            delivered=delivered,
            failed=failed,
            channels=channels,
        )
