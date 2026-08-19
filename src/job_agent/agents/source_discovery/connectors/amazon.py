import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class AmazonConnector(SourceConnector):
    """Discover jobs from the Amazon jobs public search endpoint.

    This is an unofficial JSON endpoint and may change without notice.
    """

    connector_type = "amazon"
    platform = SourcePlatform.COMPANY_CAREERS

    _BASE = "https://www.amazon.jobs"

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        query = self.config.get("query", "software engineer")
        limit = self._limit(request) or 25

        url = f"{self._BASE}/en/search.json"
        logger.info("Fetching Amazon jobs for '%s'", query)

        data = await self.http.get_json(
            url,
            params={"base_query": query, "result_limit": str(limit)},
        )
        jobs = data.get("jobs", [])

        return [self._to_document(job) for job in jobs]

    def _to_document(self, job: dict) -> RawDocument:
        path = job.get("job_path")
        return RawDocument(
            platform=self.platform,
            source="amazon",
            url=f"{self._BASE}{path}" if path else job["url_next_step"],
            title=job.get("title"),
            raw_content=json.dumps(job),
            metadata={
                "location": job.get("normalized_location"),
                "id_icims": job.get("id_icims"),
                "posted_date": job.get("posted_date"),
                "job_category": job.get("job_category"),
                "url_next_step": job.get("url_next_step"),
            },
        )
