import httpx

from quire.sources.base import SearchResult, Source


class ZLibrarySource(Source):
    name = "zlibrary"
    display_name = "Z-Library"

    def __init__(self, email: str = "", password: str = ""):
        self._email = email
        self._password = password
        self._base_url = "https://z-lib.id"
        self._client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Quire/0.1.0)",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30.0,
        )
        self._user_id: int | None = None
        self._user_key: str | None = None

    async def _ensure_logged_in(self) -> None:
        if self._user_id and self._user_key:
            return
        if not self._email or not self._password:
            raise RuntimeError("Z-Library credentials not configured")

        resp = await self._client.post(
            f"{self._base_url}/eapi/user/login",
            data={"email": self._email, "password": self._password},
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError("Z-Library login failed")

        user = data["user"]
        self._user_id = user["id"]
        self._user_key = user["remix_userkey"]
        self._client.cookies.set("remix_userid", str(self._user_id))
        self._client.cookies.set("remix_userkey", self._user_key)

    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        await self._ensure_logged_in()

        resp = await self._client.post(
            f"{self._base_url}/eapi/book/search",
            data={"message": query, "limit": max_results},
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for book in data.get("books", []):
            book_id = book.get("id")
            book_hash = book.get("hash", "")
            results.append(
                SearchResult(
                    source=self.name,
                    title=book.get("title", "Unknown"),
                    author=book.get("author", "Unknown"),
                    url=f"{self._base_url}/eapi/book/{book_id}/{book_hash}",
                    format=book.get("extension", "epub"),
                    size_bytes=book.get("filesize"),
                    year=self._parse_year(book.get("year")),
                    language=book.get("language"),
                    cover_url=book.get("cover"),
                    extra={"book_id": book_id, "hash": book_hash},
                )
            )
        return results

    async def download(self, url: str) -> tuple[bytes, str]:
        await self._ensure_logged_in()

        resp = await self._client.get(url, timeout=60.0)
        resp.raise_for_status()
        book_data = resp.json()

        book_id = book_data.get("book", {}).get("id") or url.split("/")[-2]
        book_hash = book_data.get("book", {}).get("hash") or url.split("/")[-1]
        extension = book_data.get("book", {}).get("extension", "epub")

        download_resp = await self._client.get(
            f"{self._base_url}/eapi/book/{book_id}/{book_hash}/send-to-{extension}",
            timeout=120.0,
            follow_redirects=True,
        )
        download_resp.raise_for_status()

        title = book_data.get("book", {}).get("title", "book")
        filename = f"{title}.{extension}"

        cd = download_resp.headers.get("content-disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')

        return download_resp.content, filename

    async def is_available(self) -> bool:
        if not self._email or not self._password:
            return False
        try:
            await self._ensure_logged_in()
            return True
        except Exception:
            return False

    @staticmethod
    def _parse_year(value) -> int | None:
        if not value:
            return None
        try:
            return int(str(value))
        except (ValueError, TypeError):
            return None
