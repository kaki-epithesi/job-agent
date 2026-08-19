import pytest

from job_agent.services.database import Database


class FakeHttp:
    """Minimal stand-in for ``HttpClient`` used in connector tests."""

    def __init__(self, json_response):
        self._json_response = json_response
        self.calls: list[tuple[str, str]] = []

    async def get_json(self, url, **kwargs):
        self.calls.append(("get", url))
        return self._json_response

    async def post_json(self, url, **kwargs):
        self.calls.append(("post", url))
        return self._json_response

    async def get_text(self, url, **kwargs):
        self.calls.append(("text", url))
        return ""


@pytest.fixture
async def database(tmp_path):
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/test.db")
    await db.initialize()
    yield db
    await db.close()


@pytest.fixture
def fake_http():
    def make(json_response):
        return FakeHttp(json_response)

    return make
