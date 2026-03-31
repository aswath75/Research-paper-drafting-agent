const metricCards = [
  { key: "readability_score", label: "Readability" },
  { key: "citation_accuracy", label: "Citation Accuracy" },
  { key: "structure_completeness", label: "Structure" },
  { key: "estimated_quality", label: "Quality" },
];

export default function MetricsPanel({ metrics }) {
  return (
    <div className="metrics-grid">
      {metricCards.map((item) => (
        <div className="metric-card" key={item.key}>
          <span className="metric-label">{item.label}</span>
          <strong className="metric-value">{metrics?.[item.key] ?? 0}%</strong>
        </div>
      ))}
    </div>
  );
}
