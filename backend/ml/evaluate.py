"""Scores a model on the held-out split.

Errors are reported per true-horizon bucket (<7d, 7-30d, 30-90d, >90d)
because a 5-day miss is excellent at 180 days out and useless at 3 days out.
"""

import numpy as np
import pandas as pd

HORIZON_EDGES = [-np.inf, 7, 30, 90, np.inf]
HORIZON_LABELS = ["<7d", "7-30d", "30-90d", ">90d"]


def evaluate(y_true_days: pd.Series, y_pred_days: pd.Series) -> dict[str, float]:
    """MAE (days) and median relative error, overall and per horizon bucket."""

    abs_error = (y_pred_days - y_true_days).abs()
    # Floor the denominator at a day so samples taken at reentry don't divide by ~0.
    rel_error = abs_error / y_true_days.clip(lower=1)

    metrics = {
        "n": len(y_true_days),
        "mae_days": float(abs_error.mean()),
        "median_rel_error": float(rel_error.median()),
    }

    buckets = pd.cut(y_true_days, HORIZON_EDGES, labels=HORIZON_LABELS, right=False)
    for label in HORIZON_LABELS:
        in_bucket = buckets == label
        if not in_bucket.any():
            continue

        metrics[f"n_{label}"] = int(in_bucket.sum())
        metrics[f"mae_days_{label}"] = float(abs_error[in_bucket].mean())
        metrics[f"median_rel_error_{label}"] = float(rel_error[in_bucket].median())

    return metrics
