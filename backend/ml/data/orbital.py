"""Per-snapshot geometry derived from the stored orbital elements."""

import pandas as pd

EARTH_RADIUS_KM = 6378.137


def add_orbital_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add perigee_alt_km, apogee_alt_km and period_min to each TLE row."""
    
    df["perigee_alt_km"] = df["perigee_km"] - EARTH_RADIUS_KM
    df["apogee_alt_km"] = df["apogee_km"] - EARTH_RADIUS_KM
    df["period_min"] = df["period_sec"] / 60

    return df
