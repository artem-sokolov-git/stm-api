from fastapi.testclient import TestClient

from tests.conftest import ROUTE_ID


def test_vehicles_returns_list(app_client: TestClient):
    response = app_client.get("/stm/vehicles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_vehicles_have_required_fields(app_client: TestClient):
    vehicle = app_client.get("/stm/vehicles").json()[0]
    for field in ("id", "route_id", "direction_id", "trip_id", "latitude", "longitude", "timestamp"):
        assert field in vehicle


def test_vehicles_filter_by_route(app_client: TestClient):
    data = app_client.get(f"/stm/vehicles?route_id={ROUTE_ID}").json()
    assert all(v["route_id"] == ROUTE_ID for v in data)


def test_vehicles_filter_by_direction_0(app_client: TestClient):
    data = app_client.get("/stm/vehicles?direction_id=0").json()
    assert all(v["direction_id"] == 0 for v in data)


def test_vehicles_filter_by_direction_1(app_client: TestClient):
    data = app_client.get("/stm/vehicles?direction_id=1").json()
    assert all(v["direction_id"] == 1 for v in data)


def test_vehicles_combined_filter(app_client: TestClient):
    data = app_client.get(f"/stm/vehicles?route_id={ROUTE_ID}&direction_id=0").json()
    assert all(v["route_id"] == ROUTE_ID and v["direction_id"] == 0 for v in data)
