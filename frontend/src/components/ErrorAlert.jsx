import { AlertTriangle, XCircle, HelpCircle, ShieldAlert, RefreshCw, CheckCircle } from "lucide-react";

export default function ErrorAlert({ error, onRetry, onReset, onOpenSupportedModal }) {
  if (!error) return null;

  const statusType = error.statusType || "generic";
  const details = error.details || {};

  // 1. Unsupported Image / Video
  if (statusType === "unsupported") {
    return (
      <div className="error-card error-unsupported">
        <div className="error-card-header">
          <div className="error-icon-box bg-amber">
            <ShieldAlert size={26} className="text-amber" />
          </div>
          <div>
            <span className="error-eyebrow">VALIDATION REJECTED</span>
            <h3 className="error-title">Unsupported Plant Detected</h3>
          </div>
        </div>

        <div className="error-card-body">
          <p className="error-main-msg">
            {error.message || "The uploaded file does not contain a supported plant."}
          </p>

          <div className="supported-reminder-box">
            <h4>🌿 PlantCare-AI Currently Supports Only 3 Plants:</h4>
            <div className="supported-crops-row">
              <span className="crop-pill">🍅 Tomato</span>
              <span className="crop-pill">🥔 Potato</span>
              <span className="crop-pill">🌶️ Bell Pepper</span>
            </div>
            <p className="crop-subtext">
              Images containing weeds, background objects, other crops, or non-plant subjects are automatically filtered out by our AI Plant Validator.
            </p>
          </div>

          {details.reason && (
            <div className="error-detail-box">
              <strong>Validator Note:</strong> {details.reason}
            </div>
          )}
        </div>

        <div className="error-actions">
          <button className="btn-primary" onClick={onReset}>
            <RefreshCw size={16} /> Choose Supported Plant
          </button>
          {onOpenSupportedModal && (
            <button className="btn-outline" onClick={onOpenSupportedModal}>
              View Supported Classes
            </button>
          )}
        </div>
      </div>
    );
  }

  // 2. Prediction Uncertain
  if (statusType === "uncertain") {
    return (
      <div className="error-card error-uncertain">
        <div className="error-card-header">
          <div className="error-icon-box bg-purple">
            <HelpCircle size={26} className="text-purple" />
          </div>
          <div>
            <span className="error-eyebrow">LOW CONFIDENCE</span>
            <h3 className="error-title">Prediction Uncertain</h3>
          </div>
        </div>

        <div className="error-card-body">
          <p className="error-main-msg">
            {error.message || "The AI classifier could not make a confident disease identification."}
          </p>

          <div className="guidance-checklist">
            <h4>📸 Tips for a clear diagnosis:</h4>
            <ul>
              <li><CheckCircle size={15} /> Capture a single leaf close-up in clear daylight.</li>
              <li><CheckCircle size={15} /> Ensure lesions or spots are sharply in focus.</li>
              <li><CheckCircle size={15} /> Avoid heavy shadows, intense glare, or blurry motion.</li>
              <li><CheckCircle size={15} /> Use a plain background if possible.</li>
            </ul>
          </div>
        </div>

        <div className="error-actions">
          <button className="btn-primary" onClick={onReset}>
            <RefreshCw size={16} /> Upload Clearer Image
          </button>
          {onRetry && (
            <button className="btn-outline" onClick={onRetry}>
              Retry Analysis
            </button>
          )}
        </div>
      </div>
    );
  }

  // 3. Plant Prediction Mismatch / Analysis Rejected
  if (statusType === "mismatch") {
    return (
      <div className="error-card error-mismatch">
        <div className="error-card-header">
          <div className="error-icon-box bg-red">
            <XCircle size={26} className="text-red" />
          </div>
          <div>
            <span className="error-eyebrow">INCONSISTENCY DETECTED</span>
            <h3 className="error-title">Analysis Rejected</h3>
          </div>
        </div>

        <div className="error-card-body">
          <p className="error-main-msg">
            {error.message || "The plant validator and disease classifier produced inconsistent results."}
          </p>

          <div className="mismatch-info-box">
            {details.validated_plant && (
              <div>
                <strong>Validated Plant:</strong> {details.validated_plant}
              </div>
            )}
            {details.predicted_class && (
              <div>
                <strong>Conflicting Disease:</strong> {details.predicted_class}
              </div>
            )}
            <p className="mismatch-note">
              To prevent misdiagnosis and incorrect pesticide applications, PlantCare-AI rejects predictions where species identification conflicts with disease characteristics.
            </p>
          </div>
        </div>

        <div className="error-actions">
          <button className="btn-primary" onClick={onReset}>
            <RefreshCw size={16} /> Try Another Image
          </button>
        </div>
      </div>
    );
  }

  // 4. Generic / Network Error
  return (
    <div className="error-card error-generic">
      <div className="error-card-header">
        <div className="error-icon-box bg-red">
          <AlertTriangle size={26} className="text-red" />
        </div>
        <div>
          <span className="error-eyebrow">SYSTEM NOTIFICATION</span>
          <h3 className="error-title">Analysis Could Not Complete</h3>
        </div>
      </div>

      <div className="error-card-body">
        <p className="error-main-msg">{error.message || "An unexpected error occurred."}</p>
        {statusType === "network" && (
          <p className="error-network-hint">
            Please verify that the FastAPI backend is running locally on <code>http://127.0.0.1:8000</code> or that your network connection is active.
          </p>
        )}
      </div>

      <div className="error-actions">
        {onRetry && (
          <button className="btn-primary" onClick={onRetry}>
            <RefreshCw size={16} /> Retry
          </button>
        )}
        <button className="btn-outline" onClick={onReset}>
          Reset Selection
        </button>
      </div>
    </div>
  );
}
