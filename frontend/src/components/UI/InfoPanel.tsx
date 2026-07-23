import type { Satellite } from "../../types/satellite";

interface InfoPanelProps {
  satellite: Satellite | null;
}

const EARTH_RADIUS_KM = 6371;

export function InfoPanel({ satellite }: InfoPanelProps) {
  if (!satellite) return null;

  // Approximate altitude from semi-major axis; TODO (Step 5): use the
  // satellite's live propagated position (from SatelliteField) instead, since
  // altitude varies over the orbit for eccentric paths.
  const altitudeKm = satellite.orbital_parameters.semi_major_axis_km - EARTH_RADIUS_KM;

  return (
    <div className="info-panel">
      <h2>{satellite.name}</h2>
      <p>NORAD ID: {satellite.norad_id}</p>
      <p>Altitude: ~{altitudeKm.toFixed(0)} km</p>
      <p>Cluster: {satellite.cluster_id ?? "unclassified"}</p>
    </div>
  );
}
