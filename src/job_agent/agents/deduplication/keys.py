"""Canonical deduplication keys.

Keys are deterministic and conservative: only near-exact matches (after
normalization) are considered duplicates. Fuzzy / semantic matching is a future
enhancement.
"""

import re

from job_agent.models import Job

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize(value: str | None) -> str:
    """Lowercase, drop punctuation, and collapse whitespace."""
    if not value:
        return ""
    return _NON_ALNUM.sub(" ", value.lower()).strip()


def dedup_key(job: Job) -> str:
    """Return the canonical identity key for a job."""
    company = normalize(job.company)
    title = normalize(job.title)
    location = normalize(job.location)
    return f"{company}|{title}|{location}"
