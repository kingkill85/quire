import base64
from typing import Any

import httpx


class VersoClient:
    def __init__(self, base_url: str, email: str, app_password: str):
        self.base_url = base_url.rstrip("/")
        credentials = base64.b64encode(f"{email}:{app_password}".encode()).decode()
        self._auth_header = f"Basic {credentials}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": self._auth_header},
            timeout=60.0,
        )

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get("/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def upload_book(self, file_content: bytes, filename: str) -> dict[str, Any]:
        resp = await self._client.post(
            "/api/upload",
            files={"file": (filename, file_content)},
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_books(self, page: int = 1, limit: int = 50) -> dict[str, Any]:
        resp = await self._client.post(
            "/trpc/books.list",
            json={"json": {"page": page, "limit": limit}},
        )
        resp.raise_for_status()
        return resp.json()["result"]["data"]["json"]

    async def close(self):
        await self._client.aclose()
