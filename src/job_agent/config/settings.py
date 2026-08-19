from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    # HTTP
    http_timeout: float = Field(default=30.0, alias="HTTP_TIMEOUT")
    http_retries: int = Field(default=3, alias="HTTP_RETRIES")

    # Browser (experimental LinkedIn connector only)
    headless: bool = Field(default=False, alias="HEADLESS")
    browser_timeout: int = Field(default=30_000, alias="BROWSER_TIMEOUT")
    profile_name: str = Field(default="linkedin", alias="PROFILE_NAME")

    # Discovery
    sources_file: str | None = Field(default=None, alias="SOURCES_FILE")
    request_delay: float = Field(default=3.0, alias="REQUEST_DELAY")
    max_scrolls: int = Field(default=25, alias="MAX_SCROLLS")
    max_concurrency: int = Field(default=4, alias="MAX_CONCURRENCY")

    # Matching
    resume_file: str | None = Field(default=None, alias="RESUME_FILE")

    # Email (SMTP)
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")
    smtp_to: str | None = Field(default=None, alias="SMTP_TO")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///data/database.db",
        alias="DATABASE_URL",
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Web dashboard
    web_refresh_seconds: int = Field(default=20, alias="WEB_REFRESH_SECONDS")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
