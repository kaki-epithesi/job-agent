import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class AshbyConnector(SourceConnector):
    """Discover jobs from the Ashby public job-board API."""

    connector_type = "ashby"
    platform = SourcePlatform.ASHBY

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        board = self.config.get("board")
        if not board:
            raise DiscoveryError("Ashby connector requires 'board' in config")

        url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
        logger.info("Fetching Ashby board '%s'", board)

        data = await self.http.get_json(url)
        jobs = data.get("jobs", [])
        limit = self._limit(request)
        if limit is not None:
            jobs = jobs[:limit]

        return [self._to_document(board, job) for job in jobs]

    def _to_document(self, board: str, job: dict) -> RawDocument:
        return RawDocument(
            platform=self.platform,
            source=f"ashby:{board}",
            url=job["jobUrl"],
            title=job.get("title"),
            raw_content=json.dumps(job),
            metadata={
                "location": job.get("location"),
                "department": job.get("department"),
                "team": job.get("team"),
                "employment_type": job.get("employmentType"),
                "workplace_type": job.get("workplaceType"),
                "apply_url": job.get("applyUrl"),
                "published_at": job.get("publishedAt"),
                "id": job.get("id"),
            },
        )
