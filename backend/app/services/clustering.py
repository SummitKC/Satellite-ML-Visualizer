"""Clusters satellites into orbital regimes (LEO/MEO/GEO/etc).

Step 2 of Initial-configs.md: implement the function below.
"""

import numpy as np


def cluster_satellites(features: np.ndarray, n_clusters: int = 5) -> np.ndarray:
    """Assign each satellite a cluster label based on its orbital parameters.

    Args:
        features: shape (n_satellites, 4) array of
            [semi_major_axis_km, inclination_deg, eccentricity, raan_deg]
        n_clusters: number of orbital regimes to fit

    TODO:
      - Standardize features (e.g. sklearn.preprocessing.StandardScaler) since
        semi-major axis (thousands of km) and eccentricity (0-1) are on very
        different scales
      - Fit sklearn.cluster.KMeans(n_clusters=n_clusters)
      - Return the fitted label array, shape (n_satellites,)
    """
    raise NotImplementedError
