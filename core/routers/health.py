from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/ping", summary="Health check")
async def healthcheck():
    return {"status": "ok"}
