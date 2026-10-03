"""Filters that remove rows and objects the deorbit model shouldn't learn from.

Each filter is its own function so the audit and training can report how many
objects each one drops.
"""

import pandas as pd

def drop_post_decay_epochs(df: pd.DataFrame) -> pd.DataFrame:
    """Drop TLEs whose epoch falls after the object's recorded decay date.""" 

    df["decay_date"] = pd.to_datetime(df["decay_date"]).dt.tz_localize("UTC")
    df["epoch"] = pd.to_datetime(df["epoch"], format="IS08601", errors="coerce")

    decay_end = df["decay_date"] + pd.Timedelta(days=1)

    return df[df["decay_date"].isna() | (df["epoch"] <= decay_end)]


def drop_non_drag_orbits(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only LEO, near-circular objects """

    return df[(df["perigee_alt_km"] <= 1000) & (df["eccentricity"] <= 0.1)]


def drop_controlled_deorbits(df: pd.DataFrame) -> pd.DataFrame:
    """Drop decayed objects whose reentry was commanded rather than drag-driven."""
    raise NotImplementedError


def drop_stale_tracking(df: pd.DataFrame) -> pd.DataFrame:
    """Drop decayed objects whose last TLE is too long before their decay date."""
    raise NotImplementedError


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply every filter in order, logging how many objects each removes."""



    raise NotImplementedError
