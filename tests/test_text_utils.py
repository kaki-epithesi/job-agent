from job_agent.agents.source_discovery.filters import location_matches
from job_agent.utils.text import contains_phrase, matches_any, tokenize


def test_tokenize():
    assert tokenize("San Francisco, CA") == ["san", "francisco", "ca"]
    assert tokenize(None) == []
    assert tokenize("C++") == ["c++"]


def test_contains_phrase():
    assert contains_phrase("looking for python and docker", "python") is True
    assert contains_phrase("javascript developer", "java") is False
    assert contains_phrase("distributed systems experience", "distributed systems") is True


def test_matches_any():
    assert matches_any("Bengaluru, India", ["india", "remote"]) is True
    assert matches_any("San Francisco, USA", ["india", "remote"]) is False
    assert matches_any(None, ["india"]) is False


def test_location_matches_no_preferences():
    assert location_matches("USA", []) is True


def test_location_matches_matches():
    assert location_matches("Bengaluru, Karnataka, India", ["india"]) is True
    assert location_matches("Remote", ["remote"]) is True


def test_location_matches_no_match():
    assert location_matches("San Francisco, USA", ["india", "remote"]) is False
    assert location_matches(None, ["india"]) is False
