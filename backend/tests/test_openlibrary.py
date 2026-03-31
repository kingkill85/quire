import pytest

from quire.sources.openlibrary import OpenLibrarySource

SEARCH_RESPONSE = {
    "numFound": 1,
    "docs": [
        {
            "title": "The Great Gatsby",
            "author_name": ["F. Scott Fitzgerald"],
            "first_publish_year": 1925,
            "language": ["eng"],
            "isbn": ["9780743273565"],
            "cover_i": 8231856,
            "ia": ["greatgatsby00fitz"],
            "ebook_access": "public",
        }
    ],
}


@pytest.fixture
def source():
    return OpenLibrarySource()


@pytest.mark.asyncio
async def test_search(source, httpx_mock):
    httpx_mock.add_response(
        url="https://openlibrary.org/search.json?q=great+gatsby&limit=25&fields=title%2Cauthor_name%2Cfirst_publish_year%2Clanguage%2Cisbn%2Ccover_i%2Cia%2Cebook_access",
        json=SEARCH_RESPONSE,
    )
    results = await source.search("great gatsby")
    assert len(results) == 1
    assert results[0].title == "The Great Gatsby"
    assert results[0].author == "F. Scott Fitzgerald"
    assert results[0].year == 1925
    assert results[0].source == "openlibrary"


@pytest.mark.asyncio
async def test_is_available(source, httpx_mock):
    httpx_mock.add_response(
        url="https://openlibrary.org/search.json?q=test&limit=1&fields=title",
        json={"numFound": 0, "docs": []},
    )
    assert await source.is_available() is True
