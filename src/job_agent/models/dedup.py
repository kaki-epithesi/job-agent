from pydantic import BaseModel


class DedupRecord(BaseModel):
    """A deduplication decision for a single job."""

    job_id: int
    dedup_key: str
    canonical_job_id: int
    is_duplicate: bool


class DedupReport(BaseModel):
    """Summary of a deduplication run."""

    total: int
    canonical: int
    duplicates: int
    groups: int
