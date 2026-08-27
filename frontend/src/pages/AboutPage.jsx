import { Leaf, Cpu, ShieldCheck, Activity, Database, CheckCircle2, Layers, FlaskConical, Code2 } from "lucide-react";

export default function AboutPage({ onOpenSupportedModal }) {
  return (
    <div className="page-about">
      {/* Header */}
      <div className="about-hero">
        <span className="eyebrow">SYSTEM OVERVIEW & ARCHITECTURE</span>
        <h1>About PlantCare-AI</h1>
        <p className="about-lead">
          An AI-powered plant disease detection and severity analysis system designed to assist
          agricultural producers, researchers, and agronomists in identifying common foliar diseases,
          screening visible damage severity, and applying science-based management protocols.
        </p>
      </div>

      {/* Pipeline Grid */}
      <div className="about-section">
        <h2 className="about-section-heading">Integrated Multi-Layer AI Architecture</h2>
        <div className="architecture-grid">
          {/* Layer 1 */}
          <div className="arch-card">
            <div className="arch-number">Layer 1</div>
            <div className="arch-icon-wrap bg-green-light">
              <ShieldCheck className="text-green" size={24} />
            </div>
            <h3>Plant Validator Layer</h3>
            <p>
              Pre-screens each uploaded leaf image to verify presence of a supported crop (Tomato, Potato, or Bell Pepper) using visual score metrics. Blocks out-of-domain images, weeds, and non-plant objects.
            </p>
          </div>

          {/* Layer 2 */}
          <div className="arch-card">
            <div className="arch-number">Layer 2</div>
            <div className="arch-icon-wrap bg-emerald-light">
              <Cpu className="text-emerald" size={24} />
            </div>
            <h3>15-Class CNN Disease Classifier</h3>
            <p>
              Deep Convolutional Neural Network trained on foliar plant disease datasets. Evaluates 15 discrete classes, validates compatibility with the species layer, and outputs calibrated Top-3 prediction probabilities.
            </p>
          </div>

          {/* Layer 3 */}
          <div className="arch-card">
            <div className="arch-number">Layer 3</div>
            <div className="arch-icon-wrap bg-amber-light">
              <Activity className="text-amber" size={24} />
            </div>
            <h3>Severity Estimation Engine</h3>
            <p>
              Employs HSV/Lab color segmentation, GrabCut foreground estimation, and lesion contour analysis to measure the precise percentage of leaf area affected by chlorosis and necrosis.
            </p>
          </div>

          {/* Layer 4 */}
          <div className="arch-card">
            <div className="arch-number">Layer 4</div>
            <div className="arch-icon-wrap bg-blue-light">
              <FlaskConical className="text-blue" size={24} />
            </div>
            <h3>Agronomic Treatment Engine</h3>
            <p>
              Maps positive identifications to actionable agricultural protocols, including chemical active ingredients, spray cautions, resistance management, and cultural sanitization practices.
            </p>
          </div>
        </div>
      </div>

      {/* Disease Model Reference Table */}
      <div className="about-section">
        <div className="section-header-row">
          <div>
            <h2 className="about-section-heading">Supported Crops & 15 Disease Classes</h2>
            <p className="text-muted">The exact 15 classes recognized by the PlantCare-AI CNN classifier.</p>
          </div>
          <button className="btn-outline" onClick={onOpenSupportedModal}>
            View Interactive Modal
          </button>
        </div>

        <div className="table-responsive">
          <table className="classes-summary-table">
            <thead>
              <tr>
                <th>Crop</th>
                <th>Disease Condition</th>
                <th>Pathogen / Type</th>
                <th>Classification</th>
              </tr>
            </thead>
            <tbody>
              {/* Bell Pepper */}
              <tr>
                <td rowSpan="2" className="crop-cell">🌶️ Bell Pepper</td>
                <td>Bell Pepper — Bacterial Spot</td>
                <td><em>Xanthomonas campestris</em></td>
                <td><span className="badge-severe-micro">Bacterial Disease</span></td>
              </tr>
              <tr>
                <td>Bell Pepper — Healthy</td>
                <td>None detected</td>
                <td><span className="badge-healthy-micro">Healthy</span></td>
              </tr>

              {/* Potato */}
              <tr>
                <td rowSpan="3" className="crop-cell">🥔 Potato</td>
                <td>Potato — Early Blight</td>
                <td><em>Alternaria solani</em></td>
                <td><span className="badge-mild-micro">Fungal Disease</span></td>
              </tr>
              <tr>
                <td>Potato — Late Blight</td>
                <td><em>Phytophthora infestans</em></td>
                <td><span className="badge-severe-micro">Water Mold</span></td>
              </tr>
              <tr>
                <td>Potato — Healthy</td>
                <td>None detected</td>
                <td><span className="badge-healthy-micro">Healthy</span></td>
              </tr>

              {/* Tomato */}
              <tr>
                <td rowSpan="10" className="crop-cell">🍅 Tomato</td>
                <td>Tomato — Bacterial Spot</td>
                <td><em>Xanthomonas spp.</em></td>
                <td><span className="badge-severe-micro">Bacterial</span></td>
              </tr>
              <tr>
                <td>Tomato — Early Blight</td>
                <td><em>Alternaria tomatophila</em></td>
                <td><span className="badge-mild-micro">Fungal</span></td>
              </tr>
              <tr>
                <td>Tomato — Late Blight</td>
                <td><em>Phytophthora infestans</em></td>
                <td><span className="badge-severe-micro">Water Mold</span></td>
              </tr>
              <tr>
                <td>Tomato — Leaf Mold</td>
                <td><em>Passalora fulva</em></td>
                <td><span className="badge-mild-micro">Fungal</span></td>
              </tr>
              <tr>
                <td>Tomato — Septoria Leaf Spot</td>
                <td><em>Septoria lycopersici</em></td>
                <td><span className="badge-mild-micro">Fungal</span></td>
              </tr>
              <tr>
                <td>Tomato — Spider Mites</td>
                <td><em>Tetranychus urticae</em></td>
                <td><span className="badge-moderate-micro">Mite Pest</span></td>
              </tr>
              <tr>
                <td>Tomato — Target Spot</td>
                <td><em>Corynespora cassiicola</em></td>
                <td><span className="badge-mild-micro">Fungal</span></td>
              </tr>
              <tr>
                <td>Tomato — Yellow Leaf Curl Virus</td>
                <td>TYLCV (Whitefly vector)</td>
                <td><span className="badge-severe-micro">Viral</span></td>
              </tr>
              <tr>
                <td>Tomato — Mosaic Virus</td>
                <td>ToMV</td>
                <td><span className="badge-severe-micro">Viral</span></td>
              </tr>
              <tr>
                <td>Tomato — Healthy</td>
                <td>None detected</td>
                <td><span className="badge-healthy-micro">Healthy</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="about-section">
        <h2 className="about-section-heading">Technology & Deployment Stack</h2>
        <div className="tech-stack-grid">
          <div className="tech-box">
            <h4>Backend</h4>
            <p>FastAPI • Python 3.11 • TensorFlow / Keras • OpenCV (cv2) • NumPy • Pillow</p>
          </div>
          <div className="tech-box">
            <h4>Frontend</h4>
            <p>React 19 • Vite • Modern Responsive CSS3 • Lucide React Icons</p>
          </div>
          <div className="tech-box">
            <h4>Safety & Reliability</h4>
            <p>Confidence validation • Species compatibility rejection • CORS protection • 10MB/50MB upload limits</p>
          </div>
        </div>
      </div>
    </div>
  );
}
