import pytest

from quire.services.cf_bypass import ExternalBypass, NoBypass


@pytest.mark.asyncio
async def test_no_bypass_returns_none():
    bypass = NoBypass()
    result = await bypass.get_cookies("https://example.com")
    assert result is None


@pytest.mark.asyncio
async def test_external_bypass(httpx_mock):
    httpx_mock.add_response(
        url="http://flaresolverr:8191/v1",
        json={
            "status": "ok",
            "solution": {
                "cookies": [
                    {"name": "cf_clearance", "value": "abc123"},
                    {"name": "__cf_bm", "value": "xyz789"},
                ],
                "userAgent": "Mozilla/5.0 Test",
            },
        },
    )
    bypass = ExternalBypass(flaresolverr_url="http://flaresolverr:8191/v1")
    result = await bypass.get_cookies("https://protected-site.com")
    assert result is not None
    assert result["cf_clearance"] == "abc123"
    assert result["user_agent"] == "Mozilla/5.0 Test"


@pytest.mark.asyncio
async def test_external_bypass_caches(httpx_mock):
    httpx_mock.add_response(
        url="http://flaresolverr:8191/v1",
        json={
            "status": "ok",
            "solution": {
                "cookies": [{"name": "cf_clearance", "value": "cached"}],
                "userAgent": "Mozilla/5.0",
            },
        },
    )
    bypass = ExternalBypass(flaresolverr_url="http://flaresolverr:8191/v1")
    result1 = await bypass.get_cookies("https://site.com/page1")
    result2 = await bypass.get_cookies("https://site.com/page2")
    assert result1 == result2
    # Only one HTTP request should have been made (second was cached)
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_external_bypass_failure(httpx_mock):
    httpx_mock.add_response(
        url="http://flaresolverr:8191/v1",
        json={"status": "error"},
    )
    bypass = ExternalBypass(flaresolverr_url="http://flaresolverr:8191/v1")
    result = await bypass.get_cookies("https://example.com")
    assert result is None
