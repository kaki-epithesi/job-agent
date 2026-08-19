import math
from datetime import UTC, datetime, timedelta

import pytest

from job_agent.agents.ranking.ranker import (
    FRESHNESS_HALF_LIFE_DAYS,
    combine,
    freshness_score,
    platform_score,
)
from job_agent.models import SourcePlatform


def test_freshness_now_is_one():
    now = datetime(2026, 1, 10, tzinfo=UTC)
    assert freshness_score(datetime(2026, 1, 10, tzinfo=UTC), now=now) == 1.0


def test_freshness_decays_by_half_life():
    now = datetime(2026, 1, 10, tzinfo=UTC)
    old = now - timedelta(days=FRESHNESS_HALF_LIFE_DAYS)
    assert freshness_score(old, now=now) == pytest.approx(math.exp(-1), rel=1e-6)


def test_freshness_unknown_is_neutral():
    assert freshness_score(None) == 0.5


def test_freshness_handles_naive_datetime():
    now = datetime(2026, 1, 10, tzinfo=UTC)
    naive = datetime(2026, 1, 9)
    assert freshness_score(naive, now=now) == pytest.approx(math.exp(-1 / 30), rel=1e-6)


def test_platform_score():
    assert platform_score(SourcePlatform.GREENHOUSE) == 1.0
    assert platform_score(SourcePlatform.LINKEDIN) == 0.6
    assert platform_score(None) == 0.8


def test_combine():
    assert combine(1.0, 1.0, 1.0) == pytest.approx(1.0)
    assert combine(0.5, 0.5, 1.0) == pytest.approx(0.7 * 0.5 + 0.2 * 0.5 + 0.1 * 1.0)
