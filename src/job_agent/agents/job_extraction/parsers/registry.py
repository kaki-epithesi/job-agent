"""Parser registry.

Concrete parsers self-register via the ``@register_parser`` decorator and are
looked up by ``connector_type`` (derived from ``RawDocument.source``).
"""

from job_agent.agents.job_extraction.parsers.base import JobParser

_registry: dict[str, type[JobParser]] = {}


def register_parser(cls: type[JobParser]) -> type[JobParser]:
    if not cls.connector_type:
        raise ValueError(f"{cls.__name__} must define connector_type")
    _registry[cls.connector_type] = cls
    return cls


def get_parser(connector_type: str) -> JobParser | None:
    """Return a parser for the connector type, or None if none is registered."""
    cls = _registry.get(connector_type)
    return cls() if cls is not None else None


def registered_types() -> list[str]:
    return sorted(_registry)
