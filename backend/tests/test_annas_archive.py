import pytest

from quire.sources.annas_archive import AnnasArchiveSource

SEARCH_HTML = """<html><body>
<div class="mb-4">
  <a href="/md5/abc123def456" class="js-vim-focus">
    <h3>The Art of Programming</h3>
    <div class="text-sm text-gray-500">Donald Knuth, 2020, English, epub, 5.2MB</div>
  </a>
</div>
</body></html>"""


@pytest.fixture
def source():
    return AnnasArchiveSource(api_key="")


@pytest.mark.asyncio
async def test_search_scraping(source, httpx_mock):
    httpx_mock.add_response(
        url="https://annas-archive.org/search?q=art+of+programming&ext=epub",
        text=SEARCH_HTML,
    )
    results = await source.search("art of programming")
    assert len(results) == 1
    assert results[0].source == "annas_archive"
    assert results[0].title == "The Art of Programming"


@pytest.mark.asyncio
async def test_is_available(source, httpx_mock):
    httpx_mock.add_response(url="https://annas-archive.org/", status_code=200)
    assert await source.is_available() is True
