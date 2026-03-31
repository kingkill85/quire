import pytest

from quire.services.verso import VersoClient


@pytest.fixture
def verso_client():
    return VersoClient(base_url="http://verso:3000")


@pytest.mark.asyncio
async def test_health_check(verso_client, httpx_mock):
    httpx_mock.add_response(
        url="http://verso:3000/health",
        json={"status": "ok"},
    )
    result = await verso_client.health_check()
    assert result is True


@pytest.mark.asyncio
async def test_health_check_failure(verso_client, httpx_mock):
    httpx_mock.add_response(url="http://verso:3000/health", status_code=500)
    result = await verso_client.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_upload_book(verso_client, httpx_mock):
    httpx_mock.add_response(
        url="http://verso:3000/api/upload",
        json={"book": {"id": "abc-123", "title": "Test Book"}},
        status_code=201,
    )
    result = await verso_client.upload_book(
        file_content=b"fake-epub-content",
        filename="test.epub",
        token="test-jwt-token",
    )
    assert result["book"]["id"] == "abc-123"

    request = httpx_mock.get_request()
    assert request.headers["authorization"] == "Bearer test-jwt-token"
