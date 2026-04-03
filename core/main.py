from fastapi import FastAPI

from core.routers import router

app = FastAPI(
    title="Transit API",
    description="Real-time public transit data.",
    version="0.1.0",
)

app.include_router(router)
