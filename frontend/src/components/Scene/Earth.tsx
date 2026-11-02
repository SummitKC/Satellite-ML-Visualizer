import { useEffect, useMemo } from "react";
import { useLoader, useThree } from "@react-three/fiber";
import { type Texture, TextureLoader, Vector3 } from "three";
import vertexShader from "../shaders/vertex.glsl?raw";
import fragmentShader from "../shaders/fragment.glsl?raw";
import earthDayMap8k from "../../textures/1_earth_8k.jpg";
import earthNightMap8k from "../../textures/5_night_8k.jpg";
import earthDayMap4k from "../../textures/1_earth_4k.jpg";
import earthNightMap4k from "../../textures/5_night_4k.jpg";
import { isMobileDevice } from "../../utils/device";

// Every device starts with the 4k pair (~2.3 MB), so the Earth appears quickly.
// Desktops then load the 8k pair (~8 MB) in the background and swap it in.
// Phones stay on 4k: the 8k pair takes ~350 MB of GPU memory once decoded,
// which can crash mobile browsers.
export function Earth() {
  const [dayTexture, nightTexture] = useLoader(TextureLoader, [earthDayMap4k, earthNightMap4k]);
  const { gl } = useThree();

  const uniforms = useMemo(() => {
    dayTexture.anisotropy = gl.capabilities.getMaxAnisotropy();
    return {
      dayTexture: { value: dayTexture as Texture },
      nightTexture: { value: nightTexture as Texture },
      lightDirection: { value: new Vector3(1, -0.21, 0) },
    };
  }, [dayTexture, nightTexture, gl]);

  useEffect(() => {
    if (isMobileDevice) return;

    let cancelled = false;
    let hdTextures: Texture[] = [];
    const loader = new TextureLoader();

    Promise.all([loader.loadAsync(earthDayMap8k), loader.loadAsync(earthNightMap8k)])
      .then(([hdDay, hdNight]) => {
        hdTextures = [hdDay, hdNight];
        if (cancelled) {
          hdTextures.forEach((texture) => texture.dispose());
          return;
        }
        hdDay.anisotropy = gl.capabilities.getMaxAnisotropy();
        uniforms.dayTexture.value = hdDay;
        uniforms.nightTexture.value = hdNight;

        // The 4k pair is no longer drawn, so free its GPU memory. three.js
        // re-uploads it if it's ever used again (e.g. the Earth remounts)
        dayTexture.dispose();
        nightTexture.dispose();
      })
      .catch(() => {
        // Keep showing the 4k textures if the 8k ones fail to load
      });

    return () => {
      cancelled = true;
      hdTextures.forEach((texture) => texture.dispose());
      uniforms.dayTexture.value = dayTexture;
      uniforms.nightTexture.value = nightTexture;
    };
  }, [uniforms, dayTexture, nightTexture, gl]);

  return (
    <mesh>
      <sphereGeometry args={[2, 64, 64]} />
      <shaderMaterial vertexShader={vertexShader} fragmentShader={fragmentShader} uniforms={uniforms} />
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
