import re

import httpx
from bs4 import BeautifulSoup

from quire.sources.base import SearchResult, Source

MIRRORS = [
    "https://libgen.rs",
    "https://libgen.is",
    "https://libgen.st",
]


class LibGenSource(Source):
    name = "libgen"
    display_name = "Library Genesis"

    def __init__(self, mirror: str | None = None):
        self._mirror = mirror or MIRRORS[0]
        self._client = httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (compatible; Quire/0.1.0)"},
            timeout=30.0,
            follow_redirects=True,
        )

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        resp = await self._client.get(
            f"{self._mirror}/search.php",
            params={"req": query, "res": max_results, "column": "def"},
        )
        resp.raise_for_status()
        return self._parse_results(resp.text)

    def _parse_results(self, html: str) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"rules": "rows"})
        if not table:
            return []

        results = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 10:
                continue

            title_link = cells[2].find("a", id=True)
            if not title_link:
                continue
            href = title_link.get("href", "")
            md5_match = re.search(r"md5=([A-Fa-f0-9]+)", href)
            md5 = md5_match.group(1) if md5_match else ""

            size_text = cells[7].get_text(strip=True)
            size_bytes = self._parse_size(size_text)

            results.append(
                SearchResult(
                    source=self.name,
                    title=title_link.get_text(strip=True),
                    author=cells[1].get_text(strip=True),
                    url=f"{self._mirror}/get.php?md5={md5}",
                    format=cells[8].get_text(strip=True).lower(),
                    size_bytes=size_bytes,
                    year=self._parse_int(cells[4].get_text(strip=True)),
                    language=cells[6].get_text(strip=True) or None,
                    extra={"md5": md5, "publisher": cells[3].get_text(strip=True)},
                )
            )
        return results

    async def download(self, url: str) -> tuple[bytes, str]:
        resp = await self._client.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        download_link = soup.find("a", string=re.compile(r"GET", re.I))
        if not download_link:
            download_link = soup.find("a", href=re.compile(r"\.epub|\.pdf|\.mobi", re.I))

        if not download_link:
            raise RuntimeError("Could not find download link on mirror page")

        direct_url = download_link["href"]
        if not direct_url.startswith("http"):
            direct_url = f"{self._mirror}{direct_url}"

        resp = await self._client.get(direct_url, timeout=120.0)
        resp.raise_for_status()

        filename = "book"
        cd = resp.headers.get("content-disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')
        else:
            filename = direct_url.split("/")[-1].split("?")[0]

        return resp.content, filename

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get(f"{self._mirror}/", timeout=10.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    @staticmethod
    def _parse_size(text: str) -> int | None:
        match = re.match(r"([\d.]+)\s*(Kb|Mb|Gb)", text, re.I)
        if not match:
            return None
        value = float(match.group(1))
        unit = match.group(2).lower()
        multipliers = {"kb": 1024, "mb": 1024**2, "gb": 1024**3}
        return int(value * multipliers.get(unit, 1))

    @staticmethod
    def _parse_int(text: str) -> int | None:
        try:
            return int(text)
        except (ValueError, TypeError):
            return None
