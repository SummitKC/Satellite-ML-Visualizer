import { useLoader, useThree } from "@react-three/fiber";
import { TextureLoader, Vector3 } from "three";
import vertexShader from "../shaders/vertex.glsl?raw";
import fragmentShader from "../shaders/fragment.glsl?raw";
import earthDayMap8k from "../../textures/1_earth_8k.jpg";
import earthNightMap8k from "../../textures/5_night_8k.jpg";
import earthDayMap4k from "../../textures/1_earth_4k.jpg";
import earthNightMap4k from "../../textures/5_night_4k.jpg";
import { isMobileDevice } from "../../utils/device";

// The 8k pair is ~23 MB to download and ~350 MB of GPU memory once decoded,
// which is slow on phones and can crash mobile browsers, so they get 4k
const earthDayMap = isMobileDevice ? earthDayMap4k : earthDayMap8k;
const earthNightMap = isMobileDevice ? earthNightMap4k : earthNightMap8k;

export function Earth() {
  const dayTexture = useLoader(TextureLoader, earthDayMap);
  const nightTexture = useLoader(TextureLoader, earthNightMap);
  const lightDirection = new Vector3(1, -0.21, 0);
  const { gl } = useThree();
  dayTexture.anisotropy = gl.capabilities.getMaxAnisotropy();

  return (
    <mesh>
      <sphereGeometry args={[2, 64, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={{ dayTexture: { value: dayTexture }, nightTexture: { value: nightTexture }, lightDirection: { value: lightDirection } }}
      />
    </mesh>
  );
}

// Stands in while the textures load, so satellites behind the Earth stay hidden
export function EarthPlaceholder() {
  return (
    <mesh>
      <sphereGeometry args={[2, 64, 64]} />
      <meshBasicMaterial color="#0b1a2e" />
    </mesh>
  );
}
