from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import parse_datetime
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument


@register_parser
class WorkdayParser(JobParser):
    """Best-effort parser for Workday postings (experimental connector)."""

    connector_type = "workday"

    def parse(self, document: RawDocument) -> Job | None:
        data = self._load_json(document)
        if not data:
            return None

        title = data.get("title")
        if not title:
            return None

        return Job(
            title=title,
            company=self._instance(document),
            location=data.get("locationsText"),
            apply_url=data.get("externalUrl") or data.get("externalJobPostingUrl"),
            posted_at=parse_datetime(data.get("postedOn")),
            source=document.source,
            platform=document.platform,
        )
