"""Common interface so train/evaluate/predict don't care which model they hold."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class DeorbitModel(ABC):
    name: str

    @abstractmethod
    def fit(self, features: pd.DataFrame, days_to_decay: pd.Series) -> None: ...

    @abstractmethod
    def predict_days(self, features: pd.DataFrame) -> pd.Series:
        """Predicted days until reentry, one per row."""

    def save(self, path: Path) -> None:
        raise NotImplementedError

    @classmethod
    def load(cls, path: Path) -> "DeorbitModel":
        raise NotImplementedError
