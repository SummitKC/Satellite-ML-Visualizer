"""In-memory cache of the latest fetched/clustered satellite data.

Refreshed periodically by a background task (see app.main's lifespan) so
requests to GET /api/satellites never trigger a live CelesTrak fetch.
"""

import asyncio
import logging

import numpy as np

from app.config import get_settings
from app.schemas import Satellite, SatelliteListResponse
from app.services.clustering import cluster_satellites
from app.services.tle_fetcher import fetch_active_satellites_tle, parse_orbital_parameters
from app.services.tle_history import save_snapshots

logger = logging.getLogger(__name__)

_cache: SatelliteListResponse | None = None

# Set once each refresh's snapshots are saved, so reentry scoring
# (app.services.reentry_cache) re-runs on the fresh history.
history_updated = asyncio.Event()


def get_cached_satellites() -> SatelliteListResponse | None:
    return _cache


async def refresh_satellite_cache() -> None:
    """Fetch TLEs, parse orbital parameters, cluster, and replace the cache."""
    global _cache
    settings = get_settings()

    parsed = []
    for name, tle_line1, tle_line2 in await fetch_active_satellites_tle():
        norad_id = tle_line1[2:7]
        orbital_parameters = parse_orbital_parameters(tle_line1, tle_line2)
        parsed.append((norad_id, name, tle_line1, tle_line2, orbital_parameters))

    features = np.array([
        [op.semi_major_axis_km, op.inclination_deg, op.eccentricity, op.raan_deg]
        for *_, op in parsed
    ])
    labels = cluster_satellites(features, num_clusters=settings.cluster_count)

    satellites = [
        Satellite(
            norad_id=norad_id,
            name=name,
            tle_line1=tle_line1,
            tle_line2=tle_line2,
            orbital_parameters=orbital_parameters,
            cluster_id=int(label),
        )
        for (norad_id, name, tle_line1, tle_line2, orbital_parameters), label in zip(parsed, labels)
    ]

    _cache = SatelliteListResponse(satellites=satellites, total=len(satellites))
    logger.info("Refreshed satellite cache: %d satellites", len(satellites))

    save_snapshots(parsed)
    history_updated.set()


async def periodic_refresh_loop() -> None:
    """Refresh the cache on a timer, retrying quickly on failure."""
    settings = get_settings()
    while True:
        try:
            await refresh_satellite_cache()
            await asyncio.sleep(settings.tle_refresh_interval_seconds)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to refresh satellite cache; retrying in 60s")
            await asyncio.sleep(60)