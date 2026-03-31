import httpx

from quire.sources.base import SearchResult, Source


class GutenbergSource(Source):
    name = "gutenberg"
    display_name = "Project Gutenberg"

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={"User-Agent": "Quire/0.1.0 (book-search-sidecar)"},
            timeout=15.0,
            follow_redirects=True,
        )

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        resp = await self._client.get(
            "https://gutendex.com/books/",
            params={"search": query},
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for book in data.get("results", [])[:max_results]:
            authors = book.get("authors", [])
            author_name = "Unknown"
            if authors:
                name = authors[0].get("name", "Unknown")
                parts = name.split(", ")
                author_name = " ".join(reversed(parts)) if len(parts) == 2 else name

            formats = book.get("formats", {})
            epub_url = formats.get("application/epub+zip", "")

            if not epub_url:
                continue

            results.append(
                SearchResult(
                    source=self.name,
                    title=book.get("title", "Unknown"),
                    author=author_name,
                    url=epub_url,
                    format="epub",
                    language=(book.get("languages") or [None])[0],
                    extra={"gutenberg_id": book["id"]},
                )
            )
        return results

    async def download(self, url: str) -> tuple[bytes, str]:
        resp = await self._client.get(url, timeout=120.0)
        resp.raise_for_status()
        filename = url.split("/")[-1] or "book.epub"
        return resp.content, filename

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get("https://gutendex.com/books/?search=test")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
