from job_agent.agents.notification.notifiers.base import Notifier
from job_agent.agents.notification.notifiers.registry import register_notifier
from job_agent.models import NotificationMessage


@register_notifier
class ConsoleNotifier(Notifier):
    """Prints the digest to stdout."""

    channel = "console"

    async def send(self, message: NotificationMessage) -> None:
        print(message.subject)
        print(message.body)
