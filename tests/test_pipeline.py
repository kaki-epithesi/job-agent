import json

from job_agent.models import RawDocument, SourcePlatform
from job_agent.pipeline import Pipeline
from job_agent.repositories import SqliteRawDocumentRepository
from job_agent.services.database import Database


def greenhouse_doc() -> RawDocument:
    return RawDocument(
        platform=SourcePlatform.GREENHOUSE,
        source="greenhouse:databricks",
        url="https://databricks.com/jobs/1",
        raw_content=json.dumps(
            {
                "title": "Software Engineer",
                "company_name": "Databricks",
                "location": {"name": "Remote"},
                "absolute_url": "https://databricks.com/jobs/1",
            }
        ),
    )


def write_sources(tmp_path) -> str:
    path = tmp_path / "sources.yaml"
    path.write_text("sources: []\n", encoding="utf-8")
    return str(path)


async def test_pipeline_runs_empty(tmp_path):
    pipeline = Pipeline(
        database_url=f"sqlite+aiosqlite:///{tmp_path}/t.db",
        sources_file=write_sources(tmp_path),
    )
    report = await pipeline.run()

    assert report.discovered == 0
    assert report.extracted == 0
    assert report.canonical == 0
    assert report.matched == 0
    assert report.ranked == 0
    assert report.notified == 0


async def test_pipeline_extracts_seeded_document(tmp_path):
    db_url = f"sqlite+aiosqlite:///{tmp_path}/t.db"

    db = Database(db_url)
    await db.initialize()
    await SqliteRawDocumentRepository(db).save_all([greenhouse_doc()])
    await db.close()

    pipeline = Pipeline(database_url=db_url, sources_file=write_sources(tmp_path))
    report = await pipeline.run()

    assert report.discovered == 0
    assert report.extracted == 1
    assert report.canonical == 1
    assert report.matched == 1
    assert report.ranked == 1
    assert report.notified == 1
