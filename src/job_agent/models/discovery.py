from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from job_agent.models.enums import JobType, SourcePlatform


class DiscoveryRequest(BaseModel):
    """A single discovery task handed to a connector.

    ``source`` identifies the configured source instance (e.g. ``greenhouse:databricks``).
    The remaining fields are optional filters. Connectors honor ``limit`` today; the
    other filters are reserved for downstream refinement.
    """

    source: str
    locations: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    job_types: list[JobType] = Field(default_factory=list)
    limit: int | None = None


class RawDocument(BaseModel):
    """A raw, unparsed job posting discovered by a connector.

    ``raw_content`` holds the original HTML/JSON payload for Agent 2 (Job Extraction)
    to parse. ``metadata`` carries source-specific context (department, location, ids).
    """

    platform: SourcePlatform
    source: str
    url: HttpUrl
    title: str | None = None
    raw_content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    @property
    def connector_type(self) -> str:
        """The connector/parser type, derived from the source id.

        E.g. ``greenhouse:databricks`` -> ``greenhouse``; ``amazon`` -> ``amazon``.
        """
        return self.source.split(":", 1)[0]
