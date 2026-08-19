import asyncio
import smtplib
from email.message import EmailMessage

from job_agent.agents.notification.notifiers.base import Notifier
from job_agent.agents.notification.notifiers.registry import register_notifier
from job_agent.config import settings
from job_agent.errors import ConfigurationError
from job_agent.models import NotificationMessage
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_notifier
class EmailNotifier(Notifier):
    """Sends the digest via SMTP (e.g. Gmail on port 587).

    Credentials come from ``SMTP_*`` settings (.env) or channel config.
    """

    channel = "email"

    async def send(self, message: NotificationMessage) -> None:
        await asyncio.to_thread(self._send_sync, message)

    def _send_sync(self, message: NotificationMessage) -> None:
        host = self.config.get("smtp_host") or settings.smtp_host
        port = int(self.config.get("smtp_port") or settings.smtp_port)
        username = self.config.get("smtp_user") or settings.smtp_user
        password = self.config.get("smtp_password") or settings.smtp_password
        from_addr = self.config.get("smtp_from") or settings.smtp_from or username
        to_addr = self.config.get("smtp_to") or settings.smtp_to

        if not (host and username and password and to_addr):
            raise ConfigurationError(
                "Email notifier requires SMTP_HOST, SMTP_USER, SMTP_PASSWORD, "
                "and SMTP_TO to be configured."
            )

        msg = EmailMessage()
        msg["Subject"] = message.subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg.set_content(message.body)

        logger.info("Sending email to %s via %s:%s", to_addr, host, port)
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
