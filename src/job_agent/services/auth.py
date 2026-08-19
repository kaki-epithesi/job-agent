from job_agent.services.linkedin_client import LinkedInClient
from job_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class LinkedInAuthenticator:
    """Handles one-time LinkedIn authentication."""

    def __init__(self, client: LinkedInClient) -> None:
        self.client = client

    async def login(self) -> None:
        await self.client.goto_home()
        logger.info("Please login manually.")
        input("\nAfter logging into LinkedIn press ENTER here...")
