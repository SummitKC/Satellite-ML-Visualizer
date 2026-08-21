import * as satellite from "satellite.js";

const earthRadius = 6371;
const threeEarthRadius = 2;

//Scale factor to convert from kilometers to the scale used in the Three.js scene
export const scaleFactor = threeEarthRadius / earthRadius;

export function getSatellitePosition(satrec: satellite.SatRec, date: Date = new Date()) {
  const positionAndVelocity = satellite.propagate(satrec, date);
  const positionEci = positionAndVelocity.position;
  if (!positionEci || positionEci === true) return null;

  return {
    x: positionEci.x * scaleFactor,
    y: positionEci.y * scaleFactor,
    z: positionEci.z * scaleFactor,
  };
}
