import re

import httpx
from bs4 import BeautifulSoup

from quire.sources.base import SearchResult, Source

MIRRORS = [
    "https://annas-archive.org",
    "https://annas-archive.li",
    "https://annas-archive.se",
]


class AnnasArchiveSource(Source):
    name = "annas_archive"
    display_name = "Anna's Archive"

    def __init__(self, api_key: str = "", mirror: str | None = None):
        self._api_key = api_key
        self._mirror = mirror or MIRRORS[0]
        self._client = httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (compatible; Quire/0.1.0)"},
            timeout=30.0,
            follow_redirects=True,
        )

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        resp = await self._client.get(
            f"{self._mirror}/search",
            params={"q": query, "ext": "epub"},
        )
        resp.raise_for_status()
        return self._parse_search_results(resp.text)

    def _parse_search_results(self, html: str) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for item in soup.select("a[href^='/md5/']"):
            href = item.get("href", "")
            md5 = href.replace("/md5/", "").strip("/")

            title_el = item.find("h3")
            title = title_el.get_text(strip=True) if title_el else "Unknown"

            meta_el = item.find("div", class_=re.compile(r"text-sm"))
            meta_text = meta_el.get_text(strip=True) if meta_el else ""

            author = "Unknown"
            year = None
            language = None
            fmt = "epub"
            size_bytes = None

            parts = [p.strip() for p in meta_text.split(",")]
            if len(parts) >= 1:
                author = parts[0]
            for part in parts[1:]:
                part = part.strip()
                if re.match(r"^\d{4}$", part):
                    year = int(part)
                elif part.lower() in (
                    "english", "german", "french", "spanish", "italian",
                    "portuguese", "russian", "chinese", "japanese",
                ):
                    language = part.lower()
                elif part.lower() in ("epub", "pdf", "mobi", "azw3", "djvu"):
                    fmt = part.lower()
                elif re.match(r"[\d.]+\s*[KMG]B", part, re.I):
                    size_bytes = self._parse_size(part)

            results.append(
                SearchResult(
                    source=self.name,
                    title=title,
                    author=author,
                    url=f"{self._mirror}/md5/{md5}",
                    format=fmt,
                    size_bytes=size_bytes,
                    year=year,
                    language=language,
                    extra={"md5": md5},
                )
            )
        return results

    async def download(self, url: str) -> tuple[bytes, str]:
        md5 = url.rstrip("/").split("/")[-1]

        if self._api_key:
            try:
                return await self._fast_download(md5)
            except Exception:
                pass

        resp = await self._client.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if any(host in href for host in ["library.lol", "libgen", "z-lib"]):
                try:
                    return await self._download_from_mirror(href)
                except Exception:
                    continue

        raise RuntimeError(f"No working download mirror found for {md5}")

    async def _fast_download(self, md5: str) -> tuple[bytes, str]:
        resp = await self._client.get(
            f"{self._mirror}/dyn/api/fast_download.json",
            params={"md5": md5},
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
        resp.raise_for_status()
        data = resp.json()
        downloads = data.get("downloads", [])
        if not downloads:
            raise RuntimeError("No fast download paths available")

        download_path = downloads[0]["path"]
        file_resp = await self._client.get(
            f"{self._mirror}{download_path}", timeout=120.0
        )
        file_resp.raise_for_status()

        filename = f"{md5}.epub"
        cd = file_resp.headers.get("content-disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')

        return file_resp.content, filename

    async def _download_from_mirror(self, mirror_url: str) -> tuple[bytes, str]:
        resp = await self._client.get(mirror_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        download_link = soup.find("a", string=re.compile(r"GET|Download", re.I))
        if not download_link:
            raise RuntimeError("No download link found on mirror page")

        direct_url = download_link["href"]
        file_resp = await self._client.get(direct_url, timeout=120.0)
        file_resp.raise_for_status()

        filename = direct_url.split("/")[-1].split("?")[0] or "book.epub"
        cd = file_resp.headers.get("content-disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')

        return file_resp.content, filename

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get(f"{self._mirror}/", timeout=10.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    @staticmethod
    def _parse_size(text: str) -> int | None:
        match = re.match(r"([\d.]+)\s*([KMG])B", text, re.I)
        if not match:
            return None
        value = float(match.group(1))
        unit = match.group(2).upper()
        multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3}
        return int(value * multipliers.get(unit, 1))
