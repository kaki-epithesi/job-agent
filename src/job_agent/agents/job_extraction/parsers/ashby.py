from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import (
    map_job_type,
    map_work_mode,
    parse_datetime,
)
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument


@register_parser
class AshbyParser(JobParser):
    connector_type = "ashby"

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
            location=data.get("location"),
            description=data.get("descriptionPlain") or data.get("descriptionHtml"),
            apply_url=data.get("applyUrl") or data.get("jobUrl"),
            job_type=map_job_type(data.get("employmentType")),
            work_mode=map_work_mode(data.get("workplaceType")),
            posted_at=parse_datetime(data.get("publishedAt")),
            source=document.source,
            platform=document.platform,
        )
