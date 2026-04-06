from sqlalchemy import select

from core.models.stm.static import RouteStatic, StopStatic, TripStatic
from core.static.stm.db import db
from core.static.stm.models import Route, Stop, Trip


async def fetch_route(route_id: str) -> RouteStatic | None:
    async with db.session() as session:
        row = await session.get(Route, route_id)
    return RouteStatic.model_validate(row) if row else None


async def fetch_stop(stop_id: str) -> StopStatic | None:
    async with db.session() as session:
        row = await session.get(Stop, stop_id)
    return StopStatic.model_validate(row) if row else None


async def fetch_trips_by_route(route_id: str, direction_id: int | None = None) -> list[TripStatic]:
    async with db.session() as session:
        query = select(Trip).where(Trip.route_id == route_id)
        if direction_id is not None:
            query = query.where(Trip.direction_id == direction_id)
        result = await session.execute(query)
        rows = result.scalars().all()
    return [TripStatic.model_validate(row) for row in rows]
