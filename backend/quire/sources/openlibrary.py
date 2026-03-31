import httpx

from quire.sources.base import SearchResult, Source

SEARCH_FIELDS = "title,author_name,first_publish_year,language,isbn,cover_i,ia,ebook_access"


class OpenLibrarySource(Source):
    name = "openlibrary"
    display_name = "Open Library"

    def __init__(self):
        self._client = httpx.AsyncClient(
            base_url="https://openlibrary.org",
            headers={"User-Agent": "Quire/0.1.0 (book-search-sidecar)"},
            timeout=15.0,
        )

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        resp = await self._client.get(
            "/search.json",
            params={
                "q": query,
                "limit": max_results,
                "fields": SEARCH_FIELDS,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for doc in data.get("docs", []):
            authors = doc.get("author_name", [])
            isbns = doc.get("isbn", [])
            cover_id = doc.get("cover_i")
            ia_ids = doc.get("ia", [])

            download_url = ""
            if ia_ids:
                download_url = f"https://archive.org/download/{ia_ids[0]}"

            results.append(
                SearchResult(
                    source=self.name,
                    title=doc.get("title", "Unknown"),
                    author=authors[0] if authors else "Unknown",
                    url=download_url,
                    format="epub" if ia_ids else "metadata-only",
                    year=doc.get("first_publish_year"),
                    isbn=isbns[0] if isbns else None,
                    language=(doc.get("language") or [None])[0],
                    cover_url=f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                    if cover_id
                    else None,
                    extra={
                        "ebook_access": doc.get("ebook_access", "no_ebook"),
                        "ia_ids": ia_ids,
                    },
                )
            )
        return results

    async def download(self, url: str) -> tuple[bytes, str]:
        ia_id = url.rstrip("/").split("/")[-1]

        for ext in ["epub", "pdf"]:
            try:
                file_url = f"https://archive.org/download/{ia_id}/{ia_id}.{ext}"
                resp = await self._client.get(file_url, follow_redirects=True, timeout=120.0)
                if resp.status_code == 200:
                    return resp.content, f"{ia_id}.{ext}"
            except httpx.HTTPError:
                continue

        raise RuntimeError(f"No downloadable file found for {ia_id}")

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get(
                "/search.json", params={"q": "test", "limit": 1, "fields": "title"}
            )
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
