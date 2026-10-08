"""Fields that are in the raw TLE lines but not stored as tle_history columns.

The first derivative of mean motion (ndot, line 1 cols 34-43) is the most
direct drag signal a TLE carries, so it's parsed here from tle_line1 instead
of needing a schema change.
"""

import pandas as pd


def parse_mean_motion_derivatives(tle_line1: pd.Series) -> pd.DataFrame:
    """Return ndot (rev/day^2) and nddot (rev/day^3) columns from line 1."""

    # Extract the relevant substrings from tle_line1
    ndot_str = tle_line1.str[33:43].str.strip()
    nddot_str = tle_line1.str[44:52].str.strip()

    # Convert to float, handling the special format for nddot
    ndot = pd.to_numeric(ndot_str, errors='coerce')

    # For nddot, we need to handle the scientific notation format
    def parse_nddot(s):
        if pd.isna(s) or s == '':
            return float('nan')
        else:
            # The format is like "-12345-5" which means -0.12345e-5
            base = float(s[:-2]) * 10**(-5)
            exponent = int(s[-2:])
            return base * (10 ** exponent)

    nddot = nddot_str.apply(parse_nddot)

    return pd.DataFrame({'ndot': ndot, 'nddot': nddot})