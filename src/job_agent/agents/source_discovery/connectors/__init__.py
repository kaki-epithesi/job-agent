"""Source connectors.

Importing this package registers all connectors with the registry.
"""

from job_agent.agents.source_discovery.connectors import (
    amazon,
    ashby,
    google,
    greenhouse,
    lever,
    linkedin,
    smartrecruiters,
    workday,
)
from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import (
    build_connector,
    get_connector_class,
    registered_types,
)

__all__ = [
    "SourceConnector",
    "build_connector",
    "get_connector_class",
    "registered_types",
    "amazon",
    "ashby",
    "google",
    "greenhouse",
    "lever",
    "linkedin",
    "smartrecruiters",
    "workday",
]
