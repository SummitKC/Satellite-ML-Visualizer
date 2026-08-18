import type { Satellite } from "../../types/satellite";

interface InfoPanelProps {
  satellite: Satellite | null;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

const EARTH_RADIUS_KM = 6371;

export function InfoPanel({ satellite, collapsed, onToggleCollapse }: InfoPanelProps) {
  if (!satellite) return null;

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

  // Approximate altitude from semi-major axis; TODO (Step 5): use the
  // satellite's live propagated position (from SatelliteField) instead, since
  // altitude varies over the orbit for eccentric paths.
  const altitudeKm = satellite.orbital_parameters.semi_major_axis_km - EARTH_RADIUS_KM;

  return (
    <div className="info-panel">
      <button
        type="button"
        className="info-panel-toggle"
        onClick={onToggleCollapse}
        aria-label="Collapse info panel"
        title="Collapse info panel"
      >
        &rsaquo;
      </button>
      <h2>{satellite.name}</h2>
      <p>NORAD ID: {satellite.norad_id}</p>
      <p>Altitude: ~{altitudeKm.toFixed(0)} km</p>
      <p>Cluster: {satellite.cluster_id ?? "unclassified"}</p>
    </div>
  );
}
