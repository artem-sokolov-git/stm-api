from fastapi import FastAPI

from core.routers import health, vehicles

app = FastAPI(
    title="STM API",
    description="Real-time data from the Société de transport de Montréal (STM).",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(vehicles.router)
