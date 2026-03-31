import pytest

from quire.sources.zlibrary import ZLibrarySource

LOGIN_RESPONSE = {
    "success": 1,
    "user": {"id": 12345, "remix_userkey": "abc-key-123"},
}

SEARCH_RESPONSE = {
    "success": 1,
    "books": [
        {
            "id": 99,
            "hash": "xyz789",
            "title": "Test Novel",
            "author": "Jane Doe",
            "year": "2022",
            "language": "english",
            "extension": "epub",
            "filesize": 2_000_000,
            "cover": "https://z-lib.id/covers/99.jpg",
        }
    ],
}


@pytest.fixture
def source():
    return ZLibrarySource(email="test@test.com", password="secret")


@pytest.mark.asyncio
async def test_search(source, httpx_mock):
    httpx_mock.add_response(
        url="https://z-lib.id/eapi/user/login",
        json=LOGIN_RESPONSE,
    )
    httpx_mock.add_response(
        url="https://z-lib.id/eapi/book/search",
        json=SEARCH_RESPONSE,
    )
    results = await source.search("test novel")
    assert len(results) == 1
    assert results[0].title == "Test Novel"
    assert results[0].author == "Jane Doe"
    assert results[0].format == "epub"
    assert results[0].source == "zlibrary"
