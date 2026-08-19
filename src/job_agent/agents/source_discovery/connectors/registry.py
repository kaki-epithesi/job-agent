"""Connector registry.

Concrete connectors self-register via the ``@register_connector`` decorator.
Agent 1 and the scheduler look connectors up by ``type`` only, so adding a new
connector never requires touching pipeline code.
"""

from collections.abc import Mapping
from typing import Any

from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.errors import UnknownConnectorError
from job_agent.services.http import HttpClient

_registry: dict[str, type[SourceConnector]] = {}


def register_connector(cls: type[SourceConnector]) -> type[SourceConnector]:
    """Register a connector class under its ``connector_type``."""
    if not cls.connector_type:
        raise ValueError(f"{cls.__name__} must define connector_type")
    _registry[cls.connector_type] = cls
    return cls


def get_connector_class(connector_type: str) -> type[SourceConnector]:
    try:
        return _registry[connector_type]
    except KeyError:
        raise UnknownConnectorError(f"Unknown connector type: {connector_type!r}") from None


def registered_types() -> list[str]:
    return sorted(_registry)


def build_connector(
    connector_type: str,
    http: HttpClient,
    config: Mapping[str, Any] | None = None,
) -> SourceConnector:
    """Instantiate a connector by type."""
    cls = get_connector_class(connector_type)
    return cls(http=http, config=config)
