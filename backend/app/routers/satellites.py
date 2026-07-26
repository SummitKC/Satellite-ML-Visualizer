from fastapi import APIRouter, HTTPException

from app.schemas import SatelliteListResponse
from app.services.satellite_cache import get_cached_satellites

router = APIRouter(prefix="/api", tags=["satellites"])


@router.get("/satellites", response_model=SatelliteListResponse)
async def get_satellites() -> SatelliteListResponse:
    """Return the most recently cached active satellites with orbital parameters and cluster IDs."""
    cached = get_cached_satellites()
    if cached is None:
        raise HTTPException(status_code=503, detail="Satellite data is still loading, try again shortly.")
    return cached