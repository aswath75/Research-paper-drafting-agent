export default function SectionTabs({
  sections,
  activeSection,
  onSelect,
  onRegenerate,
  regeneratingSection,
}) {
  if (!sections.length) {
    return (
      <div className="empty-state compact">
        <p>No generated sections yet. Your draft will appear here after generation.</p>
      </div>
    );
  }

  const selectedSection =
    sections.find((section) => section.name === activeSection) || sections[0];

  return (
    <div className="section-viewer">
      <div className="tab-row">
        {sections.map((section) => (
          <button
            className={`tab-button ${selectedSection.name === section.name ? "active" : ""}`}
            key={section.name}
            onClick={() => onSelect(section.name)}
            type="button"
          >
            {section.name}
          </button>
        ))}
      </div>

      <div className="section-card">
        <div className="section-heading-row">
          <div>
            <h3>{selectedSection.name}</h3>
            <p>{selectedSection.status === "reviewed" ? "Reviewed output" : "Generated output"}</p>
          </div>
          <button
            className="ghost-button"
            onClick={() => onRegenerate(selectedSection.name)}
            type="button"
            disabled={regeneratingSection === selectedSection.name}
          >
            {regeneratingSection === selectedSection.name ? "Regenerating..." : "Regenerate Section"}
          </button>
        </div>

        <div className="section-body">
          <p>{selectedSection.content}</p>
        </div>

        <div className="section-citations">
          <span>Citations</span>
          <div className="citation-tags">
            {selectedSection.citations?.length ? (
              selectedSection.citations.map((citation) => (
                <span className="citation-tag" key={citation}>
                  {citation}
                </span>
              ))
            ) : (
              <span className="muted-text">No citation labels in this section.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
