import  "../../styles.css";
import { CLUSTER_COLORS } from "../../constants/clusterColors";

interface TopBarProps {
    totalSatellites: number;
    totalClusters: number;
    selectedCluster: number | null;
    onSelectCluster: (cluster: number | null) => void;
}

export function TopBar({ totalSatellites, totalClusters, selectedCluster, onSelectCluster }: TopBarProps) {
  return (
    <div className="top-bar">
      <header>
        <h1>SV</h1>
          <div className="bar-stats">
            <p>Total Satellites: {totalSatellites}</p>
            <p>Total Clusters: {totalClusters}</p>
          </div>
        <ul className="satellite-clusters">
          {Array.from({ length: totalClusters }, (_, i) => (
            <li
              key={i}
              className={`cluster${selectedCluster === i ? " active" : ""}`}
              onClick={() => onSelectCluster(selectedCluster === i ? null : i)}
              title={`Cluster ${i + 1}`}
              aria-label={`Cluster ${i + 1}`}
            >
              <span
                className="cluster-shape"
                style={{ backgroundColor: CLUSTER_COLORS[i % CLUSTER_COLORS.length] }}
              />
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}