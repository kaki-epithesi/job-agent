import logging
import sys

from job_agent.config import settings

_configured = False


def setup_logger(name: str) -> logging.Logger:
    """Return a configured logger, configuring root logging exactly once."""
    global _configured

    if not _configured:
        logging.basicConfig(
            level=settings.log_level.upper(),
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=sys.stdout,
        )
        _configured = True

    return logging.getLogger(name)
