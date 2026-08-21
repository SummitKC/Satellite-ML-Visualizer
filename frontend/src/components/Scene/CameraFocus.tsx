import { useEffect, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { Vector3 } from "three";
import * as satellite from "satellite.js";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import type { Satellite } from "../../types/satellite";
import { getSatellitePosition } from "../../utils/satellitePosition";

interface CameraFocusProps {
  satellite: Satellite | null;
  controlsRef: React.RefObject<OrbitControlsImpl>;
}

const CAMERA_DISTANCE = 3;
const ARRIVAL_THRESHOLD = 0.01;

export function CameraFocus({ satellite: target, controlsRef }: CameraFocusProps) {
  const { camera } = useThree();
  const satrecRef = useRef<satellite.SatRec | null>(null);
  const animating = useRef(false);
  const desiredPosition = useRef(new Vector3());

  useEffect(() => {
    if (!target) {
      animating.current = false;
      return;
    }
    satrecRef.current = satellite.twoline2satrec(target.tle_line1, target.tle_line2);
    animating.current = true;
  }, [target]);

  useFrame(() => {
    if (!animating.current || !satrecRef.current) return;

    const position = getSatellitePosition(satrecRef.current);
    if (!position) return;

    const direction = new Vector3(position.x, position.y, position.z).normalize();
    desiredPosition.current.copy(direction).multiplyScalar(CAMERA_DISTANCE);

    camera.position.lerp(desiredPosition.current, 0.05);
    camera.lookAt(0, 0, 0);
    controlsRef.current?.update();

    if (camera.position.distanceTo(desiredPosition.current) < ARRIVAL_THRESHOLD) {
      animating.current = false;
    }
  });

  return null;
}
