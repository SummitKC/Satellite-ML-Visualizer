"""Persists TLE snapshots so orbital-parameter trends can be tracked over time.

The live cache in app.services.satellite_cache only ever holds the latest
fetch; decay/maneuver detection needs the history that would otherwise be
discarded on every refresh.
"""

import datetime as dt
import logging

from app.db import get_connection
from app.schemas import OrbitalParameters

logger = logging.getLogger(__name__)


def save_snapshots(parsed: list[tuple[str, str, str, str, OrbitalParameters]]) -> None:
    """Bulk-insert a catalog refresh's TLE snapshots.

    Duplicate (norad_id, epoch) pairs are ignored, since a satellite whose
    TLE hasn't been updated upstream will otherwise be re-inserted on every
    refresh cycle.
    """
    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()

    connection = get_connection()
    try:
        with connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO tle_history (
                    norad_id, epoch, fetched_at, tle_line1, tle_line2,
                    semi_major_axis_km, inclination_deg, eccentricity, raan_deg,
                    bstar, mean_motion_rev_per_day
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        int(norad_id),
                        op.epoch.isoformat(),
                        fetched_at,
                        tle_line1,
                        tle_line2,
                        op.semi_major_axis_km,
                        op.inclination_deg,
                        op.eccentricity,
                        op.raan_deg,
                        op.bstar,
                        op.mean_motion_rev_per_day,
                    )
                    for norad_id, _name, tle_line1, tle_line2, op in parsed
                ],
            )
    finally:
        connection.close()

    logger.info("Saved TLE history snapshot: %d satellites", len(parsed))
