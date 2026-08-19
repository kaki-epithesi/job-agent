from job_agent.utils.text import matches_any


def location_matches(location: str | None, preferences: list[str]) -> bool:
    """Return True if ``location`` matches any preference (or no preferences set)."""
    if not preferences:
        return True
    return matches_any(location, preferences)
