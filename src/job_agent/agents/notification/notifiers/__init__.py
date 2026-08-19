"""Notification channels.

Importing this package registers all notifiers with the registry.
"""

from job_agent.agents.notification.notifiers import console, email
from job_agent.agents.notification.notifiers.base import Notifier
from job_agent.agents.notification.notifiers.registry import (
    build_notifier,
    registered_channels,
)

__all__ = [
    "Notifier",
    "build_notifier",
    "registered_channels",
    "console",
    "email",
]
