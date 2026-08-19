from job_agent.agents.resume_matching.matcher import match
from job_agent.models import Job, MatchResult, Resume
from job_agent.repositories import (
    DedupRepository,
    JobRepository,
    MatchRepository,
)
from job_agent.utils.logger import setup_logger
from job_agent.utils.text import matches_any

logger = setup_logger(__name__)


class ResumeMatchingAgent:
    """Agent 4: scores canonical jobs against the user's resume.

    Matches only canonical (non-duplicate) jobs, falling back to all jobs if
    deduplication has not yet run. When ``resume.target_roles`` is configured,
    only jobs whose title matches one of the role keywords are scored (this is
    the single role gate for the pipeline). Persists scores and returns them
    sorted descending.
    """

    def __init__(
        self,
        job_repository: JobRepository,
        dedup_repository: DedupRepository,
        match_repository: MatchRepository,
        resume: Resume,
    ) -> None:
        self._job_repository = job_repository
        self._dedup_repository = dedup_repository
        self._match_repository = match_repository
        self._resume = resume

    async def run(self) -> list[MatchResult]:
        jobs = await self._canonical_jobs()
        jobs = self._filter_by_role(jobs)

        results = [self._score(job) for job in jobs]
        results.sort(key=lambda r: r.score, reverse=True)

        # Matching is a full snapshot: clear stale rows before writing the new set.
        await self._match_repository.clear()
        await self._match_repository.save_all(results)

        logger.info("Matched %d jobs against resume.", len(results))
        return results

    def _filter_by_role(self, jobs: list[Job]) -> list[Job]:
        if not self._resume.target_roles:
            return jobs

        filtered = [job for job in jobs if matches_any(job.title, self._resume.target_roles)]
        logger.info(
            "Role filter applied (%s): %d of %d jobs kept.",
            ", ".join(self._resume.target_roles),
            len(filtered),
            len(jobs),
        )
        return filtered

    async def _canonical_jobs(self) -> list[Job]:
        jobs = await self._job_repository.get_all()
        canonical_ids = set(await self._dedup_repository.get_canonical_job_ids())

        if canonical_ids:
            jobs = [job for job in jobs if job.id in canonical_ids]
        elif jobs:
            logger.info("No dedup results found; matching all jobs.")

        return jobs

    def _score(self, job: Job) -> MatchResult:
        result = match(self._resume, job)
        result.job_id = job.id
        return result
