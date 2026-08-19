import asyncio

from job_agent.agents.source_discovery.connectors import build_connector
from job_agent.agents.source_discovery.filters import location_matches
from job_agent.config import settings
from job_agent.config.sources import SourceConfig, load_sources
from job_agent.models import DiscoveryRequest, RawDocument
from job_agent.repositories import RawDocumentRepository
from job_agent.services.http import HttpClient
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class SourceDiscoveryAgent:
    """Agent 1: discovers raw job postings from configured source connectors.

    The agent is connector-agnostic: it reads source configuration, builds a
    ``DiscoveryRequest`` per enabled source, runs each connector concurrently,
    filters by location, deduplicates results, and persists them via an
    injected repository.
    """

    def __init__(
        self,
        http: HttpClient,
        repository: RawDocumentRepository,
        locations: list[str] | None = None,
    ) -> None:
        self._http = http
        self._repository = repository
        self._locations = locations or []

    async def run(
        self,
        sources: list[SourceConfig] | None = None,
    ) -> list[RawDocument]:
        """Run discovery for the given sources (or all enabled sources)."""
        source_configs = sources if sources is not None else self._enabled_sources()

        if not source_configs:
            logger.info("No enabled sources configured.")
            return []

        semaphore = asyncio.Semaphore(settings.max_concurrency)
        tasks = [self._discover(source, semaphore) for source in source_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        documents: list[RawDocument] = []
        for source, result in zip(source_configs, results):
            if isinstance(result, BaseException):
                logger.error("Source '%s' failed: %s", source.id, result)
                continue
            documents.extend(result)

        if self._locations:
            documents = [
                document
                for document in documents
                if location_matches(document.metadata.get("location"), self._locations)
            ]
            logger.info(
                "Location filter applied (%s): %d documents kept.",
                ", ".join(self._locations),
                len(documents),
            )

        unique = self._deduplicate(documents)
        saved = await self._repository.save_all(unique)

        logger.info(
            "Discovered %d documents (%d new) across %d sources.",
            len(unique),
            saved,
            len(source_configs),
        )
        return unique

    async def _discover(
        self,
        source: SourceConfig,
        semaphore: asyncio.Semaphore,
    ) -> list[RawDocument]:
        async with semaphore:
            connector = build_connector(source.type, self._http, source.config)
            request = DiscoveryRequest(source=source.id, locations=self._locations)
            logger.info("Running connector '%s'", source.id)
            return await connector.discover(request)

    @staticmethod
    def _enabled_sources() -> list[SourceConfig]:
        sources = load_sources()
        return [s for s in sources.sources if s.enabled]

    @staticmethod
    def _deduplicate(documents: list[RawDocument]) -> list[RawDocument]:
        unique: dict[str, RawDocument] = {}
        for doc in documents:
            unique[str(doc.url)] = doc
        return list(unique.values())
