# Satellite ML Visualizer

An interactive 3D tracker for the ~14,000 satellites in CelesTrak's active
catalog. Satellites are grouped into orbital regimes by ML clustering, and a
reentry (deorbit) model, trained on years of historical orbit data, forecasts
when low satellites will come down.

NOTE:  

## Features

**Globe**
- Day/night Earth with 8K textures and a custom shader that fades into city
  lights on the night side.
- Every active satellite, positioned in real time with SGP4 propagation
  (satellite.js).
- Satellites color-coded by orbital cluster, with a cluster filter in the
  top bar.
- Search by name or NORAD ID; the camera flies to the match.

**Info panel**
- Name, NORAD ID, approximate altitude and cluster of the selected satellite.
- **Reentry forecast:** a predicted date window, a countdown and the model's
  typical error. Estimates the model wasn't built for (actively controlled
  constellations, high orbits) are labeled low confidence, with a
  disclaimer explaining why.

**Data pipeline**
- TLEs refreshed from CelesTrak every 2 hours, with every snapshot kept in
  SQLite.
- The satellite catalog (SATCAT) refreshed daily: object type, launch and
  decay dates, radar cross-section.
- A Space-Track backfill job that pulls the last months of TLE history for
  every object that has reentered since 2015. This is the deorbit model's
  training data.

**Machine learning**
- KMeans clustering of orbital regimes (semi-major axis, inclination,
  eccentricity, RAAN).
- A gradient-boosted model that predicts days until reentry from an object's
  current orbit, its 7/30/90-day decay trends and its catalog entry. It's
  benchmarked against a physics-only baseline on a time-based train/test
  split.

## How it works

```
               TLEs every 2h, SATCAT daily
CelesTrak ───────────────────────────────▶ FastAPI backend ───── JSON ─────▶ React + Three.js
                                             │          ▲
                                 saves TLEs  ▼          │ loads model
Space-Track ── backfill job ──────▶ SQLite history ──▶ ml.train ──▶ ml/artifacts/gbm.joblib
```

- **On startup**, the backend fetches the active catalog, clusters it, caches
  it in memory and saves the TLEs to SQLite. It repeats this every 2 hours.
- **After each refresh**, it re-scores the catalog with the deorbit model in
  a background thread. It also scores once at startup from the stored
  history.
- **The frontend** fetches the satellite list once and propagates every
  position itself on each frame.

**Tech stack**
- Backend: Python 3.12, FastAPI, pandas, scikit-learn, SQLite
- Frontend: React 18, TypeScript, Vite, Three.js (via `@react-three/fiber` and
  `drei`), satellite.js

## Project structure

```
backend/
  app/
    main.py                  FastAPI app; starts the refresh loops
    config.py                Settings, read from the environment or backend/.env
    db.py                    SQLite schema (tle_history, satcat, backfill_progress)
    schemas.py               API response models
    routers/satellites.py    API routes
    services/
      tle_fetcher.py         CelesTrak TLE download and parsing
      satellite_cache.py     Refresh loop: fetch, cluster, cache, save history
      clustering.py          KMeans on orbital elements
      satcat_fetcher.py      Daily SATCAT refresh
      tle_history.py         Saves TLE snapshots to SQLite
      spacetrack.py          Rate-limited Space-Track client
      reentry_cache.py       Scores the catalog with the deorbit model
    jobs/
      backfill_history.py    Pulls historical TLEs of decayed objects from Space-Track
  ml/
    config.py                Data-cleaning and model settings
    audit.py                 Checks whether the history DB is ready to train on
    data/                    Loading, cleaning, orbital geometry, labels, splits
    features/                Feature engineering (current state, trends, catalog)
    models/                  Physics baseline and gradient-boosted model
    train.py                 Load → clean → features → split → fit → evaluate → save
    evaluate.py              Error broken down by time-to-reentry
    predict.py               Scores the live catalog (called by the API)
frontend/
  src/
    App.tsx                  Layout and selection state
    components/Scene/        Earth (day/night shader), SatelliteField, CameraFocus
    components/UI/           TopBar, InfoPanel, ReentryForecast
    hooks/                   useSatelliteData, useReentryPrediction
    utils/satellitePosition.ts   SGP4 propagation into scene coordinates
    textures/                Earth day/night maps
```

## Getting started

You'll need Python 3.12 and a current Node.js LTS. Training the deorbit model
also needs a free [Space-Track.org](https://www.space-track.org) account.

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000` (`/health` to check it's up, `/docs`
for the OpenAPI UI). On first start it downloads the active catalog and
SATCAT, and creates `data/satellite_history.sqlite3`.

> **CelesTrak throttles repeated downloads.** Its data updates about every
> 2 hours, and fetching the same file again sooner gets a `403`. Until the
> next successful refresh, `/api/satellites` returns `503`. With `--reload`,
> every saved backend file restarts the server and refetches, so this
> happens quickly during development.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

- **Textures** (`frontend/src/textures/`): the 8k day and night maps load on
  desktop and the 4k versions on mobile. These four are the only images
  committed; `.gitignore` excludes the rest.
- If the API isn't at `http://localhost:8000/api`, set `VITE_API_BASE_URL` in
  `frontend/.env`.

### 3. Training the deorbit model (optional)

The app runs without a trained model; the info panel then shows the forecast
as unavailable. To train one, from `backend/` with the virtualenv active:

1. Add your Space-Track credentials to `backend/.env`:

   ```
   SPACETRACK_IDENTITY=you@example.com
   SPACETRACK_PASSWORD=your-password
   ```

2. Start the API once, so SATCAT is loaded. The backfill reads decay dates
   from it.
3. Backfill historical TLEs. This takes several hours under Space-Track's rate
   limits. Progress is checkpointed, so re-running resumes where it stopped;
   add `--max-batches 5` for a quick test run.

   ```bash
   python -m app.jobs.backfill_history --since-year 2015
   ```

4. Check that there's enough data to train on:

   ```bash
   python -m ml.audit
   ```

5. Train. This writes `ml/artifacts/gbm.joblib` and `gbm_metrics.json`.

   ```bash
   python -m ml.train --model gbm
   ```

6. Restart the API. It scores the catalog at startup and after every TLE
   refresh.

## API

| Method | Path | Returns |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` |
| `GET` | `/api/satellites` | Active satellites with TLEs, orbital elements and cluster IDs. `503` until the first fetch completes. |
| `GET` | `/api/satellites/{norad_id}/reentry` | The deorbit model's forecast for one satellite. `503` until the first scoring run completes. |

Example reentry response:

```json
{
  "norad_id": 61760,
  "status": "forecast",
  "tle_epoch": "2026-10-09T06:57:24.485472Z",
  "predicted_decay_date": "2026-10-12T02:31:47Z",
  "error_days": 1.33
}
```

`status` is one of:

| Status | Meaning |
|---|---|
| `forecast` | Low orbit (perigee below 350 km), not actively controlled. Within what the model has learned. |
| `controlled` | Starlink or OneWeb. The operator commands the deorbit, so the drag-based estimate may not apply. |
| `too_high` | Perigee above 350 km. The estimate is low confidence; the real lifetime is likely much longer. |
| `not_modelled` | Not scored, e.g. perigee above 1,000 km, an eccentric orbit, or no history. No estimate. |

## Configuration

Backend settings are read from environment variables or `backend/.env`.

| Variable | Default | Purpose |
|---|---|---|
| `SPACETRACK_IDENTITY`, `SPACETRACK_PASSWORD` | (none) | Space-Track login, needed for the backfill job only |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins allowed to call the API |
| `CLUSTER_COUNT` | `5` | Number of KMeans clusters (the frontend currently assumes 5) |
| `TLE_REFRESH_INTERVAL_SECONDS` | `7200` | How often to refetch TLEs from CelesTrak |
| `SATCAT_REFRESH_INTERVAL_SECONDS` | `86400` | How often to refetch SATCAT |
| `DB_PATH` | `data/satellite_history.sqlite3` | SQLite history database |
| `REENTRY_MODEL_PATH` | `ml/artifacts/gbm.joblib` | Trained deorbit model the API loads |
| `SPACETRACK_REQUESTS_PER_MINUTE`, `SPACETRACK_REQUESTS_PER_HOUR` | `20`, `250` | Kept under Space-Track's published caps (30/min, 300/hour) |

Frontend: `VITE_API_BASE_URL` (default `http://localhost:8000/api`).

## The deorbit model

Trained on objects that reentered before 2024 and tested on objects that
reentered in 2024 or later. That means the test covers a later period than
anything the model trained on, including a different phase of the solar
cycle.

| Time to reentry | Gradient-boosted model, mean error | Physics baseline, mean error |
|---|---|---|
| Under 7 days | 1.3 days | 20.6 days |
| 7–30 days | 3.1 days | 70.1 days |
| 30–90 days | 11.8 days | 136.1 days |
| Over 90 days | 31.0 days | 45.4 days |
| **Overall** | **8.8 days** | **61.5 days** |

**Known limitation:** every training object reentered within ~210 days of its
first stored TLE, and the model never sees satellites that stay up. So it
gives every low-orbit object a short lifetime. That's why the API only treats
low-perigee, uncontrolled objects as real forecasts and labels the rest. The
roadmap below covers the fix.

## Roadmap

- **Deorbit model:** a longer backfill window, a survival model that also
  learns from satellites still in orbit, and solar-activity (F10.7) features.
- **Maneuver detection with TensorFlow:** flag station-keeping and orbit
  changes from TLE history. This would also replace the name-based
  "controlled" check.
- **Reentry watchlist:** a "reentering soon" filter in the top bar, and an
  option to color satellites by reentry risk.
- **Collision / conjunction prediction.**
- **Other ideas:** show what's currently flying over a location, and upcoming
  launches.

## Data sources

- [CelesTrak](https://celestrak.org): current TLEs (active group) and SATCAT.
- [Space-Track.org](https://www.space-track.org): historical TLEs
  (`gp_history`). Requires a free account; follow its usage policy and rate
  limits.
- Earth textures: Natural Earth III by Tom Patterson,
  [shadedrelief.com](https://www.shadedrelief.com/natural3/) (public domain).
  The 4k versions are downscaled from the 8k originals.
