from fastapi.testclient import TestClient

from tests.conftest import ROUTE_ID


def _get_stop_id(app_client: TestClient) -> str:
    trips = app_client.get(f"/stm/trips?route_id={ROUTE_ID}&include_stop_times=true").json()
    return trips[0]["stop_time_updates"][0]["stop_id"]


def test_static_route(app_client: TestClient):
    response = app_client.get(f"/stm/static/routes/{ROUTE_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == ROUTE_ID
    assert "route_short_name" in data
    assert "route_long_name" in data
    assert "route_type" in data


def test_static_route_not_found(app_client: TestClient):
    assert app_client.get("/stm/static/routes/INVALID_XYZ").status_code == 404


def test_static_route_trips(app_client: TestClient):
    data = app_client.get(f"/stm/static/routes/{ROUTE_ID}/trips").json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(t["route_id"] == ROUTE_ID for t in data)


def test_static_route_trips_filter_by_direction(app_client: TestClient):
    data = app_client.get(f"/stm/static/routes/{ROUTE_ID}/trips?direction_id=0").json()
    assert len(data) > 0
    assert all(t["direction_id"] == 0 for t in data)


def test_static_route_trips_unknown_route(app_client: TestClient):
    assert app_client.get("/stm/static/routes/INVALID_XYZ/trips").json() == []


def test_static_stop(app_client: TestClient):
    stop_id = _get_stop_id(app_client)
    response = app_client.get(f"/stm/static/stops/{stop_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["stop_id"] == stop_id
    assert "stop_name" in data
    assert isinstance(data["stop_lat"], float)
    assert isinstance(data["stop_lon"], float)


def test_static_stop_not_found(app_client: TestClient):
    assert app_client.get("/stm/static/stops/INVALID_XYZ").status_code == 404
