"""Tunables for the deorbit model, kept in one place so experiments are diffable."""

from pathlib import Path

ARTIFACT_DIR = Path("ml/artifacts")

# Readiness gates checked by ml.audit before training is worth attempting.
MIN_DECAYED_OBJECTS = 2000
MIN_HISTORY_POINTS_PER_OBJECT = 10

# Drag-driven decay only happens in LEO. Highly eccentric orbits (e.g. the
# Cluster-II spacecraft) reenter through lunisolar perturbation instead, which
# this model can't learn from TLE drag terms.
MAX_ECCENTRICITY = 0.1
MAX_PERIGEE_ALT_KM = 1000.0

# Objects whose tracking stopped long before reentry have a label that is far
# from their last observed state; they add noise rather than signal.
MAX_GAP_LAST_TLE_TO_DECAY_DAYS = 14

# Starlink and similar constellations deorbit propulsively on command, which
# is a decision, not physics. Excluded from training labels by name prefix.
CONTROLLED_DEORBIT_NAME_PREFIXES = ("STARLINK", "ONEWEB")

# Every training label is under ~210 days (the backfill window), and the model
# only saw objects that did reenter, so it gives every LEO object a short
# lifetime. Below this perigee that is plausible; above it predictions are
# flagged as low confidence until the model can learn longer lifetimes.
FORECAST_MAX_PERIGEE_KM = 350.0

# A sample at time t sees only TLEs with epoch <= t, looking back this far.
LOOKBACK_DAYS = (7, 30, 90)

# Sample points per decayed object when building the training set.
SAMPLES_PER_OBJECT = 8

# Time-based split: train on older decays, test on newer ones, so the solar
# cycle the model is scored on is not one it has already seen.
TEST_DECAY_START = "2024-01-01"

RANDOM_SEED = 42
