"""SQLite connection and schema for historical satellite data.

Kept separate from the in-memory live cache in app.services.satellite_cache:
that cache holds only the latest snapshot, while this stores TLE and SATCAT
history over time for ML feature engineering.
"""

import sqlite3
from pathlib import Path

from app.config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tle_history (
    norad_id INTEGER NOT NULL,
    epoch TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    tle_line1 TEXT NOT NULL,
    tle_line2 TEXT NOT NULL,
    semi_major_axis_km REAL NOT NULL,
    inclination_deg REAL NOT NULL,
    eccentricity REAL NOT NULL,
    raan_deg REAL NOT NULL,
    bstar REAL NOT NULL,
    mean_motion_rev_per_day REAL NOT NULL,
    PRIMARY KEY (norad_id, epoch)
);

CREATE TABLE IF NOT EXISTS satcat (
    norad_id INTEGER PRIMARY KEY,
    object_name TEXT NOT NULL,
    object_type TEXT,
    owner TEXT,
    launch_date TEXT,
    decay_date TEXT,
    rcs_m2 REAL,
    updated_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection to the history DB, creating the schema if needed."""
    settings = get_settings()
    db_path = Path(settings.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.executescript(_SCHEMA)
    return connection
