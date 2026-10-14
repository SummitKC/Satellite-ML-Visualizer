import { useState } from "react";
import type { Satellite } from "../../types/satellite";
import { ReentryForecast } from "./ReentryForecast";

interface InfoPanelProps {
  satellite: Satellite | null;
  satellites: Satellite[];
  collapsed: boolean;
  onToggleCollapse: () => void;
  onSelectSatellite: (satellite: Satellite) => void;
  onClearSearch: () => void;
}

const EARTH_RADIUS_KM = 6371;

export function InfoPanel({
  satellite,
  satellites,
  collapsed,
  onToggleCollapse,
  onSelectSatellite,
  onClearSearch,
}: InfoPanelProps) {
  const [query, setQuery] = useState("");

  if (collapsed) {
    return (
      <div className="info-panel info-panel-collapsed">
        <button
          type="button"
          className="info-panel-toggle"
          onClick={onToggleCollapse}
          aria-label="Expand info panel"
          title="Expand info panel"
        >
          &lsaquo;
        </button>
      </div>
    );
  }

  const handleSearch = () => {
    const term = query.trim().toLowerCase();
    if (!term) {
      onClearSearch();
      return;
    }

    const match = satellites.find(
      (s) => s.name.toLowerCase().includes(term) || String(s.norad_id).includes(term)
    );

    if (match) onSelectSatellite(match);
  };

  // Approximate altitude from semi-major axis; TODO (Step 5): use the
  // satellite's live propagated position (from SatelliteField) instead, since
  // altitude varies over the orbit for eccentric paths.
  const altitudeKm = satellite
    ? satellite.orbital_parameters.semi_major_axis_km - EARTH_RADIUS_KM
    : null;

  return (
    <div className="info-panel">
      <div className="info-panel-header">
        <button
          type="button"
          className="info-panel-toggle"
          onClick={onToggleCollapse}
          aria-label="Collapse info panel"
          title="Collapse info panel"
        >
          &rsaquo;
        </button>
        <input
          type="text"
          className="info-panel-search"
          placeholder="Search name or NORAD ID"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearch();
          }}
        />
      </div>

      {satellite ? (
        <>
          <h2>{satellite.name}</h2>
          <p>NORAD ID: {satellite.norad_id}</p>
          <p>Altitude: ~{altitudeKm!.toFixed(0)} km</p>
          <p>Cluster: {satellite.cluster_id ?? "unclassified"}</p>
          <ReentryForecast noradId={satellite.norad_id} />
        </>
      ) : (
        <p className="info-panel-empty">Select a satellite in the scene or search above.</p>
      )}
    </div>
  );
}
