"""Scores the currently tracked catalog with a saved model.

Intended to be called from the API (e.g. a /satellites/deorbit-risk route)
after each TLE refresh, so it only loads the artifact, never trains.
"""

from pathlib import Path

import pandas as pd


def predict_current_catalog(model_path: Path) -> pd.DataFrame:
    """Return norad_id, predicted_days_to_decay, predicted_decay_date."""
    raise NotImplementedError
