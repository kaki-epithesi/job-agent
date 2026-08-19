"""SQLAlchemy Core table definitions."""

from sqlalchemy import (
    JSON,
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

metadata = MetaData()

raw_documents = Table(
    "raw_documents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("platform", String, nullable=False),
    Column("source", String, nullable=False),
    Column("url", String, nullable=False, unique=True),
    Column("title", String, nullable=True),
    Column("raw_content", Text, nullable=True),
    Column("metadata", JSON, nullable=True),
    Column("discovered_at", String, nullable=False),
    Column("processed", Integer, nullable=False, default=0),
)

jobs = Table(
    "jobs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False),
    Column("company", String, nullable=False),
    Column("location", String, nullable=True),
    Column("description", Text, nullable=True),
    Column("apply_url", String, nullable=True),
    Column("job_type", String, nullable=True),
    Column("work_mode", String, nullable=True),
    Column("experience_level", String, nullable=True),
    Column("salary_min", Float, nullable=True),
    Column("salary_max", Float, nullable=True),
    Column("salary_currency", String, nullable=True),
    Column("posted_at", String, nullable=True),
    Column("source", String, nullable=True),
    Column("platform", String, nullable=True),
    Column("status", String, nullable=False, default="discovered"),
    Column("raw_url", String, nullable=True, unique=True),
)

job_dedup = Table(
    "job_dedup",
    metadata,
    Column("job_id", Integer, primary_key=True),
    Column("dedup_key", String, nullable=False, index=True),
    Column("canonical_job_id", Integer, nullable=False),
    Column("is_duplicate", Integer, nullable=False, default=0),
)

job_matches = Table(
    "job_matches",
    metadata,
    Column("job_id", Integer, primary_key=True),
    Column("score", Float, nullable=False),
    Column("matched_skills", JSON, nullable=True),
    Column("matched_roles", JSON, nullable=True),
    Column("matched_keywords", JSON, nullable=True),
    Column("location_match", Integer, nullable=False, default=0),
)

job_rankings = Table(
    "job_rankings",
    metadata,
    Column("job_id", Integer, primary_key=True),
    Column("rank_score", Float, nullable=False),
    Column("match_score", Float, nullable=False),
    Column("freshness_score", Float, nullable=False),
    Column("platform_score", Float, nullable=False),
    Column("rank", Integer, nullable=False),
)
