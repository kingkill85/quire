from abc import ABC, abstractmethod
from typing import Any

import httpx


class CfBypass(ABC):
    @abstractmethod
    async def get_cookies(self, url: str) -> dict[str, Any] | None:
        """Returns dict with cookies + user_agent, or None if bypass not available."""
        ...


class NoBypass(CfBypass):
    async def get_cookies(self, url: str) -> dict[str, Any] | None:
        return None


class ExternalBypass(CfBypass):
    """Uses FlareSolverr to bypass Cloudflare challenges."""

    def __init__(self, flaresolverr_url: str = "http://flaresolverr:8191/v1"):
        self._url = flaresolverr_url
        self._client = httpx.AsyncClient(timeout=60.0)
        self._cache: dict[str, dict[str, Any]] = {}

    async def get_cookies(self, url: str) -> dict[str, Any] | None:
        domain = url.split("//")[-1].split("/")[0]
        if domain in self._cache:
            return self._cache[domain]

        try:
            resp = await self._client.post(
                self._url,
                json={
                    "cmd": "request.get",
                    "url": url,
                    "maxTimeout": 30000,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                return None

            solution = data.get("solution", {})
            cookies = {c["name"]: c["value"] for c in solution.get("cookies", [])}
            result = {
                **cookies,
                "user_agent": solution.get("userAgent", ""),
            }

            self._cache[domain] = result
            return result
        except Exception:
            return None

    def clear_cache(self, domain: str | None = None) -> None:
        if domain:
            self._cache.pop(domain, None)
        else:
            self._cache.clear()


class InternalBypass(CfBypass):
    """Uses SeleniumBase CDP driver for built-in Cloudflare bypass."""

    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}

    async def get_cookies(self, url: str) -> dict[str, Any] | None:
        domain = url.split("//")[-1].split("/")[0]
        if domain in self._cache:
            return self._cache[domain]

        try:
            import asyncio

            result = await asyncio.to_thread(self._solve_with_selenium, url)
            if result:
                self._cache[domain] = result
            return result
        except ImportError:
            raise RuntimeError(
                "SeleniumBase not installed. Install with: pip install quire[bypass]"
            )
        except Exception:
            return None

    def _solve_with_selenium(self, url: str) -> dict[str, Any] | None:
        from seleniumbase import SB

        with SB(uc=True, headless=True) as sb:
            sb.activate_cdp_mode(url)
            sb.sleep(3)

            page_source = sb.get_page_source().lower()
            if "just a moment" in page_source or "verify you are human" in page_source:
                try:
                    sb.cdp.click_if_visible("input[type='checkbox']")
                    sb.sleep(5)
                except Exception:
                    pass

            cookies = sb.get_cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            if "cf_clearance" not in cookie_dict:
                return None

            return {
                **cookie_dict,
                "user_agent": sb.get_user_agent(),
            }

    def clear_cache(self, domain: str | None = None) -> None:
        if domain:
            self._cache.pop(domain, None)
        else:
            self._cache.clear()
