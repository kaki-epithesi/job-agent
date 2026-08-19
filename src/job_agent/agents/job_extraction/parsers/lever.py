from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import (
    map_job_type,
    map_work_mode,
    parse_datetime,
)
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument


@register_parser
class LeverParser(JobParser):
    connector_type = "lever"

    def parse(self, document: RawDocument) -> Job | None:
        data = self._load_json(document)
        if not data:
            return None

        title = data.get("text")
        if not title:
            return None

        categories = data.get("categories") or {}
        return Job(
            title=title,
            company=self._instance(document),
            location=categories.get("location"),
            description=data.get("descriptionPlain") or data.get("description"),
            apply_url=data.get("applyUrl") or data.get("hostedUrl"),
            job_type=map_job_type(categories.get("commitment")),
            work_mode=map_work_mode(data.get("workplaceType")),
            posted_at=parse_datetime(data.get("createdAt")),
            source=document.source,
            platform=document.platform,
        )
