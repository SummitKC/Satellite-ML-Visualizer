const CLUSTER_LEGEND = [
  { color: "#e63946", label: "Cluster 0 (e.g. LEO)" },
  { color: "#457b9d", label: "Cluster 1 (e.g. MEO)" },
  { color: "#2a9d8f", label: "Cluster 2 (e.g. GEO)" },
  { color: "#f4a261", label: "Cluster 3" },
  { color: "#9b5de5", label: "Cluster 4" },
];

interface SidebarProps {
  totalSatellites: number;
}

export function Sidebar({ totalSatellites }: SidebarProps) {
  return (
    <aside className="sidebar">
      <h1>Satellite ML Visualizer</h1>
      <p>Total satellites: {totalSatellites}</p>
      <h2>Cluster legend</h2>
      <ul className="legend">
        {CLUSTER_LEGEND.map((entry) => (
          <li key={entry.label}>
            <span className="legend-swatch" style={{ backgroundColor: entry.color }} />
            {entry.label}
          </li>
        ))}
      </ul>
    </aside>
  );
}
