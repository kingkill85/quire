from fastapi.testclient import TestClient

from quire.main import app


class FakeVerso:
    async def health_check(self):
        return True


def test_health():
    app.state.verso = FakeVerso()
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["verso"] == "connected"
