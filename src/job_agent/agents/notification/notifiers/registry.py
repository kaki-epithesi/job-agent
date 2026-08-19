"""Notifier registry.

Concrete notifiers self-register via ``@register_notifier`` and are looked up
by ``channel``. Agent 6 never imports a concrete notifier directly.
"""

from collections.abc import Mapping
from typing import Any

from job_agent.agents.notification.notifiers.base import Notifier
from job_agent.errors import ConfigurationError

_registry: dict[str, type[Notifier]] = {}


def register_notifier(cls: type[Notifier]) -> type[Notifier]:
    if not cls.channel:
        raise ValueError(f"{cls.__name__} must define channel")
    _registry[cls.channel] = cls
    return cls


def get_notifier_class(channel: str) -> type[Notifier]:
    try:
        return _registry[channel]
    except KeyError:
        raise ConfigurationError(f"Unknown notifier channel: {channel!r}") from None


def build_notifier(
    channel: str,
    config: Mapping[str, Any] | None = None,
) -> Notifier:
    """Instantiate a notifier by channel name."""
    cls = get_notifier_class(channel)
    return cls(config=config)


def registered_channels() -> list[str]:
    return sorted(_registry)
