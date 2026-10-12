"""Assembles the model's feature matrix from cleaned history.

A training row is one (object, sample_time) pair: features describe what was
observable at sample_time and the label is days until reentry from then.
"""

import numpy as np
import pandas as pd
from ml.config import LOOKBACK_DAYS, SAMPLES_PER_OBJECT
from ml.data.labels import days_to_decay, event_observed
from ml.features.static import add_static_features
from ml.features.trends import add_trend_features

# starts ~210 days before reentry, so in training a low count means "about
# 200 days left", and the live catalog is fetched far less often anyway.
NON_FEATURE_COLUMNS = [
    "norad_id",
    "sample_time",
    "decay_date",
    "days_to_decay",
    "event_observed",
    *(f"tle_count_{days}d" for days in LOOKBACK_DAYS),
]

# The orbit as it stood at sample time, from the latest visible TLE.
CURRENT_STATE_COLUMNS = [
    "perigee_alt_km",
    "apogee_alt_km",
    "semi_major_axis_km",
    "eccentricity",
    "inclination_deg",
    "mean_motion_rev_per_day",
    "period_min",
    "bstar",
]


def choose_sample_times(history: pd.DataFrame) -> pd.DataFrame:
    """Pick SAMPLES_PER_OBJECT sample times per decayed object, spread across
    its history so the model sees both far-from and near-to reentry states."""

    decayed = history[history["decay_date"].notna()]

    # A sample needs at least the shortest lookback window of TLEs behind it,
    # and must not fall after the decay date or its label would be negative.
    first_epoch = decayed.groupby("norad_id")["epoch"].transform("min")
    earliest_allowed = first_epoch + pd.Timedelta(days=min(LOOKBACK_DAYS))
    eligible = decayed[(decayed["epoch"] >= earliest_allowed) & (decayed["epoch"] <= decayed["decay_date"])]

    objects = eligible.groupby("norad_id").agg(first_epoch=("epoch", "min"), decay_date=("decay_date", "first"))
    max_days = ((objects["decay_date"] - objects["first_epoch"]).dt.total_seconds() / 86400).clip(lower=1)

    # Targets are log-spaced from 1 day before decay out to the earliest eligible
    # epoch, so every horizon bucket in evaluate.py gets samples.
    steps = np.linspace(0, 1, SAMPLES_PER_OBJECT)
    days_before = np.power.outer(max_days.to_numpy(), steps).ravel()

    targets = objects.loc[objects.index.repeat(SAMPLES_PER_OBJECT)].reset_index()
    targets["target_time"] = targets["decay_date"] - pd.to_timedelta(days_before, unit="D")
    # merge_asof needs identical resolutions; the float day offsets make this
    # column ns while parsed epochs can be us.
    targets["target_time"] = targets["target_time"].astype(eligible["epoch"].dtype)

    # Snap each target to the object's nearest real TLE epoch, so the sample
    # time is a moment the object was actually observed.
    snapped = pd.merge_asof(
        targets.sort_values("target_time"),
        eligible[["norad_id", "epoch"]].sort_values("epoch"),
        left_on="target_time",
        right_on="epoch",
        by="norad_id",
        direction="nearest",
    )

    # Sparse histories can snap several targets to the same epoch.
    return (snapped.rename(columns={"epoch": "sample_time"})
                   .drop_duplicates(["norad_id", "sample_time"])
                   [["norad_id", "sample_time", "decay_date"]]
                   .sort_values(["norad_id", "sample_time"])
                   .reset_index(drop=True))


def _add_current_state(samples: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """Orbital elements of the latest TLE at or before each sample time."""

    latest = history[["norad_id", "epoch", *CURRENT_STATE_COLUMNS]].dropna(subset=["epoch"])

    merged = pd.merge_asof(
        samples.sort_values("sample_time"),
        latest.sort_values("epoch"),
        left_on="sample_time",
        right_on="epoch",
        by="norad_id",
        direction="backward",
    )

    return merged.drop(columns="epoch")


def _add_features(samples: pd.DataFrame, history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    samples = _add_current_state(samples, history)
    samples = add_trend_features(history, samples)
    samples = add_static_features(samples, satcat)

    return samples.sort_values(["norad_id", "sample_time"]).reset_index(drop=True)


def build_training_set(history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Return features + `days_to_decay` + `event_observed` + `norad_id` + `decay_date`."""

    samples = _add_features(choose_sample_times(history), history, satcat)
    samples["days_to_decay"] = days_to_decay(samples["sample_time"], samples["decay_date"])
    samples["event_observed"] = event_observed(samples["decay_date"])

    return samples


def build_inference_set(history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Features for every currently tracked object, sampled at its latest epoch."""

    tracked = history[history["decay_date"].isna()]
    samples = (tracked.groupby("norad_id", as_index=False)["epoch"].max()
                      .rename(columns={"epoch": "sample_time"})
                      .dropna(subset=["sample_time"]))

    return _add_features(samples, history, satcat)