"""Scores a model on the held-out split.

Errors are reported per true-horizon bucket (<7d, 7-30d, 30-90d, >90d)
because a 5-day miss is excellent at 180 days out and useless at 3 days out.
"""

import pandas as pd


def evaluate(y_true_days: pd.Series, y_pred_days: pd.Series) -> dict[str, float]:
    """MAE (days) and median relative error, overall and per horizon bucket."""
    raise NotImplementedError
