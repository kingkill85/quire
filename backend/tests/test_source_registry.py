from quire.sources.base import SearchResult, Source
from quire.sources.registry import SourceRegistry


class FakeSource(Source):
    name = "fake"
    display_name = "Fake Source"

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        return [
            SearchResult(
                source="fake",
                title="Fake Book",
                author="Fake Author",
                url="https://fake.com/book/1",
                format="epub",
                size_bytes=1_000_000,
            )
        ]

    async def download(self, url: str) -> tuple[bytes, str]:
        return b"fake-content", "fake-book.epub"

    async def is_available(self) -> bool:
        return True


def test_register_and_get_source():
    registry = SourceRegistry()
    source = FakeSource()
    registry.register(source)
    assert registry.get("fake") is source
    assert "fake" in registry.list_sources()


def test_get_unknown_source():
    registry = SourceRegistry()
    assert registry.get("nonexistent") is None
