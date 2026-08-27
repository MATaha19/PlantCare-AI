import { Camera, Video, ShieldCheck, Activity, Cpu, Sparkles, ArrowRight, CheckCircle2, AlertTriangle, FileText, Layers, Database } from "lucide-react";

export default function HomePage({ setActivePage, onOpenSupportedModal }) {
  return (
    <div className="page-home">
      {/* 1. Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <Sparkles size={14} className="hero-badge-icon" />
            <span>AI-Powered Precision Agronomy</span>
          </div>

          <h1 className="hero-title">
            Protect Crop Yields With{" "}
            <span className="gradient-text">Intelligent Plant AI</span>
          </h1>

          <p className="hero-description">
            PlantCare-AI combines deep Convolutional Neural Networks (CNN) with digital image processing
            to identify supported crops, detect 15 foliar disease classes, estimate affected leaf severity,
            and recommend science-backed treatment plans.
          </p>

          <div className="hero-cta-group">
            <button
              className="btn-hero-primary"
              onClick={() => {
                setActivePage("image");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              <Camera size={20} />
              <span>Analyze Leaf Photo</span>
              <ArrowRight size={18} className="arrow-icon" />
            </button>

            <button
              className="btn-hero-secondary"
              onClick={() => {
                setActivePage("video");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              <Video size={20} />
              <span>Analyze Plant Video</span>
            </button>
          </div>

          {/* Quick Stats Banner */}
          <div className="hero-stats-row">
            <div className="stat-card">
              <span className="stat-number">3</span>
              <span className="stat-label">Supported Crops</span>
            </div>
            <div className="stat-divider" />
            <div className="stat-card">
              <span className="stat-number">15</span>
              <span className="stat-label">Disease & Healthy Classes</span>
            </div>
            <div className="stat-divider" />
            <div className="stat-card">
              <span className="stat-number">99%+</span>
              <span className="stat-label">AI Validation Accuracy</span>
            </div>
            <div className="stat-divider" />
            <div className="stat-card">
              <span className="stat-number">Real-Time</span>
              <span className="stat-label">Severity Estimation</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Supported Plants Banner */}
      <section className="supported-crops-section">
        <div className="section-header text-center">
          <span className="section-eyebrow">VALIDATED SPECIES</span>
          <h2 className="section-title">Supported Agricultural Crops</h2>
          <p className="section-subtitle">
            PlantCare-AI is strictly optimized for these three vital agricultural crops.
            Uploads of other plants are filtered by our validation pipeline.
          </p>
        </div>

        <div className="crops-card-grid">
          {/* Tomato Card */}
          <div className="crop-card">
            <div className="crop-card-top">
              <div className="crop-avatar tomato-bg">🍅</div>
              <div className="crop-badge-wrap">
                <span className="crop-badge">10 Classes</span>
              </div>
            </div>
            <h3 className="crop-name">Tomato</h3>
            <p className="crop-latin">Solanum lycopersicum</p>
            <p className="crop-desc">
              Detects Early Blight, Late Blight, Bacterial Spot, Leaf Mold, Septoria Spot, Spider Mites, Target Spot, Mosaic Virus, and Yellow Leaf Curl.
            </p>
            <div className="crop-footer">
              <span className="crop-status-tag">Full Diagnostic Support</span>
            </div>
          </div>

          {/* Potato Card */}
          <div className="crop-card">
            <div className="crop-card-top">
              <div className="crop-avatar potato-bg">🥔</div>
              <div className="crop-badge-wrap">
                <span className="crop-badge">3 Classes</span>
              </div>
            </div>
            <h3 className="crop-name">Potato</h3>
            <p className="crop-latin">Solanum tuberosum</p>
            <p className="crop-desc">
              Detects destructive Early Blight (<em>Alternaria solani</em>) and Late Blight (<em>Phytophthora infestans</em>) alongside healthy foliage.
            </p>
            <div className="crop-footer">
              <span className="crop-status-tag">Full Diagnostic Support</span>
            </div>
          </div>

          {/* Bell Pepper Card */}
          <div className="crop-card">
            <div className="crop-card-top">
              <div className="crop-avatar pepper-bg">🌶️</div>
              <div className="crop-badge-wrap">
                <span className="crop-badge">2 Classes</span>
              </div>
            </div>
            <h3 className="crop-name">Bell Pepper</h3>
            <p className="crop-latin">Capsicum annuum</p>
            <p className="crop-desc">
              Detects Bacterial Spot (<em>Xanthomonas campestris</em>) and healthy pepper leaves with tailored bactericidal management guidance.
            </p>
            <div className="crop-footer">
              <span className="crop-status-tag">Full Diagnostic Support</span>
            </div>
          </div>
        </div>

        <div className="text-center mt-6">
          <button className="btn-outline-lg" onClick={onOpenSupportedModal}>
            <Database size={16} /> View All 15 Model Disease Classes
          </button>
        </div>
      </section>

      {/* 3. Core Features Section */}
      <section className="features-section">
        <div className="section-header text-center">
          <span className="section-eyebrow">INTELLIGENT PIPELINE</span>
          <h2 className="section-title">Engineered For Agricultural Precision</h2>
          <p className="section-subtitle">
            A comprehensive four-stage diagnostic workflow designed for agronomists, researchers, and farmers.
          </p>
        </div>

        <div className="features-grid">
          {/* Feature 1 */}
          <div className="feature-box">
            <div className="feature-icon-wrapper bg-green-light">
              <ShieldCheck size={28} className="text-green" />
            </div>
            <h3>AI Plant Validation</h3>
            <p>
              Pre-screens uploaded images to confirm leaf presence and identify whether the subject is Tomato, Potato, or Bell Pepper before inference.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="feature-box">
            <div className="feature-icon-wrapper bg-emerald-light">
              <Cpu size={28} className="text-emerald" />
            </div>
            <h3>15-Class CNN Classifier</h3>
            <p>
              Deep Convolutional Neural Network trained on high-resolution PlantVillage foliar imagery, providing Top-3 confidence distributions.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="feature-box">
            <div className="feature-icon-wrapper bg-amber-light">
              <Activity size={28} className="text-amber" />
            </div>
            <h3>Severity & Lesion Mask</h3>
            <p>
              Segments diseased and necrotic lesions from healthy leaf tissue using HSV/Lab color space analysis to calculate the exact percentage affected.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="feature-box">
            <div className="feature-icon-wrapper bg-blue-light">
              <FileText size={28} className="text-blue" />
            </div>
            <h3>Treatment Protocols</h3>
            <p>
              Provides actionable active ingredients, chemical application guidance, non-chemical cultural practices, and safety cautions.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="feature-box">
            <div className="feature-icon-wrapper bg-purple-light">
              <Video size={28} className="text-purple" />
            </div>
            <h3>Temporal Video Analysis</h3>
            <p>
              Scans crop inspection videos, analyzes sampled frames, charts disease frequency distribution, and identifies dominant field conditions.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="feature-box">
            <div className="feature-icon-wrapper bg-teal-light">
              <Layers size={28} className="text-teal" />
            </div>
            <h3>Mismatch & Error Guard</h3>
            <p>
              Rejects ambiguous images, low confidence predictions, and plant/disease inconsistencies to protect crops from erroneous treatments.
            </p>
          </div>
        </div>
      </section>

      {/* 4. Workflow Steps */}
      <section className="workflow-section">
        <div className="section-header text-center">
          <span className="section-eyebrow">HOW IT WORKS</span>
          <h2 className="section-title">4-Step Diagnostic Journey</h2>
        </div>

        <div className="workflow-steps-grid">
          <div className="workflow-step-card">
            <div className="step-number">01</div>
            <h4>Upload or Capture</h4>
            <p>Take a leaf photo with your camera or upload a field inspection image/video.</p>
          </div>

          <div className="workflow-step-card">
            <div className="step-number">02</div>
            <h4>Species Validation</h4>
            <p>The AI Plant Validator ensures the sample belongs to Tomato, Potato, or Bell Pepper.</p>
          </div>

          <div className="workflow-step-card">
            <div className="step-number">03</div>
            <h4>CNN Diagnosis</h4>
            <p>Deep neural network classifies disease condition and calculates lesion severity percentage.</p>
          </div>

          <div className="workflow-step-card">
            <div className="step-number">04</div>
            <h4>Actionable Treatment</h4>
            <p>Receive immediate chemical and cultural management steps to protect your crop.</p>
          </div>
        </div>
      </section>

      {/* 5. Bottom Call to Action */}
      <section className="cta-banner-section">
        <div className="cta-banner-inner">
          <h2>Ready To Diagnose Your Plants?</h2>
          <p>
            Experience instant AI plant health diagnosis powered by modern computer vision.
          </p>
          <div className="cta-buttons">
            <button
              className="btn-hero-primary"
              onClick={() => {
                setActivePage("image");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              <Camera size={18} /> Analyze Leaf Image
            </button>
            <button
              className="btn-hero-secondary"
              onClick={() => {
                setActivePage("video");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              <Video size={18} /> Analyze Plant Video
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
