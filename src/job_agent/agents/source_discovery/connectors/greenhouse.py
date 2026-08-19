import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class GreenhouseConnector(SourceConnector):
    """Discover jobs from a Greenhouse public board API."""

    connector_type = "greenhouse"
    platform = SourcePlatform.GREENHOUSE

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        board = self.config.get("board")
        if not board:
            raise DiscoveryError("Greenhouse connector requires 'board' in config")

        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
        logger.info("Fetching Greenhouse board '%s'", board)

        data = await self.http.get_json(url)
        jobs = data.get("jobs", [])
        limit = self._limit(request)
        if limit is not None:
            jobs = jobs[:limit]

        return [self._to_document(board, job) for job in jobs]

    def _to_document(self, board: str, job: dict) -> RawDocument:
        location = (job.get("location") or {}).get("name")
        return RawDocument(
            platform=self.platform,
            source=f"greenhouse:{board}",
            url=job["absolute_url"],
            title=job.get("title"),
            raw_content=json.dumps(job),
            metadata={
                "location": location,
                "id": job.get("id"),
                "updated_at": job.get("updated_at"),
            },
        )
