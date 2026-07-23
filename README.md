# Satellite ML Visualizer

Interactive 3D satellite orbit tracker with ML-based orbital clustering. See
[Initial-configs.md](Initial-configs.md) for the full project brief.

This repo currently contains **scaffolding only** — project structure, config,
data shapes, and stubbed-out functions with `TODO`s. The actual TLE parsing,
clustering, and orbit propagation logic are left for you to implement as a
learning exercise, following the "Recommended Implementation Steps" in
`Initial-configs.md`.

## Structure

```
backend/
  app/
    main.py            FastAPI app, CORS, router registration
    config.py           Settings (CelesTrak URL, CORS origins, cluster count)
    schemas.py           Pydantic models: Satellite, OrbitalParameters, SatelliteListResponse
    routers/
      satellites.py       GET /api/satellites (stubbed - returns empty list)
    services/
      tle_fetcher.py       fetch_active_satellites_tle(), parse_orbital_parameters() - TODO
      clustering.py         cluster_satellites() - TODO
  requirements.txt
  .env.example

frontend/
  src/
    App.tsx                     Layout: Sidebar + Canvas scene + InfoPanel
    components/Scene/
      Earth.tsx                   Placeholder wireframe sphere - TODO: Blue Marble texture
      SatelliteField.tsx           Renders satellite points - TODO: satellite.js propagation
    components/UI/
      Sidebar.tsx                  Satellite count + cluster legend
      InfoPanel.tsx                 Selected satellite details
    hooks/useSatelliteData.ts     Fetches GET /api/satellites
    types/satellite.ts             TS types mirroring backend schemas
  package.json
  vite.config.ts
  .env.example
```

## Getting started

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000` (`/health` to check it's up, `/docs` for
the OpenAPI UI).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App runs at `http://localhost:5173`.

## Next steps

Follow the steps in `Initial-configs.md`:

1. Implement `fetch_active_satellites_tle` and `parse_orbital_parameters` in
   `backend/app/services/tle_fetcher.py`.
2. Implement `cluster_satellites` in `backend/app/services/clustering.py`, then
   wire both into `backend/app/routers/satellites.py`.
3. Add a real Earth texture in `frontend/src/components/Scene/Earth.tsx`.
4. Use `satellite.js` in `frontend/src/components/Scene/SatelliteField.tsx` to
   propagate TLEs to real-time positions.
5. Verify cluster colors and the info panel/legend reflect live data end to end.
