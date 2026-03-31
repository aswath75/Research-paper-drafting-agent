import { useState } from "react";
import MetricsPanel from "./components/MetricsPanel";
import ProgressSteps from "./components/ProgressSteps";
import SectionTabs from "./components/SectionTabs";
import {
  exportLatex,
  exportMarkdown,
  generateFullDraft,
  generateSection,
  uploadPdf,
  verifyCitations,
} from "./lib/api";

const INITIAL_FORM = {
  topic: "Multi-Agent Systems for Scientific Writing Assistance",
  outline: "Abstract\nIntroduction\nRelated Work\nMethodology\nResults\nDiscussion\nConclusion",
  references:
    "OpenAI. AI systems for reasoning and drafting.\nhttps://doi.org/10.1145/nnnnnnn\nCrossref metadata best practices for scholarly work.",
  provider: "mock",
};

function downloadTextFile(content, filename, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function calculateMetrics(sections, references) {
  const fullText = sections.map((section) => section.content).join(" ");
  const wordCount = fullText.trim() ? fullText.trim().split(/\s+/).length : 0;
  const sentenceCount = Math.max((fullText.match(/[.!?]/g) || []).length, 1);
  const averageSentenceLength = wordCount / sentenceCount;
  const readability = Math.round(Math.max(45, Math.min(95, 100 - averageSentenceLength)) * 10) / 10;
  const structure = sections.length ? 100 : 0;

  let citationAccuracy = 55;
  if (references.length) {
    const validLabels = new Set(references.map((_, index) => `[${index + 1}]`));
    const citedLabels = sections.flatMap((section) => section.citations || []);
    citationAccuracy = citedLabels.length
      ? Math.round((citedLabels.filter((label) => validLabels.has(label)).length / citedLabels.length) * 1000) / 10
      : 40;
  }

  const estimatedQuality =
    Math.round((readability * 0.35 + citationAccuracy * 0.35 + structure * 0.3) * 10) / 10;

  return {
    readability_score: readability,
    citation_accuracy: citationAccuracy,
    structure_completeness: structure,
    estimated_quality: estimatedQuality,
  };
}

export default function App() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [draft, setDraft] = useState(null);
  const [activeSection, setActiveSection] = useState("");
  const [activeStep, setActiveStep] = useState("Planning");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [regeneratingSection, setRegeneratingSection] = useState("");
  const [error, setError] = useState("");
  const [citationMessage, setCitationMessage] = useState("");

  const draftSections = draft?.sections || [];
  const references = draft?.references || [];
  const metrics = draft?.metrics;

  const previewContent = (() => {
    if (!draftSections.length) {
      return "Your generated draft preview will appear here after the multi-agent pipeline completes.";
    }

    return draftSections
      .map((section) => `## ${section.name}\n\n${section.content}`)
      .join("\n\n");
  })();

  async function handleGenerateDraft(event) {
    event.preventDefault();
    setError("");
    setCitationMessage("");
    setIsGenerating(true);
    setDraft(null);
    setActiveSection("");
    let timerId = null;

    try {
      setActiveStep("Planning");
      const stepDelays = ["Writing", "Reviewing", "Citation Checking"];
      timerId = window.setInterval(() => {
        setActiveStep((current) => {
          const currentIndex = ["Planning", ...stepDelays].indexOf(current);
          return stepDelays[currentIndex] || "Citation Checking";
        });
      }, 900);

      const response = await generateFullDraft(form);
      window.clearInterval(timerId);
      setActiveStep("Citation Checking");
      setDraft(response.document);
      setActiveSection(response.document.sections?.[0]?.name || "");
    } catch (requestError) {
      setError(requestError.message || "Draft generation could not be completed.");
    } finally {
      if (timerId) {
        window.clearInterval(timerId);
      }
      setIsGenerating(false);
    }
  }

  async function handleRegenerateSection(sectionName) {
    setError("");
    setRegeneratingSection(sectionName);

    try {
      const updatedSection = await generateSection({
        ...form,
        section_name: sectionName,
      });

      setDraft((currentDraft) => {
        if (!currentDraft) {
          return currentDraft;
        }

        const nextSections = currentDraft.sections.map((section) =>
          section.name === sectionName ? updatedSection : section
        );

        return {
          ...currentDraft,
          sections: nextSections,
          markdown: nextSections.map((section) => `## ${section.name}\n\n${section.content}`).join("\n\n"),
          metrics: calculateMetrics(nextSections, currentDraft.references || []),
        };
      });
    } catch (requestError) {
      setError(requestError.message || `Section regeneration failed for ${sectionName}.`);
    } finally {
      setRegeneratingSection("");
    }
  }

  async function handleVerifyCitations() {
    if (!references.length) {
      setCitationMessage("Add references first to run citation verification.");
      return;
    }

    setError("");
    setCitationMessage("");
    setIsVerifying(true);

    try {
      const response = await verifyCitations({
        topic: form.topic,
        references,
      });

      setDraft((currentDraft) =>
        currentDraft
          ? {
              ...currentDraft,
              references: response.references,
              metrics: calculateMetrics(currentDraft.sections || [], response.references),
            }
          : currentDraft
      );
      setCitationMessage(`Citation verification complete. Accuracy: ${response.citation_accuracy}%.`);
    } catch (requestError) {
      setError(requestError.message || "Citation verification could not be completed.");
    } finally {
      setIsVerifying(false);
    }
  }

  async function handleExport(kind) {
    if (!draft) {
      setError("Generate a draft before exporting.");
      return;
    }

    setError("");

    try {
      const payload = {
        topic: draft.topic,
        sections: draft.sections,
        references: draft.references,
      };

      if (kind === "md") {
        const response = await exportMarkdown(payload);
        downloadTextFile(response.content, "research-draft.md", "text/markdown");
      } else {
        const response = await exportLatex(payload);
        downloadTextFile(response.content, "research-draft.tex", "application/x-tex");
      }
    } catch (requestError) {
      setError(requestError.message || "Export failed.");
    }
  }

  async function handlePdfUpload(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setError("");

    try {
      const response = await uploadPdf(file);
      const extractedText = response.extracted_references.join("\n");
      setForm((currentForm) => ({
        ...currentForm,
        references: currentForm.references
          ? `${currentForm.references}\n${extractedText}`.trim()
          : extractedText,
      }));
    } catch (requestError) {
      setError(requestError.message || "PDF processing failed.");
    } finally {
      event.target.value = "";
    }
  }

  return (
    <div className="app-shell">
      <div className="app-background" />
      <main className="app-frame">
        <section className="hero-strip">
          <div>
            <span className="eyebrow">AI Academic Workspace</span>
            <h1>Multi-Agent Research Paper Drafting System</h1>
            <p>
              Plan, write, review, and verify research drafts through a clean multi-agent pipeline.
            </p>
          </div>

          <div className="provider-box">
            <label htmlFor="provider">LLM Provider</label>
            <select
              id="provider"
              value={form.provider}
              onChange={(event) => setForm((current) => ({ ...current, provider: event.target.value }))}
            >
              <option value="mock">Mock</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
            </select>
          </div>
        </section>

        <div className="layout-grid">
          <section className="panel glass-panel">
            <div className="section-heading-row">
              <div>
                <span className="panel-kicker">Input Panel</span>
                <h2>Draft Setup</h2>
              </div>
            </div>

            <form className="input-form" onSubmit={handleGenerateDraft}>
              <label>
                Topic
                <input
                  type="text"
                  value={form.topic}
                  onChange={(event) => setForm((current) => ({ ...current, topic: event.target.value }))}
                  placeholder="Enter your research topic"
                />
              </label>

              <label>
                Outline
                <textarea
                  rows="7"
                  value={form.outline}
                  onChange={(event) => setForm((current) => ({ ...current, outline: event.target.value }))}
                  placeholder="Add one section per line"
                />
              </label>

              <label>
                References
                <textarea
                  rows="7"
                  value={form.references}
                  onChange={(event) => setForm((current) => ({ ...current, references: event.target.value }))}
                  placeholder="Paste references or URLs"
                />
              </label>

              <label className="upload-field">
                <span>Upload PDF for reference extraction</span>
                <input accept=".pdf" type="file" onChange={handlePdfUpload} />
              </label>

              <button className="primary-button" disabled={isGenerating} type="submit">
                {isGenerating ? "Generating Draft..." : "Generate Full Draft"}
              </button>
            </form>

            <ProgressSteps activeStep={activeStep} isBusy={isGenerating || isVerifying} />

            {error ? <div className="feedback error">{error}</div> : null}
            {citationMessage ? <div className="feedback info">{citationMessage}</div> : null}
          </section>

          <section className="panel output-panel">
            <div className="section-heading-row">
              <div>
                <span className="panel-kicker">Output Panel</span>
                <h2>Draft Output</h2>
              </div>
              <div className="action-row">
                <button className="ghost-button" onClick={handleVerifyCitations} type="button" disabled={isVerifying}>
                  {isVerifying ? "Verifying..." : "Verify Citations"}
                </button>
                <button className="ghost-button" onClick={() => handleExport("md")} type="button">
                  Download Markdown
                </button>
                <button className="ghost-button" onClick={() => handleExport("tex")} type="button">
                  Download LaTeX
                </button>
              </div>
            </div>

            <MetricsPanel metrics={metrics} />

            <div className="preview-card">
              <div className="section-heading-row">
                <h3>Draft Preview</h3>
                <span className="muted-text scroll-hint">Scrollable preview</span>
              </div>
              <pre>{previewContent}</pre>
            </div>

            <SectionTabs
              sections={draftSections}
              activeSection={activeSection}
              onSelect={setActiveSection}
              onRegenerate={handleRegenerateSection}
              regeneratingSection={regeneratingSection}
            />

            <div className="reference-card">
              <div className="section-heading-row">
                <h3>Reference Verification</h3>
                <span className="muted-text">{references.length} sources</span>
              </div>
              {references.length ? (
                <div className="reference-list">
                  {references.map((reference, index) => (
                    <div className="reference-item" key={`${reference.raw}-${index}`}>
                      <div>
                        <strong>{reference.title || reference.raw}</strong>
                        <p>{reference.message || "Awaiting verification."}</p>
                      </div>
                      <span className={`verification-badge ${reference.verified ? "verified" : "flagged"}`}>
                        {reference.verified ? "Verified" : "Flagged"}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state compact">
                  <p>Reference checks will appear here after draft generation or verification.</p>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
