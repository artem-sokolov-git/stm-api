from pydantic import BaseModel, ConfigDict


class RouteStatic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route_id: str
    route_short_name: str
    route_long_name: str
    route_type: int
    route_color: str | None


class StopStatic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float


class TripStatic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trip_id: str
    route_id: str
    direction_id: int
    trip_headsign: str | None
    shape_id: str | None
