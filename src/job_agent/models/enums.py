from enum import StrEnum


class SourcePlatform(StrEnum):
    """Supported platforms for discovering job opportunities."""

    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    GITHUB = "github"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"
    SMARTRECRUITERS = "smartrecruiters"
    ICIMS = "icims"
    WELLFOUND = "wellfound"
    COMPANY_CAREERS = "company_careers"


class JobType(StrEnum):
    """Employment type."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"
    APPRENTICESHIP = "apprenticeship"
    UNKNOWN = "unknown"


class WorkMode(StrEnum):
    """Work arrangement."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class ExperienceLevel(StrEnum):
    """Experience level required for a job."""

    INTERN = "intern"
    FRESHER = "fresher"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    LEAD = "lead"
    UNKNOWN = "unknown"


class JobStatus(StrEnum):
    """Current processing status of a discovered job."""

    DISCOVERED = "discovered"
    EXTRACTED = "extracted"
    MATCHED = "matched"
    APPLIED = "applied"
    FAILED = "failed"


class LinkedInURLType(StrEnum):
    """Supported LinkedIn URL types."""

    POST = "post"
    JOB = "job"
    PROFILE = "profile"
    COMPANY = "company"
    SEARCH = "search"
    UNKNOWN = "unknown"
