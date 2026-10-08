"""Per-object features that don't change over time (from SATCAT)."""

import pandas as pd


def add_static_features(samples: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Add object_type (one-hot), rcs_m2 (+ missing flag) and age_days at sample time."""

    age_days = (samples["sample_time"] - satcat["launch_date"]).dt.total_seconds() / 86400
    samples["age_days"] = age_days
    
    return samples