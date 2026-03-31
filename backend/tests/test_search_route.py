import pytest
from fastapi.testclient import TestClient

from quire.main import app
from quire.services.download_queue import DownloadQueue
from quire.sources.base import SearchResult, Source
from quire.sources.registry import SourceRegistry


class StubSource(Source):
    name = "stub"
    display_name = "Stub"

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        if "empty" in query:
            return []
        return [
            SearchResult(
                source="stub",
                title=f"Result for {query}",
                author="Test Author",
                url="https://example.com/book",
                format="epub",
                size_bytes=1_000_000,
            )
        ]

    async def download(self, url: str) -> tuple[bytes, str]:
        return b"content", "book.epub"

    async def is_available(self) -> bool:
        return True


class FakeVerso:
    async def health_check(self):
        return True


@pytest.fixture(autouse=True)
def setup_app():
    registry = SourceRegistry()
    registry.register(StubSource())
    app.state.sources = registry
    app.state.verso = FakeVerso()
    app.state.download_queue = DownloadQueue(max_concurrent=2)


client = TestClient(app)


def test_search_all_sources():
    resp = client.get("/api/search?q=test+book")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Result for test book"


def test_search_specific_source():
    resp = client.get("/api/search?q=test+book&sources=stub")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 1


def test_search_empty_query():
    resp = client.get("/api/search?q=")
    assert resp.status_code == 422  # FastAPI validation error


def test_search_no_results():
    resp = client.get("/api/search?q=empty")
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == []
