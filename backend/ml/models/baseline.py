"""Physics-only baseline the learned model has to beat.

Extrapolates the recent perigee-altitude slope down to ~120 km. If the GBM
can't beat this, its extra complexity isn't earning anything.
"""

import pandas as pd

from ml.models.base import DeorbitModel


class DecayRateBaseline(DeorbitModel):
    name = "decay_rate_baseline"

    def fit(self, features: pd.DataFrame, days_to_decay: pd.Series) -> None:
        pass

    def predict_days(self, features: pd.DataFrame) -> pd.Series:
        raise NotImplementedError
