from fastapi import APIRouter, HTTPException

from core.models.stm.static import RouteStatic, StopStatic, TripStatic
from core.services.stm import static as static_service

router = APIRouter(prefix="/static")


@router.get("/routes/{route_id}", response_model=RouteStatic, summary="Route static info")
async def get_route(route_id: str) -> RouteStatic:
    route = await static_service.fetch_route(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.get("/stops/{stop_id}", response_model=StopStatic, summary="Stop static info")
async def get_stop(stop_id: str) -> StopStatic:
    stop = await static_service.fetch_stop(stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop


@router.get("/routes/{route_id}/trips", response_model=list[TripStatic], summary="Trips for a route")
async def get_route_trips(route_id: str, direction_id: int | None = None) -> list[TripStatic]:
    return await static_service.fetch_trips_by_route(route_id, direction_id)
