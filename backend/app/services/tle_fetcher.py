"""Fetches and parses TLE data from CelesTrak.

Step 1 of Initial-configs.md: implement the two functions below.
"""

import httpx

from app.config import get_settings


async def fetch_active_satellites_tle() -> list[tuple[str, str, str]]:
    """Fetch active satellite TLEs from CelesTrak.

    TODO:
      - GET settings.celestrak_tle_url with httpx.AsyncClient
      - The response body is plain text, 3 lines per satellite:
          name
          line1
          line2
      - Return a list of (name, line1, line2) tuples
    """
    settings = get_settings()
    raise NotImplementedError(f"Fetch TLE text from {settings.celestrak_tle_url}")


def parse_orbital_parameters(line1: str, line2: str) -> dict:
    """Derive orbital parameters from a TLE pair using sgp4.

    TODO:
      - Use sgp4.api.Satrec.twoline2rv(line1, line2)
      - Derive:
          semi_major_axis_km  (from satrec.a * earth radius, or mean motion)
          inclination_deg     (satrec.inclo, convert radians -> degrees)
          eccentricity        (satrec.ecco)
          raan_deg            (satrec.nodeo, convert radians -> degrees)
      - Return a dict matching app.schemas.OrbitalParameters fields
    """
    raise NotImplementedError
