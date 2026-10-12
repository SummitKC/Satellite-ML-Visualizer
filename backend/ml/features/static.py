"""Per-object features that don't change over time (from SATCAT)."""

import pandas as pd

# SATCAT object_type codes. Fixed so training and inference get identical columns.
OBJECT_TYPES = ["PAY", "R/B", "DEB", "UNK"]


def add_static_features(samples: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Add object_type (one-hot), rcs_m2 (+ missing flag) and age_days at sample time."""

    catalog = satcat.set_index("norad_id")

    launch_date = pd.to_datetime(samples["norad_id"].map(catalog["launch_date"]), utc=True)
    samples["age_days"] = (samples["sample_time"] - launch_date).dt.total_seconds() / 86400

    samples["rcs_m2"] = samples["norad_id"].map(catalog["rcs_m2"])
    samples["rcs_missing"] = samples["rcs_m2"].isna()

    object_type = pd.Categorical(samples["norad_id"].map(catalog["object_type"]), categories=OBJECT_TYPES)
    type_columns = pd.get_dummies(object_type, prefix="type").set_index(samples.index)

    return pd.concat([samples, type_columns], axis=1)
