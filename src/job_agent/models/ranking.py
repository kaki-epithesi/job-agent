from pydantic import BaseModel


class RankedJob(BaseModel):
    """A job's final ranking, combining match, freshness, and platform signals."""

    job_id: int
    rank_score: float
    match_score: float
    freshness_score: float
    platform_score: float
    rank: int = 0
