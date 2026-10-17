import { Suspense, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { Earth, EarthPlaceholder } from "./components/Scene/Earth";
import { SatelliteField } from "./components/Scene/SatelliteField";
import { CameraFocus } from "./components/Scene/CameraFocus";
import { TopBar } from "./components/UI/topBar";
import { InfoPanel } from "./components/UI/InfoPanel";
import { useSatelliteData } from "./hooks/useSatelliteData";
import type { Satellite } from "./types/satellite";
import { isMobileDevice } from "./utils/device";

export function App() {
  const { satellites, loading, error } = useSatelliteData();
  const [selected, setSelected] = useState<Satellite | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [infoPanelCollapsed, setInfoPanelCollapsed] = useState(false);
  const [searchedSatellite, setSearchedSatellite] = useState<Satellite | null>(null);
  const [clearCount, setClearCount] = useState(0);
  const controlsRef = useRef<OrbitControlsImpl>(null);

  // Memoized so SatelliteField only rebuilds its buffers when the visible set
  // actually changes, not on every re-render (e.g. selecting a satellite)
  const visibleSatellites = useMemo(
    () =>
      searchedSatellite
        ? [searchedSatellite]
        : selectedCluster === null
          ? satellites
          : satellites.filter((s) => (s.cluster_id ?? 0) === selectedCluster),
    [satellites, searchedSatellite, selectedCluster]
  );

  const handleSelectCluster = (cluster: number | null) => {
    setSearchedSatellite(null);
    setSelectedCluster(cluster);
  };

  const handleSearchSelect = (satellite: Satellite) => {
    setSelected(satellite);
    setSearchedSatellite(satellite);
  };

  const handleClear = () => {
    setSelected(null);
    setSelectedCluster(null);
    setSearchedSatellite(null);
    setClearCount((c) => c + 1);
  };

  return (
    <div className={`app${infoPanelCollapsed ? " info-collapsed" : ""}`}>
      <TopBar
        totalSatellites={satellites.length}
        totalClusters={5}
        selectedCluster={selectedCluster}
        onSelectCluster={handleSelectCluster}
        onClear={handleClear}
      />
      <div className="scene-container">
        {loading && <div className="overlay-message">Loading satellites...</div>}
        {error && <div className="overlay-message">Error: {error}</div>}
        {/* Phones have 3x screens; capping at 1.5x instead of the default 2x draws ~44% fewer pixels */}
        <Canvas camera={{ position: [0, 0, 3] }} dpr={isMobileDevice ? [1, 1.5] : [1, 2]}>
          <ambientLight intensity={1.3} />
          <pointLight position={[5, 5, 5]} />
          {/* Without its own Suspense, the Earth textures would hold back the whole scene while loading */}
          <Suspense fallback={<EarthPlaceholder />}>
            <Earth />
          </Suspense>
          <SatelliteField satellites={visibleSatellites} onSelect={setSelected} />
          <CameraFocus satellite={searchedSatellite} controlsRef={controlsRef} />
          <OrbitControls ref={controlsRef} />
        </Canvas>
      </div>
      <InfoPanel
        key={clearCount}
        satellite={selected}
        satellites={satellites}
        collapsed={infoPanelCollapsed}
        onToggleCollapse={() => setInfoPanelCollapsed((c) => !c)}
        onSelectSatellite={handleSearchSelect}
        onClearSearch={() => setSearchedSatellite(null)}
      />
    </div>
  );
}

