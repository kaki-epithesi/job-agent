from job_agent.agents.ranking.ranker import (
    combine,
    freshness_score,
    platform_score,
)
from job_agent.models import Job, RankedJob
from job_agent.repositories import (
    DedupRepository,
    JobRepository,
    MatchRepository,
    RankingRepository,
)
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class RankingAgent:
    """Agent 5: produces a final ordering of matched jobs.

    Ranks the jobs that have a resume-match score (produced by Agent 4),
    combining match, freshness, and platform signals. Sorts descending, assigns
    rank positions, and persists a fresh snapshot.
    """

    def __init__(
        self,
        job_repository: JobRepository,
        dedup_repository: DedupRepository,
        match_repository: MatchRepository,
        ranking_repository: RankingRepository,
    ) -> None:
        self._job_repository = job_repository
        self._dedup_repository = dedup_repository
        self._match_repository = match_repository
        self._ranking_repository = ranking_repository

    async def run(self) -> list[RankedJob]:
        matches = await self._match_repository.get_all()
        if not matches:
            logger.info("No match results; run 'match' before 'rank'.")
            await self._ranking_repository.clear()
            return []

        jobs_by_id = {job.id: job for job in await self._canonical_jobs()}

        ranked = [
            self._rank(jobs_by_id[result.job_id], result.score)
            for result in matches
            if result.job_id in jobs_by_id
        ]
        ranked.sort(key=lambda item: item.rank_score, reverse=True)

        for position, item in enumerate(ranked, 1):
            item.rank = position

        # Ranking is a full snapshot: clear stale rows before writing the new set.
        await self._ranking_repository.clear()
        await self._ranking_repository.save_all(ranked)

        logger.info("Ranked %d jobs.", len(ranked))
        return ranked

    async def _canonical_jobs(self) -> list[Job]:
        jobs = await self._job_repository.get_all()
        canonical_ids = set(await self._dedup_repository.get_canonical_job_ids())

        if canonical_ids:
            jobs = [job for job in jobs if job.id in canonical_ids]
        elif jobs:
            logger.info("No dedup results found; ranking all jobs.")

        return jobs

    @staticmethod
    def _rank(job: Job, match_score: float) -> RankedJob:
        freshness = freshness_score(job.posted_at)
        platform = platform_score(job.platform)
        return RankedJob(
            job_id=job.id,
            rank_score=round(combine(match_score, freshness, platform), 4),
            match_score=round(match_score, 4),
            freshness_score=round(freshness, 4),
            platform_score=platform,
        )
