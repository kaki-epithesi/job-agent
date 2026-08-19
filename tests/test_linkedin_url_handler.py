from job_agent.models import LinkedInURLType
from job_agent.services.linkedin_url_handler import LinkedInURLHandler


def test_get_type_post():
    assert (
        LinkedInURLHandler.get_type(
            "https://www.linkedin.com/posts/abc_def-activity-123?utm_source=share"
        )
        == LinkedInURLType.POST
    )


def test_get_type_feed_update():
    assert (
        LinkedInURLHandler.get_type("https://www.linkedin.com/feed/update/urn:li:activity:123")
        == LinkedInURLType.POST
    )


def test_get_type_job():
    assert (
        LinkedInURLHandler.get_type("https://www.linkedin.com/jobs/view/123456")
        == LinkedInURLType.JOB
    )


def test_get_type_unknown():
    assert LinkedInURLHandler.get_type("https://example.com/foo") == LinkedInURLType.UNKNOWN


def test_unique_normalizes_and_dedupes():
    urls = [
        "https://www.linkedin.com/posts/abc-activity-1?utm_source=share",
        "https://www.linkedin.com/posts/abc-activity-1",
        "https://www.linkedin.com/jobs/view/1",
    ]
    result = LinkedInURLHandler.unique(urls, LinkedInURLType.POST)
    assert result == ["https://www.linkedin.com/posts/abc-activity-1"]
