from pydantic import BaseModel, Field


class MatchResult(BaseModel):
    """The match score for a single job against the resume."""

    job_id: int | None = None
    score: float
    matched_skills: list[str] = Field(default_factory=list)
    matched_roles: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    location_match: bool = False
