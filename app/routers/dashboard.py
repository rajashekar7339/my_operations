from fastapi import APIRouter

from app.services.dashboard import fetch_dashboard

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
async def get_dashboard():
    return await fetch_dashboard()
