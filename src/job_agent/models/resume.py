from pydantic import BaseModel, Field


class Resume(BaseModel):
    """The user's profile used for matching (loaded from YAML)."""

    skills: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
