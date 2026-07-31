import { useLoader, useThree } from "@react-three/fiber";
import { TextureLoader, Vector3 } from "three";
import vertexShader from "../shaders/vertex.glsl?raw";
import fragmentShader from "../shaders/fragment.glsl?raw";
import earthDayMap from "../../textures/1_earth_8k.jpg";
import earthNightMap from "../..//textures/5_night_8k.jpg";

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
