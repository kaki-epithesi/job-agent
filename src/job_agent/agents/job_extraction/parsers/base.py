import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from job_agent.models import Job, RawDocument


class JobParser(ABC):
    """Contract for parsing a ``RawDocument`` into a structured ``Job``.

    Parsers are pure functions of the document's ``raw_content`` (no I/O). They
    are keyed by ``connector_type`` so a source's parser is unambiguous.
    """

    connector_type: ClassVar[str] = ""

    @abstractmethod
    def parse(self, document: RawDocument) -> Job | None:
        """Return a Job, or None if the document cannot be parsed."""

    @staticmethod
    def _load_json(document: RawDocument) -> dict[str, Any] | None:
        try:
            data = json.loads(document.raw_content or "{}")
        except (json.JSONDecodeError, TypeError):
            return None
        return data if isinstance(data, dict) else None

    @staticmethod
    def _instance(document: RawDocument) -> str:
        """Return the source instance (company/board) from the source id."""
        return document.source.split(":", 1)[-1]
