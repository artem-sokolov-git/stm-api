from fastapi.testclient import TestClient


def test_ping(app_client: TestClient):
    response = app_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
