"""Fields that are in the raw TLE lines but not stored as tle_history columns.

The first derivative of mean motion (ndot, line 1 cols 34-43) is the most
direct drag signal a TLE carries, so it's parsed here from tle_line1 instead
of needing a schema change.
"""

import pandas as pd


def parse_mean_motion_derivatives(tle_line1: pd.Series) -> pd.DataFrame:
    """Return ndot (rev/day^2) and nddot (rev/day^3) columns from line 1."""
    raise NotImplementedError
