"""Train/test splitting that avoids leaking an object across both sides.

Consecutive TLEs of the same object are nearly identical, so a random row
split would let the model memorise objects. Splits are by object and by
decay date (see TEST_DECAY_START) instead.
"""

import pandas as pd


def time_split(samples: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split by decay date: earlier decays train, later decays test."""
    raise NotImplementedError


def group_kfold(samples: pd.DataFrame, n_splits: int = 5):
    """Yield (train_idx, val_idx) folds grouped by norad_id for tuning."""
    raise NotImplementedError
