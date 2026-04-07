from fastapi.testclient import TestClient

from tests.conftest import ROUTE_ID


def test_trips_returns_list(app_client: TestClient):
    response = app_client.get("/stm/trips")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_trips_have_required_fields(app_client: TestClient):
    trip = app_client.get("/stm/trips").json()[0]
    for field in ("id", "trip_id", "route_id", "direction_id", "start_date", "stop_time_updates"):
        assert field in trip


def test_trips_no_stop_times_by_default(app_client: TestClient):
    trips = app_client.get("/stm/trips").json()
    assert all(t["stop_time_updates"] == [] for t in trips)


def test_trips_with_stop_times(app_client: TestClient):
    trips = app_client.get("/stm/trips?include_stop_times=true").json()
    assert any(len(t["stop_time_updates"]) > 0 for t in trips)


def test_trips_stop_time_fields(app_client: TestClient):
    trips = app_client.get(f"/stm/trips?route_id={ROUTE_ID}&include_stop_times=true").json()
    stu = next(stu for t in trips for stu in t["stop_time_updates"])
    for field in ("stop_id", "stop_sequence", "arrival_time", "departure_time"):
        assert field in stu


def test_trips_filter_by_route(app_client: TestClient):
    data = app_client.get(f"/stm/trips?route_id={ROUTE_ID}").json()
    assert all(t["route_id"] == ROUTE_ID for t in data)


def test_trips_filter_by_direction(app_client: TestClient):
    data = app_client.get("/stm/trips?direction_id=0").json()
    assert all(t["direction_id"] == 0 for t in data)
