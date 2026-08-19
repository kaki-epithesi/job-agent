from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import parse_datetime
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument


@register_parser
class GreenhouseParser(JobParser):
    connector_type = "greenhouse"

    def parse(self, document: RawDocument) -> Job | None:
        data = self._load_json(document)
        if not data:
            return None

        title = data.get("title")
        if not title:
            return None

        location = (data.get("location") or {}).get("name")
        return Job(
            title=title,
            company=data.get("company_name") or self._instance(document),
            location=location,
            description=data.get("content"),
            apply_url=data.get("absolute_url") or str(document.url),
            posted_at=parse_datetime(data.get("updated_at") or data.get("first_published")),
            source=document.source,
            platform=document.platform,
        )
