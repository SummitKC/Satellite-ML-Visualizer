from fastapi import APIRouter

from app.schemas import SatelliteListResponse, Satellite
from app.services.tle_fetcher import fetch_active_satellites_tle, parse_orbital_parameters

router = APIRouter(prefix="/api", tags=["satellites"])


@router.get("/satellites", response_model=SatelliteListResponse)
async def get_satellites() -> SatelliteListResponse:
    """Return all active satellites with orbital parameters and cluster IDs."""

    satellites = []

    for satelliteData in await fetch_active_satellites_tle(): 
        nort_id = satelliteData[1][2:7]
        name = satelliteData[0]
        tle_line1 = satelliteData[1]
        tle_line2  = satelliteData[2]
        orbital_parameters = parse_orbital_parameters(tle_line1, tle_line2)

        currentSatellite = Satellite(norad_id=nort_id, name=name, tle_line1=tle_line1, tle_line2=tle_line2, orbital_parameters=orbital_parameters)
        satellites.append(currentSatellite)

    return SatelliteListResponse(satellites=satellites, total=len(satellites))
