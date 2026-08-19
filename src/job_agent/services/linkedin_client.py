from urllib.parse import quote

from playwright.async_api import Page

from job_agent.config import settings
from job_agent.models import LinkedInURLType
from job_agent.services.linkedin_url_handler import LinkedInURLHandler
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class LinkedInClient:
    """High-level client for interacting with LinkedIn."""

    BASE_URL = "https://www.linkedin.com"

    def __init__(self, page: Page) -> None:
        self.page = page

    async def goto_home(self) -> None:
        logger.info("Opening LinkedIn.")
        await self.goto(self.BASE_URL)

    async def goto(self, url: str) -> None:
        logger.info("Navigating to %s", url)
        await self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=settings.browser_timeout,
        )

    async def title(self) -> str:
        return await self.page.title()

    async def current_url(self) -> str:
        return self.page.url

    async def wait(self, seconds: float) -> None:
        await self.page.wait_for_timeout(seconds * 1000)

    async def screenshot(self, path: str) -> None:
        logger.info("Saving screenshot -> %s", path)
        await self.page.screenshot(path=path, full_page=True)

    async def click(self, selector: str) -> None:
        logger.info("Clicking %s", selector)
        await self.page.locator(selector).click()

    def build_search_url(self, keyword: str) -> str:
        encoded_keyword = quote(keyword)
        return f"{self.BASE_URL}/search/results/content/?keywords={encoded_keyword}"

    async def open_search(self, keyword: str) -> None:
        url = self.build_search_url(keyword)
        logger.info("Searching LinkedIn for '%s'", keyword)
        await self.goto(url)

    async def scroll_results(self) -> None:
        logger.info("Scrolling search results (%d iterations)...", settings.max_scrolls)

        previous_height = 0
        for _ in range(settings.max_scrolls):
            current_height = await self.page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.wait(settings.request_delay)

    async def extract_post_urls(self) -> list[str]:
        anchors = await self.page.locator("a").evaluate_all(
            "elements => elements.map(element => element.href)"
        )
        logger.info("Total anchors: %d", len(anchors))

        urls = LinkedInURLHandler.unique(anchors, LinkedInURLType.POST)
        logger.info("Discovered %d unique posts.", len(urls))
        return urls

    async def is_logged_in(self) -> bool:
        await self.goto_home()
        await self.page.wait_for_timeout(3000)
        return await self.page.locator("input[placeholder*='Search']").count() > 0

    async def wait_for_feed(self) -> None:
        await self.page.wait_for_selector("main")
        await self.page.wait_for_timeout(3000)
