import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class LeverConnector(SourceConnector):
    """Discover jobs from the Lever public postings API."""

    connector_type = "lever"
    platform = SourcePlatform.LEVER

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        company = self.config.get("company")
        if not company:
            raise DiscoveryError("Lever connector requires 'company' in config")

        url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        logger.info("Fetching Lever postings for '%s'", company)

        data = await self.http.get_json(url)
        limit = self._limit(request)
        if limit is not None:
            data = data[:limit]

        return [self._to_document(company, posting) for posting in data]

    def _to_document(self, company: str, posting: dict) -> RawDocument:
        categories = posting.get("categories") or {}
        return RawDocument(
            platform=self.platform,
            source=f"lever:{company}",
            url=posting["hostedUrl"],
            title=posting.get("text"),
            raw_content=json.dumps(posting),
            metadata={
                "location": categories.get("location"),
                "team": categories.get("team"),
                "commitment": categories.get("commitment"),
                "apply_url": posting.get("applyUrl"),
                "id": posting.get("id"),
            },
        )
