from job_agent.agents.resume_matching.matcher import match
from job_agent.models import Job, Resume


def make_resume() -> Resume:
    return Resume(
        skills=["python", "docker", "fastapi"],
        roles=["backend engineer", "software engineer"],
        keywords=["microservices"],
        locations=["remote"],
    )


def test_matches_skills_roles_and_location():
    job = Job(
        title="Backend Engineer",
        company="Acme",
        location="Remote",
        description="Looking for python and docker, plus microservices experience.",
    )
    result = match(make_resume(), job)

    assert result.matched_skills == ["python", "docker"]
    assert result.matched_roles == ["backend engineer"]
    assert result.matched_keywords == ["microservices"]
    assert result.location_match is True
    assert 0.0 <= result.score <= 1.0


def test_score_higher_for_better_match():
    good = match(
        make_resume(),
        Job(
            title="Backend Engineer",
            company="A",
            location="Remote",
            description="python docker fastapi microservices",
        ),
    )
    bad = match(
        make_resume(),
        Job(title="Accountant", company="B", location="Onsite", description="tax auditing"),
    )
    assert good.score > bad.score


def test_no_overlap_scores_zero():
    result = match(
        Resume(skills=["python"]),
        Job(title="SDE", company="A", description="java and c++ development"),
    )
    assert result.matched_skills == []
    assert result.score == 0.0


def test_word_boundary_matching():
    result = match(
        Resume(skills=["java"]),
        Job(title="SDE", company="A", description="javascript developer"),
    )
    assert result.matched_skills == []


def test_multi_word_phrase_contiguity():
    result = match(
        Resume(keywords=["distributed systems"]),
        Job(title="SDE", company="A", description="experience with distributed systems"),
    )
    assert result.matched_keywords == ["distributed systems"]


def test_empty_resume_matches_nothing():
    result = match(Resume(), Job(title="SDE", company="A", description="python"))
    assert result.score == 0.0
