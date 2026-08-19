from urllib.parse import urlparse

from job_agent.models import LinkedInURLType


class LinkedInURLHandler:
    """Utility class for LinkedIn URL handling."""

    URL_PATTERNS = {
        LinkedInURLType.POST: (
            "/posts/",
            "/feed/update/",
        ),
        LinkedInURLType.JOB: ("/jobs/view/",),
        LinkedInURLType.PROFILE: ("/in/",),
        LinkedInURLType.COMPANY: ("/company/",),
        LinkedInURLType.SEARCH: ("/search/results/",),
    }

    @classmethod
    def normalize(cls, url: str) -> str:
        """Normalize a LinkedIn URL (strip query/fragment)."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    @classmethod
    def get_type(cls, url: str) -> LinkedInURLType:
        """Return the LinkedIn URL type."""
        normalized = cls.normalize(url)
        for url_type, patterns in cls.URL_PATTERNS.items():
            if any(pattern in normalized for pattern in patterns):
                return url_type
        return LinkedInURLType.UNKNOWN

    @classmethod
    def is_type(cls, url: str, url_type: LinkedInURLType) -> bool:
        """Check if a URL belongs to the given type."""
        return cls.get_type(url) == url_type

    @classmethod
    def unique(cls, urls: list[str], url_type: LinkedInURLType) -> list[str]:
        """Return unique normalized URLs of a specific type."""
        return sorted({cls.normalize(url) for url in urls if cls.is_type(url, url_type)})
