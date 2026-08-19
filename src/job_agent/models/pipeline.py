from pydantic import BaseModel


class PipelineReport(BaseModel):
    """Summary counts from a full pipeline run."""

    discovered: int = 0
    extracted: int = 0
    canonical: int = 0
    matched: int = 0
    ranked: int = 0
    notified: int = 0
