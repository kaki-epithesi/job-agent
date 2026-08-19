from job_agent.agents.notification.formatter import format_notification
from job_agent.models import Job, MatchResult, RankedJob


def test_format_notification():
    ranked = [
        RankedJob(
            job_id=1,
            rank_score=0.8,
            match_score=0.7,
            freshness_score=0.5,
            platform_score=1.0,
            rank=1,
        )
    ]
    jobs = {
        1: Job(
            id=1,
            title="Backend Engineer",
            company="Acme",
            location="Remote",
            apply_url="https://apply.example/1",
        )
    }
    matches = {1: MatchResult(job_id=1, score=0.7, matched_skills=["python"])}

    message = format_notification(ranked, jobs, matches)

    assert message.job_count == 1
    assert message.subject == "Job Agent — Top 1 Matches"
    assert "Backend Engineer" in message.body
    assert "https://apply.example/1" in message.body
    assert "python" in message.body


def test_format_notification_skips_missing_job():
    ranked = [
        RankedJob(
            job_id=999,
            rank_score=0.5,
            match_score=0.5,
            freshness_score=0.5,
            platform_score=1.0,
            rank=1,
        )
    ]
    message = format_notification(ranked, {}, {})
    assert message.body == ""
