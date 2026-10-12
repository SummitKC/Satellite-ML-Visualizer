"""In-memory cache of the deorbit model's reentry predictions.

Scoring reads months of TLE history and takes several seconds, so it runs in
a worker thread after each TLE refresh (see app.main's lifespan), and
requests to GET /api/satellites/{norad_id}/reentry only look up the result.
"""

import asyncio
import logging
from pathlib import Path

import pandas as pd

from app.config import get_settings
from app.schemas import ReentryPrediction
from app.services.satellite_cache import history_updated
from ml.predict import predict_current_catalog

logger = logging.getLogger(__name__)

_cache: dict[int, ReentryPrediction] | None = None


def get_cached_predictions() -> dict[int, ReentryPrediction] | None:
    return _cache


def _score_catalog(model_path: Path) -> dict[int, ReentryPrediction]:
    scores = predict_current_catalog(model_path)

    return {
        int(row.norad_id): ReentryPrediction(
            norad_id=int(row.norad_id),
            status=row.status,
            tle_epoch=row.tle_epoch.to_pydatetime(),
            predicted_decay_date=row.predicted_decay_date.floor("s").to_pydatetime(),
            error_days=None if pd.isna(row.error_days) else float(row.error_days),
        )
        for row in scores.itertuples(index=False)
    }


async def refresh_reentry_cache() -> None:
    """Score the tracked catalog and replace the cache."""
    global _cache
    settings = get_settings()

    _cache = await asyncio.to_thread(_score_catalog, Path(settings.reentry_model_path))

    forecasts = sum(prediction.status == "forecast" for prediction in _cache.values())
    logger.info("Refreshed reentry predictions: %d scored, %d forecasts", len(_cache), forecasts)


async def periodic_reentry_refresh_loop() -> None:
    """Score the stored history at startup, then again after every TLE refresh.

    The startup run means a throttled CelesTrak fetch doesn't leave the API
    without predictions; a failed run waits for the next TLE refresh.
    """
    while True:
        try:
            await refresh_reentry_cache()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to refresh reentry predictions; retrying after the next TLE refresh")

        await history_updated.wait()
        history_updated.clear()
