import * as satellite from "satellite.js";
import { useEffect, useMemo, useRef } from "react";
import {
  BufferAttribute,
  BufferGeometry,
  Color,
  DynamicDrawUsage,
  Sphere,
  SRGBColorSpace,
  TextureLoader,
  Vector3,
} from "three";
import { useFrame, useLoader, useThree, type ThreeEvent } from "@react-three/fiber";
import type { Satellite } from "../../types/satellite";
import { CLUSTER_COLORS } from "../../constants/clusterColors";
import { getSatellitePosition, threeEarthRadius } from "../../utils/satellitePosition";
import vertexShader from "../shaders/satelliteVertex.glsl?raw";
import fragmentShader from "../shaders/satelliteFragment.glsl?raw";
import satelliteIcon from "../../textures/satellite-icon.svg";

interface SatelliteFieldProps {
  satellites: Satellite[];
  onSelect: (satellite: Satellite) => void;
}

// Width of each satellite icon in scene units
const SATELLITE_SIZE = 0.035;

// Icons narrower than this on screen (in CSS pixels) are drawn as plain dots,
// since the satellite shape can't be made out at that size
const MIN_ICON_SIZE = 10;

// Each satellite is shaded with a gradient around its cluster color: lighter and
// shifted one way in hue at the icon's top-left, darker and shifted the other way
// at its bottom-right. Hue is a fraction of the color wheel, lightness of 0-1
const GRADIENT_HUE_SHIFT = 0.04;
const GRADIENT_LIGHTNESS_SHIFT = 0.1;

const CLUSTER_GRADIENTS = CLUSTER_COLORS.map((hex) => {
  const { h, s, l } = new Color(hex).getHSL({ h: 0, s: 0, l: 0 }, SRGBColorSpace);
  return [
    new Color().setHSL(h + GRADIENT_HUE_SHIFT, s, Math.min(l + GRADIENT_LIGHTNESS_SHIFT, 1), SRGBColorSpace),
    new Color().setHSL(h - GRADIENT_HUE_SHIFT, s, Math.max(l - GRADIENT_LIGHTNESS_SHIFT, 0), SRGBColorSpace),
  ];
});

// Satellites move about a pixel per second at the default zoom, so each frame
// only propagates a slice of them and every satellite is refreshed once per sweep
const FRAMES_PER_SWEEP = 30;

// How close (in scene units) a click or tap has to land to a satellite to select it
const PICK_THRESHOLD = 0.03;

// Pointer travel in pixels past which a press counts as rotating the globe, not a click
const MAX_CLICK_DRAG = 5;

const earthSphere = new Sphere(new Vector3(), threeEarthRadius);

// Parsing a TLE is slow, so each satellite's satrec is cached and reused
// whenever the cluster filter or search changes the visible list
const satrecCache = new WeakMap<Satellite, satellite.SatRec>();

function getSatrec(sat: Satellite) {
  let satrec = satrecCache.get(sat);
  if (!satrec) {
    satrec = satellite.twoline2satrec(sat.tle_line1, sat.tle_line2);
    satrecCache.set(sat, satrec);
  }
  return satrec;
}

function propagateRange(satrecs: satellite.SatRec[], positions: Float32Array, start: number, end: number) {
  const now = new Date();
  for (let i = start; i < end; i++) {
    // If propagation fails the satellite keeps its last known position
    const position = getSatellitePosition(satrecs[i], now);
    if (position) {
      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;
    }
  }
}

export function SatelliteField({ satellites, onSelect }: SatelliteFieldProps) {
  const raycaster = useThree((state) => state.raycaster);
  const icon = useLoader(TextureLoader, satelliteIcon);
  const nextIndex = useRef(0);

  // Every satellite is a vertex of a single Points object, so the whole field
  // is one draw call instead of one mesh (and draw call) per satellite
  const { geometry, satrecs } = useMemo(() => {
    const satrecs = satellites.map(getSatrec);
    const positions = new Float32Array(satellites.length * 3);
    const gradientStarts = new Float32Array(satellites.length * 3);
    const gradientEnds = new Float32Array(satellites.length * 3);

    satellites.forEach((sat, i) => {
      const [start, end] = CLUSTER_GRADIENTS[(sat.cluster_id ?? 0) % CLUSTER_GRADIENTS.length];
      start.toArray(gradientStarts, i * 3);
      end.toArray(gradientEnds, i * 3);
    });
    propagateRange(satrecs, positions, 0, satrecs.length);

    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(positions, 3).setUsage(DynamicDrawUsage));
    geometry.setAttribute("gradientStart", new BufferAttribute(gradientStarts, 3));
    geometry.setAttribute("gradientEnd", new BufferAttribute(gradientEnds, 3));
    return { geometry, satrecs };
  }, [satellites]);

  useEffect(() => () => geometry.dispose(), [geometry]);

  useEffect(() => {
    raycaster.params.Points.threshold = PICK_THRESHOLD;
  }, [raycaster]);

  const uniforms = useMemo(
    () => ({
      size: { value: SATELLITE_SIZE },
      viewportHeight: { value: 1 },
      minIconSize: { value: MIN_ICON_SIZE },
      icon: { value: icon },
    }),
    [icon]
  );

  useFrame(({ gl }) => {
    uniforms.viewportHeight.value = gl.domElement.height;
    uniforms.minIconSize.value = MIN_ICON_SIZE * gl.getPixelRatio();

    const count = satrecs.length;
    if (count === 0) return;

    const start = nextIndex.current < count ? nextIndex.current : 0;
    const end = Math.min(start + Math.ceil(count / FRAMES_PER_SWEEP), count);
    const position = geometry.attributes.position as BufferAttribute;
    propagateRange(satrecs, position.array as Float32Array, start, end);

    // Only upload the slice that changed this frame
    position.clearUpdateRanges();
    position.addUpdateRange(start * 3, (end - start) * 3);
    position.needsUpdate = true;

    // Keep the bounds used for raycasting and frustum culling up to date as satellites move
    if (end === count) geometry.computeBoundingSphere();

    nextIndex.current = end % count;
  });

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    if (event.delta > MAX_CLICK_DRAG) return;

    // The click ray can pass near several satellites: skip any hidden behind
    // the Earth and select the one closest to where the user clicked
    const earthHit = event.ray.intersectSphere(earthSphere, new Vector3());
    const earthDistance = earthHit ? earthHit.distanceTo(event.ray.origin) : Infinity;

    let closestIndex = -1;
    let closestDistance = Infinity;
    for (const hit of event.intersections) {
      if (hit.object !== event.object || hit.index === undefined || hit.distance > earthDistance) continue;
      if (hit.distanceToRay! < closestDistance) {
        closestIndex = hit.index;
        closestDistance = hit.distanceToRay!;
      }
    }

    if (closestIndex >= 0) onSelect(satellites[closestIndex]);
  };

  return (
    <points geometry={geometry} onClick={handleClick}>
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
      />
    </points>
  );
}
