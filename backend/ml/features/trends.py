"""How an object's orbit is changing over the lookback windows before a sample.

Decay rate matters more than current altitude: two objects at 400 km can be
weeks or years from reentry depending on how fast they are sinking.
"""

import pandas as pd

from ml.config import LOOKBACK_DAYS
from ml.features.tle_fields import parse_mean_motion_derivatives

SUM_COLUMNS = ["n", "t", "t_t", "perigee", "t_perigee", "sma", "t_sma"]
MEDIAN_COLUMNS = ["bstar", "ndot"]


def _slope(sums: pd.DataFrame, y: str) -> pd.Series:
    """Least-squares slope of y against t (km/day) from the rolling sums."""

    n = sums["n"]
    numerator = n * sums[f"t_{y}"] - sums["t"] * sums[y]
    denominator = n * sums["t_t"] - sums["t"] ** 2

    # Fewer than 3 TLEs, or TLEs bunched within hours of each other, give a
    # slope that is mostly fit noise. denominator / n^2 is the variance of t.
    enough_spread = (n >= 3) & (denominator / n**2 >= 0.25)

    return (numerator / denominator).where(enough_spread)


def add_trend_features(history: pd.DataFrame, sample_times: pd.DataFrame) -> pd.DataFrame:
    """For each (norad_id, sample_time), compute over each LOOKBACK_DAYS window:
    slope of perigee altitude and SMA, median B*, median ndot, TLE count.

    Only TLEs with epoch <= sample_time are visible, so no future leaks in.
    """

    # Only the sampled objects' TLEs from the longest lookback before their first sample.
    window_start = sample_times.groupby("norad_id")["sample_time"].min() - pd.Timedelta(days=max(LOOKBACK_DAYS))
    tles = history[["norad_id", "epoch", "perigee_alt_km", "semi_major_axis_km", "bstar", "tle_line1"]].merge(
        window_start.rename("window_start").reset_index(), on="norad_id"
    )
    tles = (tles[tles["epoch"] >= tles["window_start"]]
            .drop_duplicates(["norad_id", "epoch"])
            .sort_values(["norad_id", "epoch"]))

    # Slopes come from rolling sums of t, y, t*y and t^2. t is measured from
    # window_start so those sums stay small enough to keep their precision.
    t = (tles["epoch"] - tles["window_start"]).dt.total_seconds() / 86400
    columns = pd.DataFrame({
        "norad_id": tles["norad_id"],
        "epoch": tles["epoch"],
        "n": 1.0,
        "t": t,
        "t_t": t * t,
        "perigee": tles["perigee_alt_km"],
        "t_perigee": t * tles["perigee_alt_km"],
        "sma": tles["semi_major_axis_km"],
        "t_sma": t * tles["semi_major_axis_km"],
        "bstar": tles["bstar"],
        "ndot": parse_mean_motion_derivatives(tles["tle_line1"])["ndot"],
    })

    # Rolling results are indexed by (norad_id, epoch), unique after the dedupe above.
    windows = []
    for days in LOOKBACK_DAYS:
        # Time-based windows are (epoch - days, epoch], so each row sees only its past.
        rolling = columns.groupby("norad_id").rolling(f"{days}D", on="epoch")
        sums = rolling[SUM_COLUMNS].sum()
        medians = rolling[MEDIAN_COLUMNS].median()

        windows.append(pd.DataFrame({
            f"perigee_slope_{days}d": _slope(sums, "perigee"),
            f"sma_slope_{days}d": _slope(sums, "sma"),
            f"bstar_median_{days}d": medians["bstar"],
            f"ndot_median_{days}d": medians["ndot"],
            f"tle_count_{days}d": sums["n"],
        }))
    stats = pd.concat(windows, axis=1).reset_index()

    # Each sample takes the window stats of its latest TLE at or before sample_time.
    merged = pd.merge_asof(
        sample_times.sort_values("sample_time"),
        stats.sort_values("epoch"),
        left_on="sample_time",
        right_on="epoch",
        by="norad_id",
        direction="backward",
    )

    return merged.drop(columns="epoch")
