from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import parse_datetime
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument


@register_parser
class AmazonParser(JobParser):
    connector_type = "amazon"

    def parse(self, document: RawDocument) -> Job | None:
        data = self._load_json(document)
        if not data:
            return None

        title = data.get("title")
        if not title:
            return None

        description = data.get("description")
        basic = data.get("basic_qualifications")
        if basic:
            description = f"{description or ''}\n\nBasic Qualifications:\n{basic}"

        return Job(
            title=title,
            company=data.get("company_name") or "Amazon",
            location=data.get("normalized_location") or data.get("location"),
            description=description,
            apply_url=data.get("url_next_step") or str(document.url),
            posted_at=parse_datetime(data.get("posted_date")),
            source=document.source,
            platform=document.platform,
        )
