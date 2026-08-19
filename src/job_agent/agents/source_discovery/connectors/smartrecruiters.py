import json

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)

_PAGE_SIZE = 100


@register_connector
class SmartRecruitersConnector(SourceConnector):
    """Discover jobs from a SmartRecruiters public postings API."""

    connector_type = "smartrecruiters"
    platform = SourcePlatform.SMARTRECRUITERS

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        company = self.config.get("company")
        if not company:
            raise DiscoveryError("SmartRecruiters connector requires 'company' in config")

        url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"
        logger.info("Fetching SmartRecruiters postings for '%s'", company)

        postings = await self._fetch_all(url)
        limit = self._limit(request)
        if limit is not None:
            postings = postings[:limit]

        return [self._to_document(company, posting) for posting in postings]

    async def _fetch_all(self, url: str) -> list[dict]:
        postings: list[dict] = []
        offset = 0
        while True:
            data = await self.http.get_json(url, params={"limit": _PAGE_SIZE, "offset": offset})
            content = data.get("content", [])
            postings.extend(content)

            total = data.get("totalFound", 0)
            offset += len(content)
            if offset >= total or not content:
                return postings

    def _to_document(self, company: str, posting: dict) -> RawDocument:
        job_id = posting.get("id")
        location = (posting.get("location") or {}).get("fullLocation")
        return RawDocument(
            platform=self.platform,
            source=f"smartrecruiters:{company}",
            url=f"https://jobs.smartrecruiters.com/{company}/{job_id}",
            title=posting.get("name"),
            raw_content=json.dumps(posting),
            metadata={
                "location": location,
                "id": job_id,
                "department": (posting.get("department") or {}).get("label"),
                "employment_type": (posting.get("typeOfEmployment") or {}).get("label"),
                "released_date": posting.get("releasedDate"),
            },
        )
