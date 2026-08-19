from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.mappings import (
    map_job_type,
    parse_datetime,
)
from job_agent.agents.job_extraction.parsers.registry import register_parser
from job_agent.models import Job, RawDocument, WorkMode


@register_parser
class SmartRecruitersParser(JobParser):
    connector_type = "smartrecruiters"

    def parse(self, document: RawDocument) -> Job | None:
        data = self._load_json(document)
        if not data:
            return None

        title = data.get("name")
        if not title:
            return None

        location = (data.get("location") or {}).get("fullLocation")
        work_mode = self._work_mode(data.get("location") or {})

        return Job(
            title=title,
            company=(data.get("company") or {}).get("name") or self._instance(document),
            location=location,
            apply_url=str(document.url),
            job_type=map_job_type((data.get("typeOfEmployment") or {}).get("label")),
            work_mode=work_mode,
            posted_at=parse_datetime(data.get("releasedDate")),
            source=document.source,
            platform=document.platform,
        )

    @staticmethod
    def _work_mode(location: dict) -> WorkMode:
        if location.get("remote"):
            return WorkMode.REMOTE
        if location.get("hybrid"):
            return WorkMode.HYBRID
        if location.get("city"):
            return WorkMode.ONSITE
        return WorkMode.UNKNOWN
