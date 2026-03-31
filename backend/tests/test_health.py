from fastapi.testclient import TestClient

from quire.main import app
from quire.services.download_queue import DownloadQueue
from quire.sources.registry import SourceRegistry


class FakeVerso:
    async def health_check(self):
        return True


def test_health():
    app.state.verso = FakeVerso()
    app.state.sources = SourceRegistry()
    app.state.download_queue = DownloadQueue(max_concurrent=2)
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["verso"] == "connected"


def test_config():
    app.state.verso = FakeVerso()
    app.state.sources = SourceRegistry()
    app.state.download_queue = DownloadQueue(max_concurrent=2)
    client = TestClient(app)
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "verso_url" in data
