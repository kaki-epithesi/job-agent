from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import parse_datetime
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument


@register_parser
class GoogleParser(JobParser):
    """Best-effort parser for Google Careers (experimental connector)."""

    connector_type = "google"

    def parse(self, document: RawDocument) -> Job | None:
        data = self._load_json(document)
        if not data:
            return None

        title = data.get("title")
        if not title:
            return None

        return Job(
            title=title,
            company="Google",
            location=data.get("location"),
            apply_url=data.get("apply_url") or data.get("job_url"),
            posted_at=parse_datetime(data.get("posted_date")),
            source=document.source,
            platform=document.platform,
        )
