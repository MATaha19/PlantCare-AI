import { FlaskConical, Sprout, AlertTriangle, CheckCircle2, FileText } from "lucide-react";

export default function TreatmentCard({ treatment, isHealthy }) {
  if (!treatment) return null;

  return (
    <div className="treatment-card-container">
      <div className="treatment-main-header">
        <div className="treatment-badge-wrapper">
          <span className="treatment-eyebrow">MANAGEMENT PROTOCOL</span>
          <h3 className="treatment-condition-name">
            {treatment.condition || "Target Disease Management"}
          </h3>
        </div>
        <div className="treatment-meta-pills">
          {treatment.type && (
            <span className="treatment-type-pill">
              <Sprout size={14} /> {treatment.type}
            </span>
          )}
          {treatment.pathogen && treatment.pathogen !== "None detected" && (
            <span className="pathogen-pill">
              🔬 Pathogen: <em>{treatment.pathogen}</em>
            </span>
          )}
        </div>
      </div>

      <div className="treatment-sections-grid">
        {/* Chemical Management Card */}
        <div className="treatment-box chemical-box">
          <div className="treatment-box-header">
            <div className="box-icon-wrap chemical-icon-wrap">
              <FlaskConical size={20} />
            </div>
            <div>
              <h4>Chemical & Protective Treatment</h4>
              <span className="box-sub">
                {treatment.treatment_type || "Recommended Interventions"}
              </span>
            </div>
          </div>

          <div className="treatment-box-content">
            {treatment.active_ingredients && treatment.active_ingredients.length > 0 && (
              <div className="active-ingredients-block">
                <span className="ing-label">Active Ingredients / Compounds:</span>
                <div className="ingredient-tags">
                  {treatment.active_ingredients.map((ing, idx) => (
                    <span key={idx} className="ingredient-tag">
                      {ing}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="guidance-text-box">
              <FileText size={16} className="guidance-icon" />
              <p>{treatment.chemical_guidance}</p>
            </div>
          </div>
        </div>

        {/* Non-Chemical Cultural Management Card */}
        <div className="treatment-box organic-box">
          <div className="treatment-box-header">
            <div className="box-icon-wrap organic-icon-wrap">
              <Sprout size={20} />
            </div>
            <div>
              <h4>Cultural & Non-Chemical Management</h4>
              <span className="box-sub">Good Agricultural Practices</span>
            </div>
          </div>

          <div className="treatment-box-content">
            {treatment.non_chemical && treatment.non_chemical.length > 0 ? (
              <ul className="cultural-practices-list">
                {treatment.non_chemical.map((item, idx) => (
                  <li key={idx}>
                    <CheckCircle2 size={16} className="check-icon" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-practices-text">
                Maintain regular monitoring and standard sanitation protocols.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Safety Warning */}
      {treatment.warning && (
        <div className="safety-warning-banner">
          <div className="warning-icon-wrap">
            <AlertTriangle size={22} />
          </div>
          <div className="warning-text-wrap">
            <strong>Important Safety & Regional Regulation Warning</strong>
            <p>{treatment.warning}</p>
          </div>
        </div>
      )}
    </div>
  );
}
