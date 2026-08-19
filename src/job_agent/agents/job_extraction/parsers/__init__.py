"""Job parsers.

Importing this package registers all parsers with the registry.
"""

from job_agent.agents.job_extraction.parsers import (
    amazon,
    ashby,
    google,
    greenhouse,
    lever,
    smartrecruiters,
    workday,
)
from job_agent.agents.job_extraction.parsers.base import JobParser
from job_agent.agents.job_extraction.parsers.registry import (
    get_parser,
    registered_types,
)

__all__ = [
    "JobParser",
    "get_parser",
    "registered_types",
    "amazon",
    "ashby",
    "google",
    "greenhouse",
    "lever",
    "smartrecruiters",
    "workday",
]
