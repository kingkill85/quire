from xml.etree import ElementTree as ET

import httpx

from quire.sources.base import SearchResult, Source

ATOM_NS = "{http://www.w3.org/2005/Atom}"


class StandardEbooksSource(Source):
    name = "standard_ebooks"
    display_name = "Standard Ebooks"

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={"User-Agent": "Quire/0.1.0 (book-search-sidecar)"},
            timeout=15.0,
            follow_redirects=True,
        )
        self._feed_url = "https://standardebooks.org/feeds/opds"

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        resp = await self._client.get(self._feed_url)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)

        query_lower = query.lower()
        results = []

        for entry in root.findall(f"{ATOM_NS}entry"):
            title = (entry.findtext(f"{ATOM_NS}title") or "").strip()
            author_el = entry.find(f"{ATOM_NS}author")
            author = (
                (author_el.findtext(f"{ATOM_NS}name") or "Unknown").strip()
                if author_el
                else "Unknown"
            )

            if query_lower not in title.lower() and query_lower not in author.lower():
                continue

            epub_url = ""
            for link in entry.findall(f"{ATOM_NS}link"):
                if link.get("type") == "application/epub+zip":
                    epub_url = link.get("href", "")
                    break

            if not epub_url:
                continue

            results.append(
                SearchResult(
                    source=self.name,
                    title=title,
                    author=author,
                    url=epub_url,
                    format="epub",
                    language="en",
                )
            )

            if len(results) >= max_results:
                break

        return results

    async def download(self, url: str) -> tuple[bytes, str]:
        if not url.startswith("http"):
            url = f"https://standardebooks.org{url}"
        resp = await self._client.get(url, timeout=60.0)
        resp.raise_for_status()
        filename = url.split("/")[-1] or "book.epub"
        return resp.content, filename

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get(self._feed_url, timeout=10.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
