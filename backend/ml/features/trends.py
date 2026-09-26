"""How an object's orbit is changing over the lookback windows before a sample.

Decay rate matters more than current altitude: two objects at 400 km can be
weeks or years from reentry depending on how fast they are sinking.
"""

import pandas as pd


def add_trend_features(history: pd.DataFrame, sample_times: pd.DataFrame) -> pd.DataFrame:
    """For each (norad_id, sample_time), compute over each LOOKBACK_DAYS window:
    slope of perigee altitude and SMA, median B*, median ndot, TLE count.

    Only TLEs with epoch <= sample_time are visible, so no future leaks in.
    """
    raise NotImplementedError
