"""Assembles the model's feature matrix from cleaned history.

A training row is one (object, sample_time) pair: features describe what was
observable at sample_time and the label is days until reentry from then.
"""

import pandas as pd


def choose_sample_times(history: pd.DataFrame) -> pd.DataFrame:
    """Pick SAMPLES_PER_OBJECT sample times per decayed object, spread across
    its history so the model sees both far-from and near-to reentry states."""
    raise NotImplementedError


def build_training_set(history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Return features + `days_to_decay` + `event_observed` + `norad_id` + `decay_date`."""
    raise NotImplementedError


def build_inference_set(history: pd.DataFrame, satcat: pd.DataFrame) -> pd.DataFrame:
    """Features for every currently tracked object, sampled at its latest epoch."""
    raise NotImplementedError