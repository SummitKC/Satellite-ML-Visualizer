from fastapi import APIRouter, HTTPException

from app.schemas import ReentryPrediction, SatelliteListResponse
from app.services.reentry_cache import get_cached_predictions
from app.services.satellite_cache import get_cached_satellites

router = APIRouter(prefix="/api", tags=["satellites"])


@router.get("/satellites", response_model=SatelliteListResponse)
async def get_satellites() -> SatelliteListResponse:
    """Return the most recently cached active satellites with orbital parameters and cluster IDs."""
    cached = get_cached_satellites()
    if cached is None:
        raise HTTPException(status_code=503, detail="Satellite data is still loading, try again shortly.")
    return cached


@router.get("/satellites/{norad_id}/reentry", response_model=ReentryPrediction)
async def get_reentry_prediction(norad_id: int) -> ReentryPrediction:
    """Return the deorbit model's reentry forecast for one satellite."""
    predictions = get_cached_predictions()
    if predictions is None:
        raise HTTPException(status_code=503, detail="Reentry predictions are still loading, try again shortly.")
    return predictions.get(norad_id, ReentryPrediction(norad_id=norad_id, status="not_modelled"))
