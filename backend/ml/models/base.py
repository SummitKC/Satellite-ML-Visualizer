"""Common interface so train/evaluate/predict don't care which model they hold."""

from abc import ABC, abstractmethod
from pathlib import Path

import joblib
import pandas as pd


class DeorbitModel(ABC):
    name: str

    @abstractmethod
    def fit(self, features: pd.DataFrame, days_to_decay: pd.Series) -> None: ...

    @abstractmethod
    def predict_days(self, features: pd.DataFrame) -> pd.Series:
        """Predicted days until reentry, one per row."""

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: Path) -> "DeorbitModel":
        # joblib unpickles arbitrary code, so only load artifacts this project wrote.
        model = joblib.load(path)
        if not isinstance(model, cls):
            raise TypeError(f"{path} holds a {type(model).__name__}, not a {cls.__name__}")

        return model
