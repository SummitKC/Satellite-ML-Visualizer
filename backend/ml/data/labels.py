"""Turns SATCAT decay dates into training targets.

Objects that haven't decayed are right-censored: we only know they survived
at least until their last TLE. The first model trains on decayed objects
only; `event_observed` is carried along so a survival model can use the
censored ones later without rebuilding the dataset.
"""

import pandas as pd


def days_to_decay(sample_time: pd.Series, decay_date: pd.Series) -> pd.Series:
    """Target: days between the sample time and reentry (NaN if not decayed)."""
    raise NotImplementedError


def event_observed(decay_date: pd.Series) -> pd.Series:
    """True where the object has decayed, False where it is censored."""
    raise NotImplementedError
