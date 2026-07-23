/**
 * Placeholder Earth mesh.
 *
 * TODO (Step 3): replace the basic material with a textured one using the
 * NASA Blue Marble map, e.g.:
 *   const colorMap = useLoader(TextureLoader, "/textures/earth_daymap.jpg");
 *   <meshStandardMaterial map={colorMap} />
 */
export function Earth() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial color="#2a4d69" wireframe />
    </mesh>
  );
}
