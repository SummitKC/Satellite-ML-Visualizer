import * as satellite from "satellite.js";
import { useRef, useMemo } from 'react';
import { Mesh } from "three";
import type { Satellite } from "../../types/satellite";
import { useFrame } from "@react-three/fiber";

const CLUSTER_COLORS = ["#e63946", "#457b9d", "#2a9d8f", "#f4a261", "#9b5de5"];

interface SatelliteFieldProps {
  satellites: Satellite[];
  onSelect: (satellite: Satellite) => void;
}

//Get scale factor to convert from kilometers to the scale used in the Three.js scene
const earthRadius = 6371; 
const threeEarthRadius = 2;
const scaleFactor = threeEarthRadius / earthRadius;

const currentSatellite = ({ tle1, tle2 }: {tle1: string, tle2: string}) => {

  //Set a reference to the mesh so we can update its position in the useFrame hook
    const meshRef = useRef<Mesh>(null);

    const satrec = useMemo(() => {
      return satellite.twoline2satrec(tle1, tle2);
    }, [tle1, tle2]);

    useFrame(() => {
      if (!meshRef.current) return;
      
      //get current time, to get the current position of the satellite
      const nowDate = new Date();
      const positionAndVelocity = satellite.propagate(satrec, nowDate);
      const positionEci = positionAndVelocity.position;

      //get position vector and scale it to the Three.js scene
      if (positionEci && positionEci !== true) {
          const x = positionEci.x * scaleFactor;
          const y = positionEci.y * scaleFactor;
          const z = positionEci.z * scaleFactor;
        
        meshRef.current.position.set(x, y, z);
      }
  });

  return meshRef;

};

export function SatelliteField({ satellites, onSelect }: SatelliteFieldProps) {
  return (
    <group>
      {satellites.map((satellite) => (
        <mesh
          ref={currentSatellite({ tle1: satellite.tle_line1, tle2: satellite.tle_line2 })}
          key={satellite.norad_id}
          onClick={() => onSelect(satellite)}
        >
          <sphereGeometry args={[.01, 8, 8]} />
          <meshBasicMaterial
            color={CLUSTER_COLORS[(satellite.cluster_id ?? 0) % CLUSTER_COLORS.length]}
          />
        </mesh>
      ))}
    </group>
  );
}
