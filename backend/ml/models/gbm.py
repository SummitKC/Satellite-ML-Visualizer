"""Gradient-boosted regressor on log(days_to_decay).

Log target because lifetimes span days to years and an absolute-error loss
would be dominated by the long-lived objects. Uses scikit-learn's
HistGradientBoostingRegressor, which handles the NaNs from missing RCS
natively and is already a project dependency.
"""

import pandas as pd

from ml.models.base import DeorbitModel


class GBMDeorbitModel(DeorbitModel):
    name = "gbm"

    def fit(self, features: pd.DataFrame, days_to_decay: pd.Series) -> None:
        raise NotImplementedError

    def predict_days(self, features: pd.DataFrame) -> pd.Series:
        raise NotImplementedError
