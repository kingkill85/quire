from typing import Any

import httpx


class VersoClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=60.0,
        )

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get("/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def login(self, email: str, password: str) -> dict[str, Any]:
        resp = await self._client.post(
            "/trpc/auth.login",
            json={"email": email, "password": password},
        )
        resp.raise_for_status()
        data = resp.json()
        # tRPC response: { result: { data: ... } }
        if "result" in data:
            inner = data["result"]
            if "data" in inner:
                return inner["data"]
            return inner
        return data

    async def upload_book(
        self, file_content: bytes, filename: str, token: str
    ) -> dict[str, Any]:
        resp = await self._client.post(
            "/api/upload",
            files={"file": (filename, file_content)},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
