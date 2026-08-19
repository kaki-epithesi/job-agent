from pydantic import BaseModel, Field


class NotificationMessage(BaseModel):
    """A formatted digest ready to be delivered to notifiers."""

    subject: str
    body: str
    job_count: int = 0


class NotificationReport(BaseModel):
    """Result of a notification run."""

    delivered: int = 0
    failed: int = 0
    channels: list[str] = Field(default_factory=list)
