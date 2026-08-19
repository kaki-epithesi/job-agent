"""Deterministic resume-vs-job matching.

Baseline keyword/token-overlap scorer. Word-boundary token matching ensures
``java`` does not match ``javascript``; multi-word phrases must appear
contiguously. Semantic/embedding matching is a future enhancement.
"""

from job_agent.models import Job, MatchResult, Resume
from job_agent.utils.text import contains_phrase, matches_any

SKILL_WEIGHT = 0.5
ROLE_WEIGHT = 0.3
KEYWORD_WEIGHT = 0.1
LOCATION_WEIGHT = 0.1


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def match(resume: Resume, job: Job) -> MatchResult:
    """Score a job against a resume, returning a ``MatchResult``."""
    job_text = " ".join(filter(None, [job.title, job.description]))

    matched_skills = [skill for skill in resume.skills if contains_phrase(job_text, skill)]
    matched_roles = [role for role in resume.roles if contains_phrase(job.title, role)]
    matched_keywords = [
        keyword for keyword in resume.keywords if contains_phrase(job_text, keyword)
    ]
    location_match = matches_any(job.location, resume.locations)

    score = (
        SKILL_WEIGHT * _ratio(len(matched_skills), len(resume.skills))
        + ROLE_WEIGHT * _ratio(len(matched_roles), len(resume.roles))
        + KEYWORD_WEIGHT * _ratio(len(matched_keywords), len(resume.keywords))
        + LOCATION_WEIGHT * (1.0 if location_match else 0.0)
    )

    return MatchResult(
        score=round(score, 4),
        matched_skills=matched_skills,
        matched_roles=matched_roles,
        matched_keywords=matched_keywords,
        location_match=location_match,
    )
