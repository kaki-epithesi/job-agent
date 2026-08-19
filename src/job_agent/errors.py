"""Typed exception hierarchy for the platform."""


class JobAgentError(Exception):
    """Base exception for all job-agent errors."""


class ConfigurationError(JobAgentError):
    """Invalid or missing configuration."""


class AuthenticationError(JobAgentError):
    """A connector could not authenticate."""


class DiscoveryError(JobAgentError):
    """A connector failed while discovering documents."""


class UnknownConnectorError(JobAgentError):
    """A requested connector type is not registered."""
