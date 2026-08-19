"""Ranking signal functions.

The composite rank score combines a resume-match score, a freshness score, and
a per-platform trust score. Weights are module constants for testability.
"""

import math
from datetime import UTC, datetime

from job_agent.models import SourcePlatform

MATCH_WEIGHT = 0.7
FRESHNESS_WEIGHT = 0.2
PLATFORM_WEIGHT = 0.1

FRESHNESS_HALF_LIFE_DAYS = 30.0
UNKNOWN_FRESHNESS = 0.5

PLATFORM_WEIGHTS: dict[SourcePlatform, float] = {
    SourcePlatform.COMPANY_CAREERS: 1.0,
    SourcePlatform.GREENHOUSE: 1.0,
    SourcePlatform.LEVER: 1.0,
    SourcePlatform.ASHBY: 1.0,
    SourcePlatform.WORKDAY: 1.0,
    SourcePlatform.SMARTRECRUITERS: 1.0,
    SourcePlatform.ICIMS: 1.0,
    SourcePlatform.WELLFOUND: 0.8,
    SourcePlatform.GITHUB: 0.7,
    SourcePlatform.REDDIT: 0.5,
    SourcePlatform.LINKEDIN: 0.6,
}

DEFAULT_PLATFORM_WEIGHT = 0.8


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def freshness_score(posted_at: datetime | None, now: datetime | None = None) -> float:
    """Return a recency score in (0, 1] using exponential decay."""
    if posted_at is None:
        return UNKNOWN_FRESHNESS

    reference = now or datetime.now(UTC)
    age_days = (_to_utc(reference) - _to_utc(posted_at)).total_seconds() / 86400.0
    age_days = max(age_days, 0.0)

    return math.exp(-age_days / FRESHNESS_HALF_LIFE_DAYS)


def platform_score(platform: SourcePlatform | None) -> float:
    """Return the trust weight for a source platform."""
    if platform is None:
        return DEFAULT_PLATFORM_WEIGHT
    return PLATFORM_WEIGHTS.get(platform, DEFAULT_PLATFORM_WEIGHT)


def combine(match_score: float, freshness: float, platform: float) -> float:
    """Combine signals into a single rank score in [0, 1]."""
    return MATCH_WEIGHT * match_score + FRESHNESS_WEIGHT * freshness + PLATFORM_WEIGHT * platform
