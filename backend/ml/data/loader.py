"""Reads tle_history and satcat out of SQLite into DataFrames.

Reuses app.db.get_connection so the ML code and the API always agree on
which DB file and schema are in play.
"""

import pandas as pd
from app.db import get_connection


def load_tle_history() -> pd.DataFrame:
    """All TLE snapshots, with epoch parsed to UTC datetimes and sorted per object."""
    
    connection = get_connection()
    tle_history = pd.read_sql_query("SELECT * FROM tle_history ORDER BY norad_id, epoch", connection)  
    connection.close()
    
    return tle_history 


def load_satcat() -> pd.DataFrame:
    """SATCAT metadata with launch_date/decay_date parsed to datetimes."""

    connection = get_connection()
    satcat = pd.read_sql_query("SELECT * FROM satcat", connection)
    connection.close()

    return satcat


def load_joined() -> pd.DataFrame:
    """TLE history joined to SATCAT on norad_id (inner join)."""

    tle_history = load_tle_history()
    satcat = load_satcat()

    # Join on norad_id, keeping only rows that exist in both tables
    joined = pd.merge(tle_history, satcat, on="norad_id", how="inner")

    return joined