from job_agent.models.dedup import DedupRecord, DedupReport
from job_agent.models.discovery import DiscoveryRequest, RawDocument
from job_agent.models.enums import (
    ExperienceLevel,
    JobStatus,
    JobType,
    LinkedInURLType,
    SourcePlatform,
    WorkMode,
)
from job_agent.models.job import Job
from job_agent.models.match import MatchResult
from job_agent.models.notification import NotificationMessage, NotificationReport
from job_agent.models.pipeline import PipelineReport
from job_agent.models.ranking import RankedJob
from job_agent.models.resume import Resume

__all__ = [
    "DiscoveryRequest",
    "RawDocument",
    "DedupRecord",
    "DedupReport",
    "Job",
    "MatchResult",
    "NotificationMessage",
    "NotificationReport",
    "PipelineReport",
    "RankedJob",
    "Resume",
    "SourcePlatform",
    "JobType",
    "WorkMode",
    "ExperienceLevel",
    "JobStatus",
    "LinkedInURLType",
]
