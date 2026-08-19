"""Read-only queries for the web UI."""

from sqlalchemy import func, select

from job_agent.repositories.tables import job_dedup, job_matches, job_rankings, jobs


def _short_date(value: str | None) -> str | None:
    return value[:10] if value else None


def _humanize(value: str | None) -> str | None:
    return value.replace("_", " ").title() if value else None


def _truncate(value: str | None, limit: int = 200) -> str | None:
    if not value:
        return None
    return value if len(value) <= limit else value[:limit].rstrip() + "…"


def _to_display(row) -> dict:
    data = dict(row)
    data["posted_at"] = _short_date(data.get("posted_at"))
    data["matched_skills"] = data.get("matched_skills") or []
    data["work_mode"] = _humanize(data.get("work_mode"))
    data["job_type"] = _humanize(data.get("job_type"))
    data["description"] = _truncate(data.get("description"))
    data["is_duplicate"] = bool(data.get("is_duplicate"))
    return data


def _base_statement(ranked_only: bool):
    statement = (
        select(
            jobs.c.id,
            jobs.c.title,
            jobs.c.company,
            jobs.c.location,
            jobs.c.apply_url,
            jobs.c.description,
            jobs.c.posted_at,
            jobs.c.job_type,
            jobs.c.work_mode,
            jobs.c.platform,
            jobs.c.source,
            job_rankings.c.rank,
            job_rankings.c.rank_score,
            job_rankings.c.match_score,
            job_rankings.c.freshness_score,
            job_matches.c.matched_skills,
            job_dedup.c.is_duplicate,
        )
        .outerjoin(job_rankings, job_rankings.c.job_id == jobs.c.id)
        .outerjoin(job_matches, job_matches.c.job_id == jobs.c.id)
        .outerjoin(job_dedup, job_dedup.c.job_id == jobs.c.id)
    )

    if ranked_only:
        statement = statement.where(job_rankings.c.job_id.is_not(None)).order_by(
            job_rankings.c.rank
        )
    else:
        statement = statement.order_by(
            job_rankings.c.rank.is_(None), job_rankings.c.rank, jobs.c.id
        )
    return statement


async def fetch_jobs(session, ranked_only: bool = False, limit: int | None = None) -> list[dict]:
    """Return jobs (all, or only ranked), with ranking/match/dedup info."""
    statement = _base_statement(ranked_only)
    if limit is not None:
        statement = statement.limit(limit)

    result = await session.execute(statement)
    return [_to_display(row) for row in result.mappings().all()]


async def fetch_stats(session) -> dict[str, int]:
    """Return count stats for the dashboard header."""
    jobs_count = (await session.execute(select(func.count()).select_from(jobs))).scalar_one()
    ranked = (await session.execute(select(func.count()).select_from(job_rankings))).scalar_one()
    matched = (await session.execute(select(func.count()).select_from(job_matches))).scalar_one()
    duplicates = (
        await session.execute(
            select(func.count()).select_from(job_dedup).where(job_dedup.c.is_duplicate == 1)
        )
    ).scalar_one()
    return {
        "jobs": jobs_count,
        "ranked": ranked,
        "matched": matched,
        "duplicates": duplicates,
    }
