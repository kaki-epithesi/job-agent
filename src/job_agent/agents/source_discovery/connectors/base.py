from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar

from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.services.http import HttpClient


class SourceConnector(ABC):
    """Base contract every source connector implements.

    Connectors receive their transport and per-source ``config`` through the
    constructor (dependency injection). They read task-level filters from the
    ``DiscoveryRequest``. Agent 1 only ever talks to this interface.
    """

    connector_type: ClassVar[str] = ""
    platform: ClassVar[SourcePlatform] = SourcePlatform.COMPANY_CAREERS

    def __init__(
        self,
        http: HttpClient,
        config: Mapping[str, Any] | None = None,
    ) -> None:
        self.http = http
        self.config: dict[str, Any] = dict(config or {})

    def _limit(self, request: DiscoveryRequest) -> int | None:
        """Resolve the result limit from the request, then connector config."""
        if request.limit is not None:
            return request.limit
        return self.config.get("limit")

    @abstractmethod
    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        """Discover raw job postings for the given request."""
