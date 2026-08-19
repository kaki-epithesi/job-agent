from pathlib import Path

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from job_agent.config import settings
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class BrowserService:
    """Manages the Playwright browser lifecycle for the LinkedIn connector."""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None

    async def __aenter__(self) -> "BrowserService":
        await self.initialize()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.shutdown()

    async def initialize(self) -> None:
        logger.info("Initializing Playwright...")

        self._playwright = await async_playwright().start()

        profile_path = Path("data") / "profiles" / settings.profile_name
        profile_path.mkdir(parents=True, exist_ok=True)

        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=settings.headless,
        )

        logger.info("Persistent browser profile loaded: %s", profile_path)

    async def new_page(self) -> Page:
        if self._context is None:
            raise RuntimeError("BrowserService not initialized.")

        pages = self._context.pages
        if pages:
            return pages[0]

        page = await self._context.new_page()
        page.set_default_timeout(settings.browser_timeout)
        return page

    async def shutdown(self) -> None:
        logger.info("Closing browser...")

        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()

        logger.info("Browser closed.")
