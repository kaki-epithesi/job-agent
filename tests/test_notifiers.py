import asyncio

import pytest

from job_agent.agents.notification.notifiers import (
    build_notifier,
    registered_channels,
)
from job_agent.agents.notification.notifiers.console import ConsoleNotifier
from job_agent.errors import ConfigurationError
from job_agent.models import NotificationMessage


def test_console_registered():
    assert registered_channels() == ["console", "email"]


def test_build_console_notifier():
    notifier = build_notifier("console", {})
    assert isinstance(notifier, ConsoleNotifier)
    assert notifier.channel == "console"


def test_unknown_channel_raises():
    with pytest.raises(ConfigurationError):
        build_notifier("does-not-exist", {})


def test_console_send_prints_message(capsys):
    notifier = ConsoleNotifier()
    asyncio.run(notifier.send(NotificationMessage(subject="Subject", body="Body")))

    captured = capsys.readouterr().out
    assert "Subject" in captured
    assert "Body" in captured
