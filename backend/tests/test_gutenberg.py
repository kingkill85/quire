import pytest

from quire.sources.gutenberg import GutenbergSource

GUTENDEX_RESPONSE = {
    "count": 1,
    "results": [
        {
            "id": 1342,
            "title": "Pride and Prejudice",
            "authors": [{"name": "Austen, Jane", "birth_year": 1775, "death_year": 1817}],
            "languages": ["en"],
            "formats": {
                "application/epub+zip": "https://www.gutenberg.org/ebooks/1342.epub3.images",
                "text/html": "https://www.gutenberg.org/ebooks/1342.html.images",
            },
        }
    ],
}


@pytest.fixture
def source():
    return GutenbergSource()


@pytest.mark.asyncio
async def test_search(source, httpx_mock):
    httpx_mock.add_response(
        url="https://gutendex.com/books/?search=pride+and+prejudice",
        json=GUTENDEX_RESPONSE,
    )
    results = await source.search("pride and prejudice")
    assert len(results) == 1
    assert results[0].title == "Pride and Prejudice"
    assert results[0].author == "Jane Austen"
    assert results[0].format == "epub"
    assert "1342" in results[0].url
