import pytest

from quire.sources.libgen import LibGenSource

SEARCH_HTML = """<html><body>
<table rules="rows" width="100%">
<tr><th>ID</th><th>Author</th><th>Title</th><th>Publisher</th><th>Year</th><th>Pages</th><th>Language</th><th>Size</th><th>Extension</th><th>Mirror</th></tr>
<tr><td>1</td><td><a>Author One</a></td>
<td><a id="1" href="/book/index.php?md5=ABC123">Test Book Title</a></td>
<td>Publisher</td><td>2020</td><td>100</td><td>English</td>
<td>5 Mb</td><td>epub</td>
<td><a href="/get.php?md5=ABC123">[1]</a></td></tr>
</table>
</body></html>"""


@pytest.fixture
def source():
    return LibGenSource()


@pytest.mark.asyncio
async def test_search(source, httpx_mock):
    httpx_mock.add_response(
        url="https://libgen.rs/search.php?req=test+book&res=25&column=def",
        text=SEARCH_HTML,
    )
    results = await source.search("test book")
    assert len(results) == 1
    assert results[0].title == "Test Book Title"
    assert results[0].author == "Author One"
    assert results[0].format == "epub"
    assert "ABC123" in results[0].url


@pytest.mark.asyncio
async def test_is_available(source, httpx_mock):
    httpx_mock.add_response(url="https://libgen.rs/", status_code=200)
    assert await source.is_available() is True
