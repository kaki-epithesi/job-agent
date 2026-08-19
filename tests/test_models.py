from job_agent.models import DiscoveryRequest, RawDocument, SourcePlatform


def test_discovery_request_defaults():
    request = DiscoveryRequest(source="greenhouse:databricks")
    assert request.source == "greenhouse:databricks"
    assert request.locations == []
    assert request.keywords == []
    assert request.job_types == []
    assert request.limit is None


def test_raw_document_defaults():
    doc = RawDocument(
        platform=SourcePlatform.GREENHOUSE,
        source="greenhouse:databricks",
        url="https://example.com/jobs/1",
    )
    assert doc.title is None
    assert doc.raw_content is None
    assert doc.metadata == {}
    assert doc.discovered_at is not None


def test_raw_document_requires_url():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        RawDocument(
            platform=SourcePlatform.GREENHOUSE,
            source="x",
            url="not-a-url",
        )
