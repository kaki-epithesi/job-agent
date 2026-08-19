"""Async HTTP client with retry on transient failures."""

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from job_agent.config import settings
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)

_USER_AGENT = "job-agent/0.1 (+personal job search)"


def _is_transient(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return False


class HttpClient:
    """Wraps ``httpx.AsyncClient`` with sensible defaults and retries."""

    def __init__(self, timeout: float | None = None) -> None:
        self._timeout = timeout if timeout is not None else settings.http_timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client is not None:
            await self._client.aclose()
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("HttpClient is not open; use 'async with'.")
        return self._client

    @retry(
        retry=retry_if_exception(_is_transient),
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(settings.http_retries),
        reraise=True,
    )
    async def get_json(self, url: str, **kwargs: Any) -> Any:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    @retry(
        retry=retry_if_exception(_is_transient),
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(settings.http_retries),
        reraise=True,
    )
    async def get_text(self, url: str, **kwargs: Any) -> str:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response.text

    @retry(
        retry=retry_if_exception(_is_transient),
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(settings.http_retries),
        reraise=True,
    )
    async def post_json(self, url: str, **kwargs: Any) -> Any:
        response = await self.client.post(url, **kwargs)
        response.raise_for_status()
        return response.json()
