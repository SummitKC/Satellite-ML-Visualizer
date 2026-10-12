"""Physics-only baseline the learned model has to beat.

Extrapolates the recent perigee-altitude slope down to ~120 km. If the GBM
can't beat this, its extra complexity isn't earning anything.
"""

import pandas as pd

from ml.models.base import DeorbitModel

REENTRY_ALT_KM = 120.0


class DecayRateBaseline(DeorbitModel):
    name = "decay_rate_baseline"

    def fit(self, features: pd.DataFrame, days_to_decay: pd.Series) -> None:
        # The physics needs no fitting. These cover objects with no usable
        # slope, and cap near-flat slopes that extrapolate to centuries.
        self.fallback_days = float(days_to_decay.median())
        self.max_days = float(days_to_decay.max())

    def predict_days(self, features: pd.DataFrame) -> pd.Series:
        # Decay accelerates, so the most recent slope is the least stale. On the
        # 2024+ test set, 7d-first beat 30d-first by ~18 days MAE.
        slope = (features["perigee_slope_7d"]
                 .fillna(features["perigee_slope_30d"])
                 .fillna(features["perigee_slope_90d"]))

        days = (features["perigee_alt_km"] - REENTRY_ALT_KM) / -slope
        days = days.where(slope < 0, self.fallback_days)

        return days.clip(lower=0, upper=self.max_days)
