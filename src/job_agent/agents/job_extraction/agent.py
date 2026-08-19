from job_agent.agents.job_extraction.parsers import get_parser
from job_agent.models import Job
from job_agent.repositories import JobRepository, RawDocumentRepository
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class JobExtractionAgent:
    """Agent 2: extracts structured jobs from unprocessed raw documents.

    Loads unprocessed ``RawDocument``s, routes each to the parser matching its
    connector type, persists the resulting ``Job``s, and marks the source
    documents processed. Missing or failing parsers are tolerated and logged.
    """

    def __init__(
        self,
        raw_repository: RawDocumentRepository,
        job_repository: JobRepository,
    ) -> None:
        self._raw_repository = raw_repository
        self._job_repository = job_repository

    async def run(self, limit: int | None = None) -> list[Job]:
        """Extract jobs from up to ``limit`` unprocessed documents."""
        documents = await self._raw_repository.get_unprocessed(limit)
        if not documents:
            logger.info("No unprocessed documents to extract.")
            return []

        jobs: list[Job] = []
        processed_ids: list[int] = []

        for document in documents:
            document_id = document.id

            parser = get_parser(document.connector_type)
            if parser is None:
                logger.warning(
                    "No parser for connector type '%s'; skipping %s",
                    document.connector_type,
                    document.url,
                )
                if document_id is not None:
                    processed_ids.append(document_id)
                continue

            try:
                job = parser.parse(document)
            except Exception:
                # Unexpected parser error: leave unprocessed so a fixed parser
                # can retry this document on the next run.
                logger.exception("Failed to parse document %s", document.url)
                continue

            if job is None:
                logger.debug("Parser skipped document %s", document.url)
                if document_id is not None:
                    processed_ids.append(document_id)
                continue

            job.raw_url = document.url
            jobs.append(job)
            if document_id is not None:
                processed_ids.append(document_id)

        saved = await self._job_repository.save_all(jobs)
        await self._raw_repository.mark_processed(processed_ids)

        logger.info(
            "Extracted %d jobs (%d new) from %d documents.",
            len(jobs),
            saved,
            len(documents),
        )
        return jobs
