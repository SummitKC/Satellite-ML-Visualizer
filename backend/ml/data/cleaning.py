"""Filters that remove rows and objects the deorbit model shouldn't learn from.

Each filter is its own function so the audit and training can report how many
objects each one drops.
"""

import pandas as pd


def drop_post_decay_epochs(df: pd.DataFrame) -> pd.DataFrame:
    """Drop TLEs whose epoch falls after the object's recorded decay date."""
    raise NotImplementedError


def drop_non_drag_orbits(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only LEO, near-circular objects (see MAX_ECCENTRICITY, MAX_PERIGEE_ALT_KM)."""
    raise NotImplementedError


def drop_controlled_deorbits(df: pd.DataFrame) -> pd.DataFrame:
    """Drop decayed objects whose reentry was commanded rather than drag-driven."""
    raise NotImplementedError


def drop_stale_tracking(df: pd.DataFrame) -> pd.DataFrame:
    """Drop decayed objects whose last TLE is too long before their decay date."""
    raise NotImplementedError


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply every filter in order, logging how many objects each removes."""
    raise NotImplementedError
