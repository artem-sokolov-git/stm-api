from fastapi import HTTPException
from google.transit import gtfs_realtime_pb2

from core.client import stm_client
from core.config import settings
from core.filters.trips import TripFilter
from core.models.trips import StopTimeUpdate, TripUpdate


async def fetch_trip_updates(filters: TripFilter) -> list[TripUpdate]:
    async with stm_client() as client:
        response = await client.get(settings.trip_updates_endpoint)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="STM API error")

    feed = gtfs_realtime_pb2.FeedMessage()  # ty: ignore[unresolved-attribute]
    feed.ParseFromString(response.content)

    def build_stop_times(entity: gtfs_realtime_pb2.FeedEntity) -> list[StopTimeUpdate]:  # ty: ignore[unresolved-attribute]
        if not filters.include_stop_times:
            return []
        return [
            StopTimeUpdate(
                stop_sequence=stu.stop_sequence,
                stop_id=stu.stop_id,
                arrival_time=stu.arrival.time if stu.HasField("arrival") else None,
                arrival_delay=stu.arrival.delay if stu.HasField("arrival") else None,
                departure_time=stu.departure.time
                if stu.HasField("departure")
                else None,
                departure_delay=stu.departure.delay
                if stu.HasField("departure")
                else None,
            )
            for stu in entity.trip_update.stop_time_update
        ]

    trips = [
        TripUpdate(
            id=entity.id,
            trip_id=entity.trip_update.trip.trip_id,
            route_id=entity.trip_update.trip.route_id,
            direction_id=entity.trip_update.trip.direction_id,
            start_date=entity.trip_update.trip.start_date,
            stop_time_updates=build_stop_times(entity),
        )
        for entity in feed.entity
        if entity.HasField("trip_update")
    ]

    if filters.route_id is not None:
        trips = [t for t in trips if t.route_id == filters.route_id]
    if filters.direction_id is not None:
        trips = [t for t in trips if t.direction_id == filters.direction_id]

    return trips
