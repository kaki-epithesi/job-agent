import asyncio

import pytest

from job_agent.agents.notification.notifiers import build_notifier
from job_agent.errors import ConfigurationError
from job_agent.models import NotificationMessage


def test_email_notifier_sends(monkeypatch):
    import job_agent.agents.notification.notifiers.email as email_module

    sent = []

    class FakeSMTP:
        def __init__(self, host, port):
            self.host = host
            self.port = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            self.started = True

        def login(self, username, password):
            self.username = username
            self.password = password

        def send_message(self, msg):
            sent.append(msg)

    monkeypatch.setattr(email_module.smtplib, "SMTP", FakeSMTP)

    notifier = build_notifier(
        "email",
        {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "me@gmail.com",
            "smtp_password": "secret",
            "smtp_from": "me@gmail.com",
            "smtp_to": "me@gmail.com",
        },
    )

    asyncio.run(notifier.send(NotificationMessage(subject="Subject", body="Body")))

    assert len(sent) == 1
    assert sent[0]["Subject"] == "Subject"


def test_email_notifier_requires_config():
    notifier = build_notifier("email", {})

    with pytest.raises(ConfigurationError):
        asyncio.run(notifier.send(NotificationMessage(subject="Subject", body="Body")))
