from dataclasses import dataclass

from fastapi import Query


@dataclass
class TripFilter:
    route_id: str | None = Query(None, description="Filter by route (e.g. 10, 80, 747)")
    direction_id: int | None = Query(None, description="Filter by direction (0 or 1)")
    include_stop_times: bool = Query(
        False, description="Include stop_time_updates in response"
    )
