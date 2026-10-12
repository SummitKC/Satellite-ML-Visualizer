"""End-to-end training: load -> clean -> features -> split -> fit -> evaluate -> save.

    python -m ml.train --model gbm
"""

import argparse
import json
import logging
from datetime import datetime, timezone

from ml.config import ARTIFACT_DIR, TEST_DECAY_START
from ml.data.cleaning import clean
from ml.data.loader import load_joined, load_satcat
from ml.data.orbital import add_orbital_features
from ml.data.splits import time_split
from ml.evaluate import evaluate
from ml.features.build import NON_FEATURE_COLUMNS, build_training_set
from ml.models.baseline import DecayRateBaseline
from ml.models.gbm import GBMDeorbitModel

logger = logging.getLogger(__name__)

MODELS = {"baseline": DecayRateBaseline, "gbm": GBMDeorbitModel}


def _describe(samples) -> str:
    return f"{len(samples):,} samples from {samples['norad_id'].nunique():,} objects"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=list(MODELS), default="gbm")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    history = add_orbital_features(load_joined())
    logger.info("Loaded %d TLEs for %d objects", len(history), history["norad_id"].nunique())
    history = clean(history)
    logger.info("Cleaned to %d TLEs for %d objects", len(history), history["norad_id"].nunique())

    samples = build_training_set(history, load_satcat())
    train_set, test_set = time_split(samples)
    logger.info("Train: %s. Test (decayed from %s): %s", _describe(train_set), TEST_DECAY_START, _describe(test_set))

    x_train, y_train = train_set.drop(columns=NON_FEATURE_COLUMNS), train_set["days_to_decay"]
    x_test, y_test = test_set.drop(columns=NON_FEATURE_COLUMNS), test_set["days_to_decay"]

    # The baseline always runs so the chosen model's score has something to beat.
    models = [DecayRateBaseline()]
    if args.model != "baseline":
        models.append(MODELS[args.model]())

    metrics = {}
    for model in models:
        model.fit(x_train, y_train)
        metrics[model.name] = evaluate(y_test, model.predict_days(x_test))
        logger.info(
            "%s: MAE %.1f days, median relative error %.2f",
            model.name, metrics[model.name]["mae_days"], metrics[model.name]["median_rel_error"],
        )

    chosen = models[-1]
    model_path = ARTIFACT_DIR / f"{chosen.name}.joblib"
    chosen.save(model_path)

    report = {
        "model": chosen.name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "test_decay_start": TEST_DECAY_START,
        "train_samples": len(train_set),
        "test_samples": len(test_set),
        "metrics": metrics,
    }
    metrics_path = ARTIFACT_DIR / f"{chosen.name}_metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2))
    logger.info("Saved %s and %s", model_path, metrics_path)


if __name__ == "__main__":
    main()
