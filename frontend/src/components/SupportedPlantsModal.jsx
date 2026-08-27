import { X, CheckCircle2, ShieldCheck, AlertCircle } from "lucide-react";

export default function SupportedPlantsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const plantsData = [
    {
      name: "Tomato",
      latin: "Solanum lycopersicum",
      icon: "🍅",
      badge: "10 Disease Classes",
      classes: [
        { name: "Tomato — Healthy", type: "Healthy" },
        { name: "Tomato — Early Blight", type: "Fungal", pathogen: "Alternaria solani" },
        { name: "Tomato — Late Blight", type: "Water mold", pathogen: "Phytophthora infestans" },
        { name: "Tomato — Bacterial Spot", type: "Bacterial", pathogen: "Xanthomonas spp." },
        { name: "Tomato — Leaf Mold", type: "Fungal", pathogen: "Passalora fulva" },
        { name: "Tomato — Septoria Leaf Spot", type: "Fungal", pathogen: "Septoria lycopersici" },
        { name: "Tomato — Spider Mites", type: "Mite Pest", pathogen: "Tetranychus urticae" },
        { name: "Tomato — Target Spot", type: "Fungal", pathogen: "Corynespora cassiicola" },
        { name: "Tomato — Yellow Leaf Curl Virus", type: "Viral", pathogen: "TYLCV" },
        { name: "Tomato — Mosaic Virus", type: "Viral", pathogen: "ToMV" },
      ],
    },
    {
      name: "Potato",
      latin: "Solanum tuberosum",
      icon: "🥔",
      badge: "3 Disease Classes",
      classes: [
        { name: "Potato — Healthy", type: "Healthy" },
        { name: "Potato — Early Blight", type: "Fungal", pathogen: "Alternaria solani" },
        { name: "Potato — Late Blight", type: "Water mold", pathogen: "Phytophthora infestans" },
      ],
    },
    {
      name: "Bell Pepper",
      latin: "Capsicum annuum",
      icon: "🌶️",
      badge: "2 Disease Classes",
      classes: [
        { name: "Bell Pepper — Healthy", type: "Healthy" },
        { name: "Bell Pepper — Bacterial Spot", type: "Bacterial", pathogen: "Xanthomonas spp." },
      ],
    },
  ];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-text">
            <span className="eyebrow">SYSTEM SPECIFICATIONS</span>
            <h2>Supported Plants & 15 Disease Classes</h2>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="modal-notice-banner">
            <ShieldCheck size={20} className="notice-icon" />
            <div>
              <strong>Strict Multi-Crop Support:</strong> PlantCare-AI is trained exclusively on these 3 crops. Non-supported plants (apple, corn, grapes, weeds, etc.) are blocked by the integrated AI Plant Validator.
            </div>
          </div>

          <div className="supported-plants-list">
            {plantsData.map((plant) => (
              <div key={plant.name} className="plant-modal-card">
                <div className="plant-modal-card-header">
                  <div className="plant-title-group">
                    <span className="plant-emoji">{plant.icon}</span>
                    <div>
                      <h3>{plant.name}</h3>
                      <span className="latin-name">{plant.latin}</span>
                    </div>
                  </div>
                  <span className="plant-class-count-badge">{plant.badge}</span>
                </div>

                <div className="classes-grid">
                  {plant.classes.map((cls, i) => (
                    <div
                      key={i}
                      className={`class-item-chip ${
                        cls.type === "Healthy" ? "chip-healthy" : "chip-disease"
                      }`}
                    >
                      <div className="chip-header">
                        <span className="chip-name">{cls.name}</span>
                        <span className="chip-type-tag">{cls.type}</span>
                      </div>
                      {cls.pathogen && (
                        <span className="chip-pathogen">
                          <em>{cls.pathogen}</em>
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-primary" onClick={onClose}>
            Got It
          </button>
        </div>
      </div>
    </div>
  );
}
