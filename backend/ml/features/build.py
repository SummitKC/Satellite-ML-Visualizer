"""Assembles the model's feature matrix from cleaned history.

A training row is one (object, sample_time) pair: features describe what was
observable at sample_time and the label is days until reentry from then.
"""

import numpy as np
import pandas as pd
from ml.config import LOOKBACK_DAYS, SAMPLES_PER_OBJECT


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
    # merge_asof needs identical resolutions; decay_date is ns, parsed epochs are us.
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



def build_training_set(history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Return features + `days_to_decay` + `event_observed` + `norad_id` + `decay_date`."""

    return

    raise NotImplementedError


def build_inference_set(history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Features for every currently tracked object, sampled at its latest epoch."""
    raise NotImplementedError