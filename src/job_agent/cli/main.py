import asyncio
from pathlib import Path

import typer

from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)

app = typer.Typer(
    name="job-agent",
    help="Job Agent — extensible job discovery platform.",
    no_args_is_help=True,
)


@app.command()
def discover(
    sources_file: str | None = typer.Option(
        None, "--sources-file", help="Path to a sources YAML file."
    ),
) -> None:
    """Run source discovery and print discovered raw documents."""
    asyncio.run(_discover(sources_file))


@app.command()
def login() -> None:
    """Authenticate to LinkedIn once (persists a browser profile)."""
    asyncio.run(_login())


@app.command()
def extract(
    limit: int | None = typer.Option(None, "--limit", help="Max documents to process."),
) -> None:
    """Extract structured jobs from unprocessed raw documents."""
    asyncio.run(_extract(limit))


@app.command()
def dedupe() -> None:
    """Collapse duplicate jobs and record canonical representatives."""
    asyncio.run(_dedupe())


@app.command()
def match(
    limit: int | None = typer.Option(None, "--limit", help="Show top N matches."),
    resume_file: str | None = typer.Option(
        None, "--resume-file", help="Path to a resume YAML file."
    ),
) -> None:
    """Score canonical jobs against the resume and show the top matches."""
    asyncio.run(_match(limit, resume_file))


@app.command()
def rank(
    limit: int | None = typer.Option(None, "--limit", help="Show top N results."),
) -> None:
    """Rank matched jobs by match, freshness, and platform signals."""
    asyncio.run(_rank(limit))


@app.command()
def notify(
    top: int = typer.Option(10, "--top", help="Number of top jobs to notify."),
) -> None:
    """Send the top-ranked jobs to enabled notification channels."""
    asyncio.run(_notify(top))


@app.command()
def run(
    sources_file: str | None = typer.Option(
        None, "--sources-file", help="Path to a sources YAML file."
    ),
    resume_file: str | None = typer.Option(
        None, "--resume-file", help="Path to a resume YAML file."
    ),
    top: int = typer.Option(10, "--top", help="Number of top jobs to notify."),
) -> None:
    """Run the full pipeline: discover -> extract -> dedupe -> match -> rank -> notify."""
    asyncio.run(_run(sources_file, resume_file, top))


@app.command("db-init")
def db_init() -> None:
    """Create database tables."""
    asyncio.run(_init_db())


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind address."),
    port: int = typer.Option(8000, "--port", help="Port to listen on."),
) -> None:
    """Start the web dashboard."""
    import uvicorn

    from job_agent.web.app import app

    uvicorn.run(app, host=host, port=port, log_level="info")


async def _discover(sources_file: str | None) -> None:
    from job_agent.agents.source_discovery import SourceDiscoveryAgent
    from job_agent.config.sources import load_sources
    from job_agent.repositories import SqliteRawDocumentRepository
    from job_agent.services.database import Database
    from job_agent.services.http import HttpClient

    path = None if sources_file is None else Path(sources_file)
    config = load_sources(path)
    source_configs = [s for s in config.sources if s.enabled]

    async with HttpClient() as http:
        db = Database()
        await db.initialize()
        try:
            repository = SqliteRawDocumentRepository(db)
            agent = SourceDiscoveryAgent(http, repository, locations=config.locations)
            documents = await agent.run(source_configs)
        finally:
            await db.close()

    for doc in documents:
        typer.echo(f"{doc.platform.value:16} | {doc.title or '-'} | {doc.url}")
    typer.echo(f"\nDiscovered {len(documents)} documents.")


async def _login() -> None:
    from job_agent.services.auth import LinkedInAuthenticator
    from job_agent.services.browser import BrowserService
    from job_agent.services.linkedin_client import LinkedInClient

    async with BrowserService() as browser:
        page = await browser.new_page()
        client = LinkedInClient(page)
        await LinkedInAuthenticator(client).login()


async def _extract(limit: int | None) -> None:
    from job_agent.agents.job_extraction import JobExtractionAgent
    from job_agent.repositories import (
        SqliteJobRepository,
        SqliteRawDocumentRepository,
    )
    from job_agent.services.database import Database

    db = Database()
    await db.initialize()
    try:
        agent = JobExtractionAgent(
            raw_repository=SqliteRawDocumentRepository(db),
            job_repository=SqliteJobRepository(db),
        )
        jobs = await agent.run(limit)
    finally:
        await db.close()

    for job in jobs:
        typer.echo(
            f"{job.company:24} | {job.title} | {job.location or '-'} | {job.apply_url or '-'}"
        )
    typer.echo(f"\nExtracted {len(jobs)} jobs.")


async def _dedupe() -> None:
    from job_agent.agents.deduplication import DeduplicationAgent
    from job_agent.repositories import SqliteDedupRepository, SqliteJobRepository
    from job_agent.services.database import Database

    db = Database()
    await db.initialize()
    try:
        agent = DeduplicationAgent(
            job_repository=SqliteJobRepository(db),
            dedup_repository=SqliteDedupRepository(db),
        )
        report = await agent.run()
    finally:
        await db.close()

    typer.echo(
        f"Deduplicated {report.total} jobs -> {report.canonical} canonical "
        f"({report.duplicates} duplicates across {report.groups} groups)."
    )


async def _match(limit: int | None, resume_file: str | None) -> None:
    from pathlib import Path

    from job_agent.agents.resume_matching import ResumeMatchingAgent
    from job_agent.config.resume import load_resume
    from job_agent.repositories import (
        SqliteDedupRepository,
        SqliteJobRepository,
        SqliteMatchRepository,
    )
    from job_agent.services.database import Database

    resume = load_resume(Path(resume_file) if resume_file else None)

    db = Database()
    await db.initialize()
    try:
        job_repo = SqliteJobRepository(db)
        agent = ResumeMatchingAgent(
            job_repository=job_repo,
            dedup_repository=SqliteDedupRepository(db),
            match_repository=SqliteMatchRepository(db),
            resume=resume,
        )
        results = await agent.run()
        jobs_by_id = {job.id: job for job in await job_repo.get_all()}
    finally:
        await db.close()

    top = results[:limit] if limit else results
    for rank, result in enumerate(top, 1):
        job = jobs_by_id.get(result.job_id)
        name = f"{job.company} | {job.title}" if job else f"job #{result.job_id}"
        skills = ", ".join(result.matched_skills) or "-"
        typer.echo(f"{rank:3}. [{result.score:.2f}] {name} | skills: {skills}")
    typer.echo(f"\nMatched {len(results)} jobs.")


async def _rank(limit: int | None) -> None:
    from job_agent.agents.ranking import RankingAgent
    from job_agent.repositories import (
        SqliteDedupRepository,
        SqliteJobRepository,
        SqliteMatchRepository,
        SqliteRankingRepository,
    )
    from job_agent.services.database import Database

    db = Database()
    await db.initialize()
    try:
        job_repo = SqliteJobRepository(db)
        agent = RankingAgent(
            job_repository=job_repo,
            dedup_repository=SqliteDedupRepository(db),
            match_repository=SqliteMatchRepository(db),
            ranking_repository=SqliteRankingRepository(db),
        )
        results = await agent.run()
        jobs_by_id = {job.id: job for job in await job_repo.get_all()}
    finally:
        await db.close()

    top = results[:limit] if limit else results
    for rank, result in enumerate(top, 1):
        job = jobs_by_id.get(result.job_id)
        name = f"{job.company} | {job.title}" if job else f"job #{result.job_id}"
        typer.echo(
            f"{rank:3}. [{result.rank_score:.2f}] {name} | "
            f"match={result.match_score:.2f} fresh={result.freshness_score:.2f}"
        )
    typer.echo(f"\nRanked {len(results)} jobs.")


async def _notify(top: int) -> None:
    from job_agent.agents.notification import NotificationAgent
    from job_agent.agents.notification.notifiers import build_notifier
    from job_agent.config.notifications import load_notifications
    from job_agent.repositories import (
        SqliteJobRepository,
        SqliteMatchRepository,
        SqliteRankingRepository,
    )
    from job_agent.services.database import Database

    config = load_notifications()
    notifiers = [
        build_notifier(channel.type, channel.config)
        for channel in config.channels
        if channel.enabled
    ]

    db = Database()
    await db.initialize()
    try:
        agent = NotificationAgent(
            notifiers=notifiers,
            ranking_repository=SqliteRankingRepository(db),
            job_repository=SqliteJobRepository(db),
            match_repository=SqliteMatchRepository(db),
            top_n=top,
        )
        report = await agent.run()
    finally:
        await db.close()

    typer.echo(
        f"\nNotified {report.delivered} channel(s) ({', '.join(report.channels) or 'none'})."
    )


async def _run(sources_file: str | None, resume_file: str | None, top: int) -> None:
    from job_agent.pipeline import Pipeline

    report = await Pipeline(
        sources_file=sources_file,
        resume_file=resume_file,
        top_n=top,
    ).run()

    typer.echo(
        f"discovered={report.discovered} extracted={report.extracted} "
        f"canonical={report.canonical} matched={report.matched} "
        f"ranked={report.ranked} notified={report.notified}"
    )


async def _init_db() -> None:
    from job_agent.services.database import Database

    db = Database()
    try:
        await db.initialize()
    finally:
        await db.close()
    typer.echo("Database initialized.")


def main() -> None:
    app()
