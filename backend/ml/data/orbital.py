"""Per-snapshot geometry derived from the stored orbital elements."""

import pandas as pd

EARTH_RADIUS_KM = 6378.137


def add_orbital_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add perigee_alt_km, apogee_alt_km and period_min to each TLE row."""
    
    df["perigee_alt_km"] = df["semi_major_axis_km"] * (1 - df["eccentricity"]) - EARTH_RADIUS_KM
    df["apogee_alt_km"] = df["semi_major_axis_km"] * (1 + df["eccentricity"]) - EARTH_RADIUS_KM
    df["period_min"] = 1440 / df["mean_motion_rev_per_day"]

    return df
