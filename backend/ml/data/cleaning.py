"""Filters that remove rows and objects the deorbit model shouldn't learn from.

Each filter is its own function so the audit and training can report how many
objects each one drops.
"""

import pandas as pd
from ml.config import MAX_ECCENTRICITY, MAX_GAP_LAST_TLE_TO_DECAY_DAYS, MAX_PERIGEE_ALT_KM

def drop_post_decay_epochs(df: pd.DataFrame) -> pd.DataFrame:
    """Drop TLEs whose epoch falls after the object's recorded decay date.""" 

    df["decay_date"] = pd.to_datetime(df["decay_date"]).dt.tz_localize("UTC")
    df["epoch"] = pd.to_datetime(df["epoch"], format="ISO8601", errors="coerce")

    decay_end = df["decay_date"] + pd.Timedelta(days=1)

    return df[df["decay_date"].isna() | (df["epoch"] <= decay_end)]


def drop_non_drag_orbits(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only LEO, near-circular objects """

    return df[(df["perigee_alt_km"] <= MAX_PERIGEE_ALT_KM) & (df["eccentricity"] <= MAX_ECCENTRICITY)]


def drop_controlled_deorbits(df: pd.DataFrame) -> pd.DataFrame:
    """Drop decayed objects whose reentry was commanded rather than drag-driven."""

    return df[df["decay_date"].isna() | (df["decay_type"] != "controlled")]



def drop_stale_tracking(df: pd.DataFrame) -> pd.DataFrame:
    """Drop decayed objects whose last TLE is too long before their decay date."""

    last_epoch = df.groupby("norad_id")["epoch"].transform("max")
    gap = df["decay_date"] - last_epoch

    return df[df["decay_date"].isna() | (gap <= pd.Timedelta(days=MAX_GAP_LAST_TLE_TO_DECAY_DAYS))]


def clean(df: pd.DataFrame) -> pd.DataFrame:

    return (df.pipe(drop_post_decay_epochs)
              .pipe(drop_non_drag_orbits)
              .pipe(drop_controlled_deorbits)
              .pipe(drop_stale_tracking))


