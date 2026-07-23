from fastapi import APIRouter

from app.schemas import SatelliteListResponse

router = APIRouter(prefix="/api", tags=["satellites"])


@router.get("/satellites", response_model=SatelliteListResponse)
async def get_satellites() -> SatelliteListResponse:
    """Return all active satellites with orbital parameters and cluster IDs.

    TODO (Step 2):
      - Call services.tle_fetcher.fetch_active_satellites_tle()
      - Parse each TLE pair with services.tle_fetcher.parse_orbital_parameters()
      - Build the feature matrix and call services.clustering.cluster_satellites()
      - Assemble Satellite objects (with cluster_id set) and return them
    """
    return SatelliteListResponse(satellites=[], total=0)
