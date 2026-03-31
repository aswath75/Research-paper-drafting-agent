const PIPELINE_STEPS = ["Planning", "Writing", "Reviewing", "Citation Checking"];

export default function ProgressSteps({ activeStep, isBusy }) {
  return (
    <div className="progress-card">
      <div className="section-heading-row">
        <h3>Generation Flow</h3>
        <span className={`status-pill ${isBusy ? "live" : ""}`}>
          {isBusy ? "Running" : "Ready"}
        </span>
      </div>
      <div className="step-list">
        {PIPELINE_STEPS.map((step, index) => {
          const isActive = activeStep === step;
          const isComplete = PIPELINE_STEPS.indexOf(activeStep) > index;
          return (
            <div className={`step-item ${isActive ? "active" : ""} ${isComplete ? "complete" : ""}`} key={step}>
              <span className="step-dot" />
              <span>{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
