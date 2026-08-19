import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class GoogleConnector(SourceConnector):
    """Discover jobs from Google Careers (experimental / unverified).

    Google's careers API is undocumented and has changed frequently. This connector
    is best-effort and kept disabled by default.
    """

    connector_type = "google"
    platform = SourcePlatform.COMPANY_CAREERS

    _SEARCH_URL = "https://careers.google.com/api/v3/search/"

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        query = self.config.get("query", "software engineer")

        logger.info("Fetching Google careers for '%s'", query)
        try:
            data = await self.http.post_json(
                self._SEARCH_URL,
                json={"q": query, "page": 1},
            )
        except Exception as exc:
            raise DiscoveryError(
                "Google careers API is experimental and may have changed; "
                "see https://careers.google.com"
            ) from exc

        jobs = data.get("jobs", [])
        return [self._to_document(job) for job in jobs]

    def _to_document(self, job: dict) -> RawDocument:
        url = job.get("apply_url") or job.get("job_url")
        if not url:
            raise DiscoveryError(f"Google job missing URL: {job!r}")

        return RawDocument(
            platform=self.platform,
            source="google",
            url=url,
            title=job.get("title"),
            raw_content=json.dumps(job),
            metadata={
                "location": job.get("location"),
                "id": job.get("id"),
                "posted_date": job.get("posted_date"),
            },
        )
