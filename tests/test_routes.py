from fastapi.testclient import TestClient

from tests.conftest import ROUTE_ID


def test_route_detail(app_client: TestClient):
    response = app_client.get(f"/stm/routes/{ROUTE_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == ROUTE_ID
    assert isinstance(data["vehicles"], list)
    assert isinstance(data["trips"], list)


def test_route_detail_vehicles_belong_to_route(app_client: TestClient):
    data = app_client.get(f"/stm/routes/{ROUTE_ID}").json()
    assert all(v["route_id"] == ROUTE_ID for v in data["vehicles"])


def test_route_detail_trips_belong_to_route(app_client: TestClient):
    data = app_client.get(f"/stm/routes/{ROUTE_ID}").json()
    assert all(t["route_id"] == ROUTE_ID for t in data["trips"])


def test_route_detail_with_stop_times(app_client: TestClient):
    data = app_client.get(f"/stm/routes/{ROUTE_ID}?include_stop_times=true").json()
    assert any(len(t["stop_time_updates"]) > 0 for t in data["trips"])
