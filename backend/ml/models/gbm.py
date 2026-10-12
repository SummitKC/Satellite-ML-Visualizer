"""Gradient-boosted regressor on log(days_to_decay).

Log target because lifetimes span days to years and an absolute-error loss
would be dominated by the long-lived objects. Uses scikit-learn's
HistGradientBoostingRegressor, which handles the NaNs from missing RCS
natively and is already a project dependency.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from ml.config import RANDOM_SEED
from ml.models.base import DeorbitModel


class GBMDeorbitModel(DeorbitModel):
    name = "gbm"

    def __init__(self) -> None:
        # Built-in early stopping holds out random rows, which puts samples of
        # the same object on both sides; a fixed round count avoids that.
        self.regressor = HistGradientBoostingRegressor(
            learning_rate=0.05,
            max_iter=500,
            min_samples_leaf=50,
            l2_regularization=1.0,
            early_stopping=False,
            random_state=RANDOM_SEED,
        )
        self.feature_names: list[str] = []

    def fit(self, features: pd.DataFrame, days_to_decay: pd.Series) -> None:
        self.feature_names = list(features.columns)
        # log1p rather than log so a sample taken on the day of reentry (0 days) stays finite.
        self.regressor.fit(features.astype(float), np.log1p(days_to_decay.clip(lower=0)))

    def predict_days(self, features: pd.DataFrame) -> pd.Series:
        # Same column order as training, whatever order the caller built them in.
        log_days = self.regressor.predict(features[self.feature_names].astype(float))

        return pd.Series(np.expm1(log_days), index=features.index).clip(lower=0)
