from job_agent.models import Job, MatchResult, NotificationMessage, RankedJob


def format_notification(
    ranked: list[RankedJob],
    jobs_by_id: dict[int, Job],
    matches_by_id: dict[int, MatchResult],
) -> NotificationMessage:
    """Render ranked jobs into a human-readable digest."""
    lines: list[str] = []

    for item in ranked:
        job = jobs_by_id.get(item.job_id)
        if job is None:
            continue

        lines.append(f"{item.rank}. [{item.rank_score:.2f}] {job.company} — {job.title}")
        if job.location:
            lines.append(f"   {job.location}")
        if job.apply_url:
            lines.append(f"   {job.apply_url}")

        match = matches_by_id.get(item.job_id)
        if match and match.matched_skills:
            lines.append(f"   matched: {', '.join(match.matched_skills)}")

        lines.append("")

    subject = f"Job Agent — Top {len(ranked)} Matches"
    body = "\n".join(lines).rstrip()
    return NotificationMessage(subject=subject, body=body, job_count=len(ranked))
