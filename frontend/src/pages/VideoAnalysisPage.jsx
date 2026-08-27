import { useState, useRef, useEffect } from "react";
import {
  Video,
  Upload,
  RotateCcw,
  Sparkles,
  Activity,
  CheckCircle2,
  AlertCircle,
  Clock,
  Film,
  Search,
  Filter,
  Layers,
  Percent,
  Play,
  Square
} from "lucide-react";
import { analyzeVideo } from "../services/api";
import TreatmentCard from "../components/TreatmentCard";
import ErrorAlert from "../components/ErrorAlert";

export default function VideoAnalysisPage({ onOpenSupportedModal }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const recordingTimerRef = useRef(null);

  // Analysis state
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Table filtering
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");

  useEffect(() => {
    return () => {
      stopRecording();
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      if (recordingTimerRef.current) clearInterval(recordingTimerRef.current);
    };
  }, []);

  const handleFileSelection = (file) => {
    if (!file) return;
    setResult(null);
    setError(null);

    const allowedExtensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"];
    const ext = "." + file.name.split(".").pop().toLowerCase();

    if (!allowedExtensions.includes(ext) && !file.type.startsWith("video/")) {
      setError({
        statusType: "generic",
        message: "Unsupported video format. Please upload MP4, AVI, MOV, MKV, or WEBM.",
      });
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError({
        statusType: "generic",
        message: "Video exceeds maximum allowed size of 50 MB.",
      });
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    const url = URL.createObjectURL(file);
    setSelectedFile(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelection(file);
  };

  // Video recording
  const startRecording = async () => {
    setResult(null);
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });

      streamRef.current = stream;
      recordedChunksRef.current = [];

      let mimeType = "video/webm";
      if (MediaRecorder.isTypeSupported("video/webm;codecs=vp9")) {
        mimeType = "video/webm;codecs=vp9";
      } else if (MediaRecorder.isTypeSupported("video/webm;codecs=vp8")) {
        mimeType = "video/webm;codecs=vp8";
      }

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(recordedChunksRef.current, { type: "video/webm" });
        const file = new File([blob], `crop-video-${Date.now()}.webm`, { type: "video/webm" });
        handleFileSelection(file);
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }
      };

      recorder.start();
      setIsRecording(true);
      setRecordingSeconds(0);

      recordingTimerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setError({
        statusType: "generic",
        message: "Unable to access video camera. Please check browser permissions.",
      });
    }
  };

  const stopRecording = () => {
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const clearAll = () => {
    stopRecording();
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl("");
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setResult(null);
    setError(null);
    setLoading(true);
    setLoadingStep("Extracting and sampling video frames...");

    const t1 = setTimeout(() => {
      setLoadingStep("Validating plants & classifying diseases per frame...");
    }, 1200);

    const t2 = setTimeout(() => {
      setLoadingStep("Computing disease distribution and overall severity...");
    }, 2800);

    try {
      const data = await analyzeVideo(selectedFile);
      setResult(data);
      setTimeout(() => {
        const el = document.getElementById("video-results");
        if (el) el.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err);
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      setLoading(false);
      setLoadingStep("");
    }
  };

  const overall = result?.overall_result;
  const videoStats = result?.video;
  const frameResults = result?.frame_results || [];
  const diseaseDist = result?.disease_distribution || {};
  const treatment = result?.treatment;

  const isHealthy =
    overall?.disease_detected === false ||
    overall?.plant_status === "Healthy" ||
    overall?.dominant_disease?.toLowerCase().includes("healthy");

  // Filter frame results table
  const filteredFrames = frameResults.filter((f) => {
    const matchesSearch = f.prediction?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity =
      severityFilter === "all" ||
      f.severity?.toLowerCase() === severityFilter.toLowerCase();
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="page-analysis">
      {/* Header */}
      <div className="analysis-page-header">
        <span className="eyebrow">MULTI-FRAME TEMPORAL DIAGNOSTICS</span>
        <h2>Crop Video Disease & Distribution Analysis</h2>
        <p>
          Upload field inspection videos or record live. PlantCare-AI samples video frames,
          tracks disease consistency, and computes aggregate severity distributions.
        </p>
      </div>

      {/* Upload / Record Card */}
      <div className="analysis-card upload-section-card">
        {!isRecording ? (
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
                  <Video size={36} className="text-emerald" />
                </div>
                <h3>Drag & Drop Plant Video</h3>
                <p className="drop-subtext">Supports MP4, AVI, MOV, MKV, WEBM (Max 50 MB)</p>

                <div className="drop-actions-row">
                  <label className="btn-primary cursor-pointer">
                    <Upload size={18} /> Choose Video File
                    <input
                      type="file"
                      accept="video/mp4,video/x-msvideo,video/quicktime,video/x-matroska,video/webm"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileSelection(file);
                      }}
                      hidden
                    />
                  </label>

                  <button className="btn-outline" onClick={startRecording}>
                    <Video size={18} /> Record Video
                  </button>
                </div>
              </div>
            ) : (
              /* Selected Video Preview Card */
              <div className="selected-preview-card">
                <div className="preview-header-bar">
                  <div className="file-info-text">
                    <span className="file-name">{selectedFile.name}</span>
                    <span className="file-size">
                      ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
                    </span>
                  </div>
                  <button className="btn-clear" onClick={clearAll}>
                    <RotateCcw size={16} /> Reset
                  </button>
                </div>

                <div className="preview-video-container">
                  <video src={previewUrl} controls className="preview-video-element" />
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
                        <span>Analyzing Frames...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={20} />
                        <span>Run Multi-Frame Analysis</span>
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
          /* Live Video Recording State */
          <div className="recording-view-box">
            <div className="recording-header">
              <span className="recording-pulse-dot" />
              <span>Recording Video... ({recordingSeconds}s)</span>
            </div>
            <p className="recording-sub">Pan smoothly across plant foliage and leaves.</p>
            <button className="btn-danger" onClick={stopRecording}>
              <Square size={18} /> Stop & Analyze Video
            </button>
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
      {result && overall && (
        <div id="video-results" className="analysis-results-wrapper">
          {/* Executive Summary Hero */}
          <div className={`video-hero-summary ${isHealthy ? "healthy-bg" : "disease-bg"}`}>
            <div className="video-hero-top">
              <span className="hero-eyebrow">VIDEO EXECUTIVE SUMMARY</span>
              <span className={`status-pill ${isHealthy ? "healthy" : "disease"}`}>
                {isHealthy ? "✓ Healthy Crop Video" : "⚠ Disease Detected In Crop Video"}
              </span>
            </div>
            <h2 className="video-dominant-title">
              {overall.dominant_disease || "Analysis Summary"}
            </h2>
            <div className="video-summary-meta">
              <span>Dominant Plant: <strong>{overall.plant}</strong></span>
              <span>•</span>
              <span>Avg Confidence: <strong>{overall.average_confidence}%</strong></span>
              <span>•</span>
              <span>Overall Severity: <strong>{overall.overall_severity}</strong></span>
            </div>
          </div>

          {/* Video Diagnostics Grid */}
          <div className="video-stats-grid">
            <div className="stat-card">
              <span className="stat-icon-wrap"><Clock size={18} /></span>
              <div>
                <span className="stat-num">{videoStats?.duration_seconds || 0}s</span>
                <span className="stat-desc">Video Duration</span>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon-wrap"><Film size={18} /></span>
              <div>
                <span className="stat-num">{videoStats?.total_frames || 0}</span>
                <span className="stat-desc">Total Video Frames</span>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon-wrap"><Layers size={18} /></span>
              <div>
                <span className="stat-num">{videoStats?.frames_analyzed || 0}</span>
                <span className="stat-desc">Sampled & Analyzed</span>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon-wrap text-emerald"><CheckCircle2 size={18} /></span>
              <div>
                <span className="stat-num text-emerald">{videoStats?.supported_frames || 0}</span>
                <span className="stat-desc">Supported Plant Frames</span>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon-wrap text-amber"><AlertCircle size={18} /></span>
              <div>
                <span className="stat-num text-amber">{videoStats?.unsupported_frames || 0}</span>
                <span className="stat-desc">Unsupported Frames</span>
              </div>
            </div>

            <div className="stat-card">
              <span className="stat-icon-wrap text-purple"><Percent size={18} /></span>
              <div>
                <span className="stat-num text-purple">{videoStats?.uncertain_frames || 0}</span>
                <span className="stat-desc">Uncertain Frames</span>
              </div>
            </div>
          </div>

          {/* Disease Distribution Chart */}
          {Object.keys(diseaseDist).length > 0 && (
            <div className="distribution-card">
              <div className="distribution-header">
                <span className="eyebrow">FREQUENCY DISTRIBUTION</span>
                <h3>Detected Conditions Across Analyzed Frames</h3>
              </div>

              <div className="distribution-bars-list">
                {Object.entries(diseaseDist).map(([condName, count]) => {
                  const total = videoStats?.usable_frames || videoStats?.frames_analyzed || 1;
                  const pct = Math.round((count / total) * 100);
                  const isHealthyCond = condName.toLowerCase().includes("healthy");

                  return (
                    <div key={condName} className="dist-row">
                      <div className="dist-label-row">
                        <span className="dist-name">{condName}</span>
                        <span className="dist-count">
                          <strong>{count} frames</strong> ({pct}%)
                        </span>
                      </div>
                      <div className="dist-bar-track">
                        <div
                          className={`dist-bar-fill ${isHealthyCond ? "bg-green" : "bg-red"}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Frame-by-Frame Data Table */}
          <div className="frame-table-card">
            <div className="frame-table-header">
              <div>
                <span className="eyebrow">DETAILED TIMELINE</span>
                <h3>Frame-by-Frame Diagnostic Log</h3>
              </div>

              <div className="table-filters-row">
                <div className="search-input-wrap">
                  <Search size={15} />
                  <input
                    type="text"
                    placeholder="Search condition..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                <div className="filter-select-wrap">
                  <Filter size={15} />
                  <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                  >
                    <option value="all">All Severities</option>
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                    <option value="no disease">No disease</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="table-responsive">
              <table className="frames-data-table">
                <thead>
                  <tr>
                    <th>Frame #</th>
                    <th>Diagnosis</th>
                    <th>Confidence</th>
                    <th>Affected Leaf %</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFrames.length > 0 ? (
                    filteredFrames.map((f, idx) => (
                      <tr key={idx}>
                        <td className="font-mono">#{f.frame}</td>
                        <td className="font-medium">{f.prediction}</td>
                        <td>
                          <span className="confidence-pill">{f.confidence}%</span>
                        </td>
                        <td>{f.affected_area_percentage}%</td>
                        <td>
                          <span
                            className={`severity-pill-table ${
                              f.severity === "Severe"
                                ? "sev-severe"
                                : f.severity === "Moderate"
                                ? "sev-moderate"
                                : f.severity === "Mild"
                                ? "sev-mild"
                                : "sev-healthy"
                            }`}
                          >
                            {f.severity}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="text-center py-6 text-muted">
                        No frames match your search or severity filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Treatment Section */}
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
