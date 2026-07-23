import type { Satellite } from "../../types/satellite";

const CLUSTER_COLORS = ["#e63946", "#457b9d", "#2a9d8f", "#f4a261", "#9b5de5"];

interface SatelliteFieldProps {
  satellites: Satellite[];
  onSelect: (satellite: Satellite) => void;
}

/**
 * Renders each satellite as a point, color-coded by cluster_id.
 *
 * TODO (Step 4): use satellite.js (twoline2satrec + propagate) to convert each
 * satellite's TLE to ECI coordinates for the current time, then eciToGeodetic
 * to get lat/lon/alt, then project that onto the unit-radius Earth sphere used
 * in Earth.tsx to get [x, y, z]. Update on a render loop (useFrame) for
 * real-time movement.
 */
export function SatelliteField({ satellites, onSelect }: SatelliteFieldProps) {
  return (
    <group>
      {satellites.map((satellite) => (
        <mesh
          key={satellite.norad_id}
          position={[0, 0, 0]}
          onClick={() => onSelect(satellite)}
        >
          <sphereGeometry args={[0.01, 8, 8]} />
          <meshBasicMaterial
            color={CLUSTER_COLORS[(satellite.cluster_id ?? 0) % CLUSTER_COLORS.length]}
          />
        </mesh>
      ))}
    </group>
  );
}
