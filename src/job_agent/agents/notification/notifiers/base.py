from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar

from job_agent.models import NotificationMessage


class Notifier(ABC):
    """Base contract for notification channels.

    Notifiers are dumb adapters: they receive a formatted ``NotificationMessage``
    and deliver it. A channel is added by subclassing and registering with
    ``@register_notifier``.
    """

    channel: ClassVar[str] = ""

    def __init__(self, config: Mapping[str, Any] | None = None) -> None:
        self.config: dict[str, Any] = dict(config or {})

    @abstractmethod
    async def send(self, message: NotificationMessage) -> None:
        """Deliver the message through this channel."""
