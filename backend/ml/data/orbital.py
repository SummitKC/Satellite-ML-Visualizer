"""Per-snapshot geometry derived from the stored orbital elements."""

import pandas as pd

EARTH_RADIUS_KM = 6378.137


def add_orbital_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add perigee_alt_km, apogee_alt_km and period_min to each TLE row."""
    raise NotImplementedError
