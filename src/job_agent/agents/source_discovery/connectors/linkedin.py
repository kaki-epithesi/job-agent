from job_agent.agents.source_discovery.connectors.base import SourceConnector
from job_agent.agents.source_discovery.connectors.registry import register_connector
from job_agent.errors import AuthenticationError, DiscoveryError
from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


@register_connector
class LinkedInConnector(SourceConnector):
    """Discover LinkedIn hiring posts (experimental).

    Requires a persistent authenticated browser profile (run ``job-agent login``
    first). Kept disabled by default; reliability is limited by LinkedIn's
    anti-bot protections. Uses Playwright internally.
    """

    connector_type = "linkedin"
    platform = SourcePlatform.LINKEDIN

    async def discover(self, request: DiscoveryRequest) -> list[RawDocument]:
        keywords = self.config.get("keywords", [])
        if not keywords:
            raise DiscoveryError("LinkedIn connector requires 'keywords' in config")

        from job_agent.services.browser import BrowserService
        from job_agent.services.linkedin_client import LinkedInClient

        documents: list[RawDocument] = []

        async with BrowserService() as browser:
            page = await browser.new_page()
            client = LinkedInClient(page)

            if not await client.is_logged_in():
                raise AuthenticationError(
                    "LinkedIn session not found. Run 'job-agent login' first."
                )

            for keyword in keywords:
                await client.open_search(keyword)
                await client.wait_for_feed()
                await client.scroll_results()
                urls = await client.extract_post_urls()

                for url in urls:
                    documents.append(
                        RawDocument(
                            platform=self.platform,
                            source="linkedin",
                            url=url,
                            metadata={"keyword": keyword},
                        )
                    )

        return documents
