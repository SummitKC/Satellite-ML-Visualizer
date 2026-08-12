import  "../../styles.css";

interface TopBarProps {
    totalSatellites: number; 
    totalClusters: number;

}

export function TopBar({ totalSatellites, totalClusters }: TopBarProps) {
  return (
    <div className="top-bar">
      <header>
        <h1>Satellite Visualizer</h1>
          <div className="bar-stats">
            <p>Total Satellites: {totalSatellites}</p>
            <p>Total Clusters: {totalClusters}</p>
          </div>
        <ul className="satellite-clusters">
          {Array.from({ length: totalClusters }, (_, i) => (
            <li key={i} className="cluster">
              Cluster {i + 1}
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}