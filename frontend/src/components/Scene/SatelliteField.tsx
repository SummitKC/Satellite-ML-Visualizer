import * as satellite from "satellite.js";
import { useRef, useMemo } from 'react';
import { Mesh } from "three";
import type { Satellite } from "../../types/satellite";
import { useFrame } from "@react-three/fiber";
import { CLUSTER_COLORS } from "../../constants/clusterColors";
import { getSatellitePosition } from "../../utils/satellitePosition";

interface SatelliteFieldProps {
  satellites: Satellite[];
  onSelect: (satellite: Satellite) => void;
}

interface SatelliteMeshProps {
  sat: Satellite;
  onSelect: (satellite: Satellite) => void;
}

function SatelliteMesh({ sat, onSelect }: SatelliteMeshProps) {
  //Set a reference to the mesh so we can update its position in the useFrame hook
  const meshRef = useRef<Mesh>(null);

  const satrec = useMemo(() => {
    return satellite.twoline2satrec(sat.tle_line1, sat.tle_line2);
  }, [sat.tle_line1, sat.tle_line2]);

  useFrame(() => {
    if (!meshRef.current) return;

    const position = getSatellitePosition(satrec);
    if (position) {
      meshRef.current.position.set(position.x, position.y, position.z);
    }
  });

  return (
    <mesh ref={meshRef} onClick={() => onSelect(sat)}>
      <sphereGeometry args={[.01, 8, 8]} />
      <meshBasicMaterial
        color={CLUSTER_COLORS[(sat.cluster_id ?? 0) % CLUSTER_COLORS.length]}
      />
    </mesh>
  );
}

export function SatelliteField({ satellites, onSelect }: SatelliteFieldProps) {
  return (
    <group>
      {satellites.map((sat) => (
        <SatelliteMesh key={sat.norad_id} sat={sat} onSelect={onSelect} />
      ))}
    </group>
  );
}
