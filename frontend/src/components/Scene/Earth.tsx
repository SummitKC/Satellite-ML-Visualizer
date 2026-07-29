import { useLoader, useThree } from "@react-three/fiber";
import { TextureLoader } from "three";
import vertexShader from "../shaders/vertex.glsl?raw";
import fragmentShader from "../shaders/fragment.glsl?raw";
import earthDayMap from "../../textures/8k_earth_daymap.jpg";

export function Earth() {
  const dayTexture = useLoader(TextureLoader, earthDayMap);
  const { gl } = useThree();
  dayTexture.anisotropy = gl.capabilities.getMaxAnisotropy();

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={{ dayTexture: { value: dayTexture } }}
      />
    </mesh>
  );
}
