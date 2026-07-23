import { useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { Earth } from "./components/Scene/Earth";
import { SatelliteField } from "./components/Scene/SatelliteField";
import { Sidebar } from "./components/UI/Sidebar";
import { InfoPanel } from "./components/UI/InfoPanel";
import { useSatelliteData } from "./hooks/useSatelliteData";
import type { Satellite } from "./types/satellite";

export function App() {
  const { satellites, loading, error } = useSatelliteData();
  const [selected, setSelected] = useState<Satellite | null>(null);

  return (
    <div className="app">
      <Sidebar totalSatellites={satellites.length} />
      <div className="scene-container">
        {loading && <div className="overlay-message">Loading satellites...</div>}
        {error && <div className="overlay-message">Error: {error}</div>}
        <Canvas camera={{ position: [0, 0, 3] }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[5, 5, 5]} />
          <Earth />
          <SatelliteField satellites={satellites} onSelect={setSelected} />
          <OrbitControls />
        </Canvas>
      </div>
      <InfoPanel satellite={selected} />
    </div>
  );
}
