from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from core.routers import router
from core.static.stm.db import db, is_fresh


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.open(settings.gtfs_db_path)
    if not is_fresh(settings.gtfs_db_path, settings.gtfs_max_age_days):
        await db.load(settings.gtfs_static_url)
    yield
    await db.close()


app = FastAPI(
    title="Transit API",
    description="Real-time public transit data.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
