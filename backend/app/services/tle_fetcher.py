"""Fetches and parses TLE data from CelesTrak."""

import logging
import math

import httpx
from app.config import get_settings
from app.schemas import OrbitalParameters
from sgp4.api import Satrec, SGP4_ERRORS
from sgp4.conveniences import sat_epoch_datetime

logger = logging.getLogger(__name__)


async def fetch_active_satellites_tle() -> list[tuple[str, str, str]]:
    """Fetch active satellite TLEs from CelesTrak."""
    settings = get_settings()
    tle_list: list[tuple[str, str, str]] = []
    current_name = None
    current_line1 = None

    try: 
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.celestrak_tle_url)
            response.raise_for_status()

        for line in response.iter_lines(): 
            cleaned_line = line.strip()

            if not cleaned_line: 
                continue

            if cleaned_line.startswith("1 "): 
                current_line1 = cleaned_line

            # End of current data 
            elif cleaned_line.startswith("2 "): 

                if current_line1 is None or current_name is None:
                    continue

                tle_list.append((current_name, current_line1, cleaned_line))

                # Reset name, and lines
                current_name = None
                current_line1 = None

            else: 
                current_name = cleaned_line                

        return tle_list
    except httpx.HTTPStatusError as e:
        logger.error(
            "Error response %s while requesting %s.",
            e.response.status_code,
            e.request.url,
        )
        raise
    except httpx.RequestError as e:
        logger.error("An error occurred while requesting %s.", e.request.url)
        raise


def parse_orbital_parameters(line1: str, line2: str) -> OrbitalParameters:
    """Derive orbital parameters from a TLE pair using sgp4."""
    earth_radius = 6378.137
    minutes_per_day = 1440.0

    current_satellite = Satrec.twoline2rv(line1, line2)

    if current_satellite.error != 0:
        raise ValueError(f"TLE parse error {current_satellite.error}: {SGP4_ERRORS[current_satellite.error]}")

    return OrbitalParameters(
        semi_major_axis_km=current_satellite.a * earth_radius,
        inclination_deg=math.degrees(current_satellite.inclo),
        eccentricity=current_satellite.ecco,
        raan_deg=math.degrees(current_satellite.nodeo),
        bstar=current_satellite.bstar,
        mean_motion_rev_per_day=current_satellite.no_kozai * minutes_per_day / (2 * math.pi),
        epoch=sat_epoch_datetime(current_satellite),
    )
