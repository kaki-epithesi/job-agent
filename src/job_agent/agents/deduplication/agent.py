from collections import defaultdict

from job_agent.agents.deduplication.keys import dedup_key
from job_agent.models import DedupRecord, DedupReport, Job
from job_agent.repositories import DedupRepository, JobRepository
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


def _canonical_rank(job: Job) -> tuple[int, int, int]:
    """Sort key: prefer jobs with an apply URL and a description, then lowest id."""
    return (
        0 if job.apply_url else 1,
        0 if job.description else 1,
        job.id or 0,
    )


class DeduplicationAgent:
    """Agent 3: collapses duplicate jobs across sources.

    Groups jobs by canonical identity key, selects the most complete job as the
    canonical representative, and records the decision for downstream agents.
    """

    def __init__(
        self,
        job_repository: JobRepository,
        dedup_repository: DedupRepository,
    ) -> None:
        self._job_repository = job_repository
        self._dedup_repository = dedup_repository

    async def run(self) -> DedupReport:
        """Deduplicate all stored jobs and persist the result."""
        jobs = await self._job_repository.get_all()
        if not jobs:
            logger.info("No jobs to deduplicate.")
            return DedupReport(total=0, canonical=0, duplicates=0, groups=0)

        groups: dict[str, list[Job]] = defaultdict(list)
        for job in jobs:
            groups[dedup_key(job)].append(job)

        records: list[DedupRecord] = []
        for key, group in groups.items():
            group.sort(key=_canonical_rank)
            canonical = group[0]
            for job in group:
                records.append(
                    DedupRecord(
                        job_id=job.id,
                        dedup_key=key,
                        canonical_job_id=canonical.id,
                        is_duplicate=job.id != canonical.id,
                    )
                )

        await self._dedup_repository.save_all(records)

        duplicates = len(jobs) - len(groups)
        logger.info(
            "Deduplicated %d jobs into %d groups (%d duplicates).",
            len(jobs),
            len(groups),
            duplicates,
        )
        return DedupReport(
            total=len(jobs),
            canonical=len(groups),
            duplicates=duplicates,
            groups=len(groups),
        )
