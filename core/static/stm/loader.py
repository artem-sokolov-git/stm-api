import csv
import io
import zipfile

import httpx


async def download_zip(url: str) -> bytes:
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        response = await client.get(url)
    response.raise_for_status()
    return response.content


def parse_zip(zip_bytes: bytes) -> dict[str, list[dict]]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        routes = [
            {
                "route_id": row["route_id"],
                "route_short_name": row["route_short_name"],
                "route_long_name": row["route_long_name"],
                "route_type": int(row["route_type"]),
                "route_color": row.get("route_color") or None,
            }
            for row in csv.DictReader(io.StringIO(zf.read("routes.txt").decode("utf-8-sig")))
        ]

        stops = [
            {
                "stop_id": row["stop_id"],
                "stop_name": row["stop_name"],
                "stop_lat": float(row["stop_lat"]),
                "stop_lon": float(row["stop_lon"]),
            }
            for row in csv.DictReader(io.StringIO(zf.read("stops.txt").decode("utf-8-sig")))
        ]

        trips = [
            {
                "trip_id": row["trip_id"],
                "route_id": row["route_id"],
                "direction_id": int(row["direction_id"]),
                "trip_headsign": row.get("trip_headsign") or None,
                "shape_id": row.get("shape_id") or None,
            }
            for row in csv.DictReader(io.StringIO(zf.read("trips.txt").decode("utf-8-sig")))
        ]

    return {"routes": routes, "stops": stops, "trips": trips}
