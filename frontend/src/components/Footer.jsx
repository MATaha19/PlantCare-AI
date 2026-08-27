import { Leaf, ShieldCheck, Cpu, Database } from "lucide-react";

export default function Footer({ setActivePage, onOpenSupportedModal }) {
  return (
    <footer className="footer-container">
      <div className="footer-inner">
        <div className="footer-grid">
          {/* Col 1: Brand & Mission */}
          <div className="footer-brand-col">
            <div className="footer-brand">
              <div className="footer-logo-badge">
                <Leaf size={22} className="footer-leaf-icon" />
              </div>
              <span className="footer-brand-name">
                PlantCare<span className="accent">-AI</span>
              </span>
            </div>
            <p className="footer-tagline">
              Intelligent Computer Vision & Deep Learning system for rapid plant disease
              identification, severity screening, and agronomic management recommendations.
            </p>
            <div className="footer-badges">
              <span className="footer-badge">
                <Cpu size={13} /> Deep CNN Model
              </span>
              <span className="footer-badge">
                <ShieldCheck size={13} /> Plant Validator Layer
              </span>
              <span className="footer-badge">
                <Database size={13} /> 15 Disease Classes
              </span>
            </div>
          </div>

          {/* Col 2: Supported Plants */}
          <div className="footer-col">
            <h4>Supported Crops</h4>
            <ul className="footer-links">
              <li>
                <button className="footer-link-btn" onClick={onOpenSupportedModal}>
                  🍅 Tomato (10 Classes)
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={onOpenSupportedModal}>
                  🥔 Potato (3 Classes)
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={onOpenSupportedModal}>
                  🌶️ Bell Pepper (2 Classes)
                </button>
              </li>
              <li>
                <button className="footer-link-btn text-accent" onClick={onOpenSupportedModal}>
                  → View All 15 Disease Classes
                </button>
              </li>
            </ul>
          </div>

          {/* Col 3: Navigation */}
          <div className="footer-col">
            <h4>Quick Navigation</h4>
            <ul className="footer-links">
              <li>
                <button className="footer-link-btn" onClick={() => { setActivePage("home"); window.scrollTo(0, 0); }}>
                  Home Overview
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={() => { setActivePage("image"); window.scrollTo(0, 0); }}>
                  Leaf Image Diagnostics
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={() => { setActivePage("video"); window.scrollTo(0, 0); }}>
                  Video Temporal Analysis
                </button>
              </li>
              <li>
                <button className="footer-link-btn" onClick={() => { setActivePage("about"); window.scrollTo(0, 0); }}>
                  About System & Model
                </button>
              </li>
            </ul>
          </div>

          {/* Col 4: Notice */}
          <div className="footer-col">
            <h4>System Notice</h4>
            <p className="footer-disclaimer">
              PlantCare-AI is designed for agricultural disease screening and decision support.
              Always cross-reference with local agricultural extension guidelines and pesticide labels.
            </p>
          </div>
        </div>

        <div className="footer-bottom">
          <p>© {new Date().getFullYear()} PlantCare-AI • Computer Vision & Precision Agriculture Diagnostic System.</p>
          <div className="footer-bottom-links">
            <span>FastAPI Backend Connected</span>
            <span>•</span>
            <span>React 19 Frontend</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
