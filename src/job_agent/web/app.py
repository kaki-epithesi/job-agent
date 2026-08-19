import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from job_agent.config import settings
from job_agent.services.database import Database
from job_agent.web import queries

db = Database()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

_run_state: dict = {
    "status": "idle",
    "started_at": None,
    "finished_at": None,
    "error": None,
}


async def _default_run() -> None:
    """Run the full pipeline (overridable in tests)."""
    from job_agent.pipeline import Pipeline

    await Pipeline().run()


async def _run_pipeline_task() -> None:
    try:
        await _default_run()
        _run_state.update(status="completed", error=None)
    except Exception as exc:  # noqa: BLE001
        _run_state.update(status="failed", error=str(exc))
    finally:
        _run_state["finished_at"] = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.initialize()
    yield
    await db.close()


app = FastAPI(title="Job Agent", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, view: str = "all"):
    ranked_only = view == "ranked"
    async with db.session_factory() as session:
        jobs = await queries.fetch_jobs(session, ranked_only=ranked_only)
        stats = await queries.fetch_stats(session)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "jobs": jobs,
            "stats": stats,
            "view": view,
            "refresh_seconds": settings.web_refresh_seconds,
        },
    )


@app.get("/api/jobs")
async def api_jobs(view: str = "all"):
    async with db.session_factory() as session:
        return await queries.fetch_jobs(session, ranked_only=(view == "ranked"))


@app.get("/api/status")
async def api_status():
    return _run_state


@app.post("/run")
async def trigger_run():
    if _run_state["status"] != "running":
        _run_state.update(
            status="running",
            started_at=time.time(),
            finished_at=None,
            error=None,
        )
        asyncio.create_task(_run_pipeline_task())
    return _run_state
