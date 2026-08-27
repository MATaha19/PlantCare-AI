import { useState, useRef, useEffect } from "react";
import {
  Upload,
  Camera,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Activity,
  ShieldCheck,
  Percent,
  Sprout,
  Maximize2,
  FileImage
} from "lucide-react";
import { predictImage } from "../services/api";
import SeverityVisualizer from "../components/SeverityVisualizer";
import TreatmentCard from "../components/TreatmentCard";
import ErrorAlert from "../components/ErrorAlert";

export default function ImageAnalysisPage({ onOpenSupportedModal }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  // Camera state
  const [cameraOpen, setCameraOpen] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Analysis state
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      stopCamera();
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, []);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOpen(false);
  };

  const openCamera = async () => {
    resetAnalysis();
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      streamRef.current = stream;
      setCameraOpen(true);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch(() => {});
        }
      }, 100);
    } catch (err) {
      setError({
        statusType: "generic",
        message: "Camera permission denied or camera not found on this device.",
      });
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setError({ statusType: "generic", message: "Failed to capture photo frame." });
          return;
        }
        const file = new File([blob], `plant-capture-${Date.now()}.jpg`, { type: "image/jpeg" });
        handleFileSelection(file);
        stopCamera();
      },
      "image/jpeg",
      0.95
    );
  };

  const handleFileSelection = (file) => {
    if (!file) return;
    resetAnalysis();

    if (!file.type.startsWith("image/")) {
      setError({
        statusType: "generic",
        message: "Unsupported file format. Please choose a JPG, JPEG, or PNG image.",
      });
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError({
        statusType: "generic",
        message: "File size exceeds 10 MB limit. Please select a smaller photo.",
      });
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    const url = URL.createObjectURL(file);
    setSelectedFile(file);
    setPreviewUrl(url);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelection(file);
  };

  const resetAnalysis = () => {
    setResult(null);
    setError(null);
  };

  const clearAll = () => {
    stopCamera();
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl("");
    resetAnalysis();
  };

  // Perform backend prediction
  const handleAnalyze = async () => {
    if (!selectedFile) return;

    resetAnalysis();
    setLoading(true);
    setLoadingStep("Validating Plant Species (Plant Validator)...");

    const timer1 = setTimeout(() => {
      setLoadingStep("Inference via 15-Class CNN Disease Model...");
    }, 600);

    const timer2 = setTimeout(() => {
      setLoadingStep("Estimating Severity & Lesion Mask...");
    }, 1200);

    try {
      const data = await predictImage(selectedFile);
      setResult(data);
      setTimeout(() => {
        const resultsEl = document.getElementById("analysis-results");
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);
    } catch (err) {
      setError(err);
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      setLoading(false);
      setLoadingStep("");
    }
  };

  const prediction = result?.prediction;
  const severity = result?.severity;
  const top3 = result?.top_3_predictions || [];
  const treatment = result?.treatment;

  const isHealthy =
    prediction?.disease_detected === false ||
    prediction?.plant_status === "Healthy" ||
    prediction?.class?.toLowerCase().includes("healthy");

  const plantName = prediction?.class?.split(" — ")?.[0]?.trim() || "Plant";
  const diseaseName = prediction?.class?.split(" — ")?.[1]?.trim() || prediction?.class || "Status";

  return (
    <div className="page-analysis">
      {/* Header */}
      <div className="analysis-page-header">
        <span className="eyebrow">IMAGE DIAGNOSTIC LAB</span>
        <h2>Plant Disease & Severity Screening</h2>
        <p>
          Upload or capture a close-up photo of a plant leaf. PlantCare-AI will validate the plant,
          classify diseases, and calculate visible severity percentage.
        </p>
      </div>

      {/* Main Upload / Camera Area */}
      <div className="analysis-card upload-section-card">
        {!cameraOpen ? (
          <div>
            {!selectedFile ? (
              <div
                className={`drop-zone ${isDragOver ? "drag-over" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragOver(true);
                }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
              >
                <div className="drop-zone-icon-box">
                  <Upload size={36} className="text-emerald" />
                </div>
                <h3>Drag & Drop Plant Leaf Photo</h3>
                <p className="drop-subtext">Supports JPG, JPEG, PNG (Max 10 MB)</p>

                <div className="drop-actions-row">
                  <label className="btn-primary cursor-pointer">
                    <FileImage size={18} /> Choose File
                    <input
                      type="file"
                      accept="image/jpeg,image/jpg,image/png"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileSelection(file);
                      }}
                      hidden
                    />
                  </label>

                  <button className="btn-outline" onClick={openCamera}>
                    <Camera size={18} /> Use Camera
                  </button>
                </div>

                <div className="supported-quick-reminder">
                  <span>Supported:</span>
                  <span className="pill">🍅 Tomato</span>
                  <span className="pill">🥔 Potato</span>
                  <span className="pill">🌶️ Bell Pepper</span>
                </div>
              </div>
            ) : (
              /* Selected Image Preview Area */
              <div className="selected-preview-card">
                <div className="preview-header-bar">
                  <div className="file-info-text">
                    <span className="file-name">{selectedFile.name}</span>
                    <span className="file-size">
                      ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </span>
                  </div>
                  <button className="btn-clear" onClick={clearAll} title="Remove image">
                    <RotateCcw size={16} /> Reset
                  </button>
                </div>

                <div className="preview-image-container">
                  <img src={previewUrl} alt="Selected leaf preview" className="preview-img" />
                </div>

                <div className="preview-controls-bar">
                  <button
                    className="btn-analyze"
                    onClick={handleAnalyze}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Activity className="spin-slow" size={20} />
                        <span>Analyzing Leaf...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={20} />
                        <span>Run AI Disease Analysis</span>
                      </>
                    )}
                  </button>
                </div>

                {loading && (
                  <div className="loading-progress-box">
                    <div className="loading-bar-animated" />
                    <p className="loading-step-text">{loadingStep}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          /* Live Camera Viewfinder */
          <div className="camera-viewfinder-card">
            <div className="camera-header-bar">
              <span className="camera-title">Live Camera Capture</span>
              <button className="btn-clear" onClick={stopCamera}>
                Cancel
              </button>
            </div>

            <div className="video-stream-box">
              <video ref={videoRef} autoPlay playsInline muted className="camera-video-element" />
              <div className="camera-target-crosshair" />
            </div>

            <div className="camera-controls-bar">
              <button className="btn-capture-photo" onClick={capturePhoto}>
                <div className="capture-inner-dot" />
              </button>
              <span className="capture-hint">Tap to capture leaf photo</span>
            </div>
          </div>
        )}
      </div>

      {/* Error Alert Display */}
      {error && (
        <div className="mt-6">
          <ErrorAlert
            error={error}
            onRetry={handleAnalyze}
            onReset={clearAll}
            onOpenSupportedModal={onOpenSupportedModal}
          />
        </div>
      )}

      {/* Results Section */}
      {result && prediction && (
        <div id="analysis-results" className="analysis-results-wrapper">
          {/* Healthy vs Disease Hero Banner */}
          {isHealthy ? (
            <div className="healthy-hero-banner">
              <div className="healthy-icon-circle">
                <CheckCircle2 size={42} />
              </div>
              <div className="healthy-hero-text">
                <span className="healthy-tag">VERIFIED BY PLANTCARE-AI</span>
                <h2>Healthy {plantName} Plant</h2>
                <p>
                  No active foliar disease or pathogenic lesions were detected on this leaf sample.
                  Standard preventive agronomic maintenance is recommended.
                </p>
              </div>
            </div>
          ) : (
            <div className="disease-hero-banner">
              <div className="disease-icon-circle">
                <AlertCircle size={42} />
              </div>
              <div className="disease-hero-text">
                <span className="disease-tag">PATHOGEN DETECTED</span>
                <h2>{prediction.class}</h2>
                <p>
                  Disease symptoms identified on <strong>{plantName}</strong> with{" "}
                  <strong>{prediction.confidence}%</strong> confidence.
                </p>
              </div>
            </div>
          )}

          {/* Metric Cards Grid */}
          <div className="metrics-grid">
            {/* 1. Plant Species & Validator */}
            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-label">Identified Plant</span>
                <Sprout className="metric-icon text-emerald" size={20} />
              </div>
              <div className="metric-value">{plantName}</div>
              <div className="metric-sub-badge bg-green-sub">
                <ShieldCheck size={14} /> Species Validated
              </div>
            </div>

            {/* 2. Disease Condition */}
            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-label">Condition</span>
                <Activity className="metric-icon text-blue" size={20} />
              </div>
              <div className="metric-value text-capitalize">{diseaseName}</div>
              <div className="metric-sub-badge bg-blue-sub">
                {isHealthy ? "✓ Optimal Foliage" : "⚠ Pathogen Found"}
              </div>
            </div>

            {/* 3. AI Confidence */}
            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-label">Model Confidence</span>
                <Percent className="metric-icon text-purple" size={20} />
              </div>
              <div className="metric-value">{prediction.confidence}%</div>
              <div className="confidence-meter-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${Math.min(prediction.confidence, 100)}%` }}
                />
              </div>
            </div>

            {/* 4. Severity Assessment */}
            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-label">Disease Severity</span>
                <Activity className="metric-icon text-amber" size={20} />
              </div>
              <div className="metric-value">
                {isHealthy ? "No disease" : severity?.level || "Unknown"}
              </div>
              <div className="metric-sub-badge bg-amber-sub">
                Affected Area: {isHealthy ? "0.00" : severity?.affected_area_percentage}%
              </div>
            </div>
          </div>

          {/* Visual Analysis (Lesion Segmenter & Heatmap) */}
          <div className="mt-8">
            <SeverityVisualizer
              imageUrl={previewUrl}
              severity={severity}
              isHealthy={isHealthy}
            />
          </div>

          {/* Top 3 Predictions */}
          {top3.length > 0 && (
            <div className="top3-predictions-card">
              <div className="top3-header">
                <span className="eyebrow">NEURAL NETWORK CONFIDENCE DISTRIBUTION</span>
                <h3>Top 3 Disease Candidates</h3>
              </div>
              <div className="top3-list">
                {top3.map((item, idx) => (
                  <div key={idx} className="top3-item">
                    <div className="top3-rank-badge">#{idx + 1}</div>
                    <div className="top3-info">
                      <div className="top3-name-row">
                        <span className="top3-name">{item.class}</span>
                        <span className="top3-pct">{item.confidence}%</span>
                      </div>
                      <div className="top3-bar-track">
                        <div
                          className="top3-bar-fill"
                          style={{ width: `${Math.min(item.confidence, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Treatment & Cultural Management */}
          {treatment && (
            <div className="mt-8">
              <TreatmentCard treatment={treatment} isHealthy={isHealthy} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
