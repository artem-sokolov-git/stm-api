from pydantic import BaseModel


class VehiclePosition(BaseModel):
    id: str
    route_id: str
    direction_id: int
    trip_id: str
    latitude: float
    longitude: float
    bearing: float
    speed: float
    current_status: int
    stop_id: str
    occupancy_status: int
    timestamp: int
