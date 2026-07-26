"""Clusters satellites into orbital regimes (LEO/MEO/GEO/etc)."""

import numpy as np
from sklearn import preprocessing, cluster

def cluster_satellites(features: np.ndarray, num_clusters: int = 5) -> np.ndarray:
    """Assign each satellite a cluster label based on its orbital parameters."""

    satellite_data_array = np.asarray(features)

    scaled_data = preprocessing.StandardScaler().fit_transform(satellite_data_array)
    kmeans = cluster.KMeans(n_clusters=num_clusters, random_state=0, n_init="auto")

    return kmeans.fit_predict(scaled_data)

