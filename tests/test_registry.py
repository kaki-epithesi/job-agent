import pytest

from job_agent.agents.source_discovery.connectors import registered_types
from job_agent.agents.source_discovery.connectors.registry import build_connector
from job_agent.errors import UnknownConnectorError


def test_all_connectors_registered():
    assert registered_types() == [
        "amazon",
        "ashby",
        "google",
        "greenhouse",
        "lever",
        "linkedin",
        "smartrecruiters",
        "workday",
    ]


def test_unknown_connector_raises():
    with pytest.raises(UnknownConnectorError):
        build_connector("does-not-exist", http=None)
