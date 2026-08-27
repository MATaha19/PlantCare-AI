import { useState, useEffect, useRef } from "react";
import { Eye, Layers, Sliders, Sparkles, CheckCircle2 } from "lucide-react";

export default function SeverityVisualizer({ imageUrl, severity, isHealthy }) {
  const [viewMode, setViewMode] = useState("side-by-side"); // "side-by-side" | "overlay"
  const [overlayOpacity, setOverlayOpacity] = useState(65);
  const [highlightColor, setHighlightColor] = useState("red"); // "red" | "amber" | "green"
  const canvasRef = useRef(null);
  const [isProcessingCanvas, setIsProcessingCanvas] = useState(true);

  // Generate lesion mask on canvas
  useEffect(() => {
    if (!imageUrl) return;

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageUrl;

    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      canvas.width = img.naturalWidth || 600;
      canvas.height = img.naturalHeight || 600;

      // Draw original
      ctx.drawImage(img, 0, 0);

      if (isHealthy) {
        setIsProcessingCanvas(false);
        return;
      }

      // Read pixel data to segment diseased/discolored leaf area
      try {
        const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imgData.data;

        // Color overlay tint
        const tint =
          highlightColor === "red"
            ? [239, 68, 68]
            : highlightColor === "amber"
            ? [245, 158, 11]
            : [16, 185, 129];

        for (let i = 0; i < data.length; i += 4) {
          const r = data[i];
          const g = data[i + 1];
          const b = data[i + 2];

          // Leaf pixel check (greenish / foliage)
          const isGreen = g > r * 0.85 && g > b * 0.8 && g > 40;
          // Diseased discoloration cue (brownish, yellowing, dark spot, pale necrotic spot)
          const isYellowing = r > 110 && g > 100 && b < 80 && Math.abs(r - g) < 45;
          const isBrownNecrotic = (r > g + 10 || (r > 60 && g < 75 && b < 60)) && r > 40;
          const isDarkSpot = (r + g + b) / 3 < 65 && Math.abs(r - g) > 8;

          const isDiseased = (isYellowing || isBrownNecrotic || isDarkSpot) && (isGreen || r > 50 || g > 40);

          if (isDiseased) {
            data[i] = Math.round(data[i] * 0.35 + tint[0] * 0.65);
            data[i + 1] = Math.round(data[i + 1] * 0.35 + tint[1] * 0.65);
            data[i + 2] = Math.round(data[i + 2] * 0.35 + tint[2] * 0.65);
          } else if (!isGreen && (r + g + b) / 3 > 220) {
            // Background dimming
            data[i] = Math.round(data[i] * 0.85);
            data[i + 1] = Math.round(data[i + 1] * 0.85);
            data[i + 2] = Math.round(data[i + 2] * 0.85);
          }
        }

        ctx.putImageData(imgData, 0, 0);
      } catch (err) {
        console.warn("Canvas visualizer error:", err);
      }

      setIsProcessingCanvas(false);
    };
  }, [imageUrl, highlightColor, isHealthy]);

  const affectedPct = severity?.affected_area_percentage ?? 0;
  const severityLevel = severity?.level || (isHealthy ? "No disease" : "Unknown");

  const getSeverityBadgeClass = (lvl) => {
    switch (lvl?.toLowerCase()) {
      case "mild":
        return "badge-mild";
      case "moderate":
        return "badge-moderate";
      case "severe":
        return "badge-severe";
      case "no disease":
        return "badge-healthy";
      default:
        return "badge-neutral";
    }
  };

  return (
    <div className="visualizer-card">
      <div className="visualizer-header">
        <div>
          <span className="eyebrow">COMPUTER VISION SEGMENTATION</span>
          <h3 className="visualizer-title">Lesion & Severity Visualization</h3>
        </div>

        <div className="visualizer-controls">
          <div className="mode-toggle-group">
            <button
              className={`toggle-btn ${viewMode === "side-by-side" ? "active" : ""}`}
              onClick={() => setViewMode("side-by-side")}
            >
              <Eye size={15} /> Side-by-Side
            </button>
            <button
              className={`toggle-btn ${viewMode === "overlay" ? "active" : ""}`}
              onClick={() => setViewMode("overlay")}
            >
              <Layers size={15} /> Blend Overlay
            </button>
          </div>
        </div>
      </div>

      {/* Main Image View Area */}
      <div className="visualizer-viewport">
        {viewMode === "side-by-side" ? (
          <div className="side-by-side-grid">
            {/* Original */}
            <div className="image-frame-box">
              <div className="frame-label">
                <span>Original Leaf Photo</span>
              </div>
              <div className="img-wrap">
                <img src={imageUrl} alt="Original plant leaf" className="view-image" />
              </div>
            </div>

            {/* Segmented Lesions */}
            <div className="image-frame-box">
              <div className="frame-label">
                <span>AI Lesion Segmentation Mask</span>
                <span className={`severity-pill-micro ${getSeverityBadgeClass(severityLevel)}`}>
                  {severityLevel} ({affectedPct}%)
                </span>
              </div>
              <div className="img-wrap">
                <canvas ref={canvasRef} className="view-image view-canvas" />
              </div>
            </div>
          </div>
        ) : (
          <div className="overlay-view-box">
            <div className="overlay-stack">
              <img src={imageUrl} alt="Original leaf" className="view-image base-layer" />
              <canvas
                ref={canvasRef}
                className="view-image blend-layer"
                style={{ opacity: overlayOpacity / 100 }}
              />
            </div>
            <div className="slider-control-bar">
              <Sliders size={16} />
              <span>Mask Opacity: {overlayOpacity}%</span>
              <input
                type="range"
                min="0"
                max="100"
                value={overlayOpacity}
                onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                className="opacity-slider"
              />
            </div>
          </div>
        )}
      </div>

      {/* Visualizer Footer Bar */}
      <div className="visualizer-footer">
        <div className="legend-items">
          <span className="legend-title">Visual Map:</span>
          {isHealthy ? (
            <span className="legend-item text-green">
              <CheckCircle2 size={15} /> Uniform Healthy Leaf Tissue (0% Lesion Area)
            </span>
          ) : (
            <>
              <span className="legend-item">
                <span className="dot dot-red" /> Highlighted Necrotic/Diseased Spots
              </span>
              <span className="legend-item">
                <span className="dot dot-green" /> Retained Healthy Leaf Tissue
              </span>
            </>
          )}
        </div>

        {!isHealthy && (
          <div className="highlight-color-picker">
            <span>Color Map:</span>
            <button
              className={`color-dot-btn dot-red ${highlightColor === "red" ? "active" : ""}`}
              onClick={() => setHighlightColor("red")}
              title="Crimson Highlight"
            />
            <button
              className={`color-dot-btn dot-amber ${highlightColor === "amber" ? "active" : ""}`}
              onClick={() => setHighlightColor("amber")}
              title="Thermal Amber"
            />
            <button
              className={`color-dot-btn dot-green ${highlightColor === "green" ? "active" : ""}`}
              onClick={() => setHighlightColor("green")}
              title="Bio-Green"
            />
          </div>
        )}
      </div>
    </div>
  );
}
