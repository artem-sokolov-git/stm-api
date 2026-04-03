from fastapi import APIRouter

from core.routers import health
from core.routers.stm import router as stm_router

router = APIRouter()

router.include_router(health.router)
router.include_router(stm_router)
