from fastapi.testclient import TestClient

from tests.conftest import ROUTE_ID


def _get_stop_id(app_client: TestClient) -> str:
    trips = app_client.get(f"/stm/trips?route_id={ROUTE_ID}&include_stop_times=true").json()
    return trips[0]["stop_time_updates"][0]["stop_id"]


def test_stop_departures_unknown_stop(app_client: TestClient):
    response = app_client.get("/stm/stops/INVALID_XYZ/departures")
    assert response.status_code == 200
    assert response.json() == []


def test_stop_departures_returns_list(app_client: TestClient):
    stop_id = _get_stop_id(app_client)
    response = app_client.get(f"/stm/stops/{stop_id}/departures")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_stop_departures_have_required_fields(app_client: TestClient):
    stop_id = _get_stop_id(app_client)
    departure = app_client.get(f"/stm/stops/{stop_id}/departures").json()[0]
    for field in ("trip_id", "route_id", "direction_id", "stop_sequence"):
        assert field in departure
