"""Scores the currently tracked catalog with a saved model.

Called from the API (app.services.reentry_cache) after each TLE refresh, so
it only loads the artifact, never trains.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ml.config import CONTROLLED_DEORBIT_NAME_PREFIXES, FORECAST_MAX_PERIGEE_KM, LOOKBACK_DAYS
from ml.data.cleaning import clean
from ml.data.loader import load_joined, load_satcat
from ml.data.orbital import add_orbital_features
from ml.evaluate import HORIZON_EDGES, HORIZON_LABELS
from ml.features.build import NON_FEATURE_COLUMNS, build_inference_set
from ml.models.base import DeorbitModel

# Inference only needs each object's latest TLE and the longest lookback
# behind it; the margin keeps full windows for objects a few weeks stale.
HISTORY_DAYS = max(LOOKBACK_DAYS) + 30


def _error_days(model: DeorbitModel, model_path: Path, predicted_days: pd.Series) -> pd.Series:
    """Held-out MAE of the horizon bucket each prediction falls in, from train.py's report."""

    report = json.loads((model_path.parent / f"{model.name}_metrics.json").read_text())
    metrics = report["metrics"][model.name]

    buckets = pd.cut(predicted_days, HORIZON_EDGES, labels=HORIZON_LABELS, right=False)
    return buckets.map({label: metrics.get(f"mae_days_{label}") for label in HORIZON_LABELS}).astype(float)


def _status(samples: pd.DataFrame, satcat: pd.DataFrame) -> np.ndarray:
    """Whether each prediction is presentable: "forecast", "controlled" or "too_high"."""

    names = samples["norad_id"].map(satcat.set_index("norad_id")["object_name"]).str.upper()
    controlled = names.str.startswith(CONTROLLED_DEORBIT_NAME_PREFIXES, na=False)
    too_high = samples["perigee_alt_km"] > FORECAST_MAX_PERIGEE_KM

    return np.select([controlled, too_high], ["controlled", "too_high"], default="forecast")


def predict_current_catalog(model_path: Path) -> pd.DataFrame:
    """Return norad_id, tle_epoch, status, predicted_days_to_decay,
    predicted_decay_date and error_days."""

    model = DeorbitModel.load(model_path)

    since = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=HISTORY_DAYS)).strftime("%Y-%m-%d")
    satcat = load_satcat()
    history = clean(add_orbital_features(load_joined(since)))
    samples = build_inference_set(history, satcat)
    predicted_days = model.predict_days(samples.drop(columns=NON_FEATURE_COLUMNS, errors="ignore"))

    # Days are counted from each object's latest TLE, not from now.
    prediction_results = pd.DataFrame({
        "norad_id": samples["norad_id"],
        "tle_epoch": samples["sample_time"],
        "status": _status(samples, satcat),
        "predicted_days_to_decay": predicted_days,
        "predicted_decay_date": samples["sample_time"] + pd.to_timedelta(predicted_days, unit="D"),
        "error_days": _error_days(model, model_path, predicted_days),
    })
    return prediction_results