import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class WorkdayConnector(SourceConnector):
    """Discover jobs from a Workday career site (experimental).

    Workday is per-tenant: each company uses a different ``*.myworkdayjobs.com``
    host and a site id, and many tenants sit behind bot protection. Enable this
    connector per company by supplying the correct ``host``, ``tenant``, and
    ``site`` (see README). Not enabled by default.
    """

    connector_type = "workday"
    platform = SourcePlatform.WORKDAY

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        host = self.config.get("host")
        tenant = self.config.get("tenant")
        if not host or not tenant:
            raise DiscoveryError("Workday connector requires 'host' and 'tenant' in config")

        site = self.config.get("site", "External")
        endpoint = self.config.get("endpoint", "jobs")
        search_text = self.config.get("search_text", "")
        limit = self.config.get("limit", 20)

        url = f"https://{host}/wday/cxs/{tenant}/{site}/{endpoint}"
        body = {
            "appliedFacets": {},
            "limit": limit,
            "offset": 0,
            "searchText": search_text,
        }

        logger.info("Fetching Workday jobs for tenant '%s'", tenant)
        try:
            data = await self.http.post_json(url, json=body)
        except Exception as exc:
            raise DiscoveryError(
                f"Workday discovery failed for tenant '{tenant}' "
                f"({url}). Workday is per-tenant: confirm the host/site are "
                f"correct and the tenant is live. Original error: {exc}"
            ) from exc

        postings = data.get("jobPostings", [])
        return [self._to_document(tenant, posting) for posting in postings]

    def _to_document(self, tenant: str, posting: dict) -> RawDocument:
        url = posting.get("externalUrl") or posting.get("externalJobPostingUrl")
        if not url:
            raise DiscoveryError(f"Workday posting missing URL: {posting!r}")

        location = posting.get("locationsText")
        return RawDocument(
            platform=self.platform,
            source=f"workday:{tenant}",
            url=url,
            title=posting.get("title"),
            raw_content=json.dumps(posting),
            metadata={
                "location": location,
                "posted_on": posting.get("postedOn"),
                "job_id": posting.get("jobId"),
            },
        )
