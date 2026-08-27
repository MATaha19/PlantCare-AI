import { useState, useEffect } from "react";
import { Leaf, Activity, Camera, Video, Info, Home, Menu, X, CheckCircle2, AlertCircle } from "lucide-react";
import { checkBackendHealth } from "../services/api";

export default function Navbar({ activePage, setActivePage }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [backendHealth, setBackendHealth] = useState({
    status: "checking",
    classes: 15,
  });

  useEffect(() => {
    let mounted = true;

    async function verifyHealth() {
      const data = await checkBackendHealth();
      if (!mounted) return;
      if (data && data.status === "healthy") {
        setBackendHealth({
          status: "online",
          classes: data.supported_classes || 15,
        });
      } else {
        setBackendHealth({
          status: "offline",
          classes: 15,
        });
      }
    }

    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: "home", label: "Home", icon: Home },
    { id: "image", label: "Image Analysis", icon: Camera },
    { id: "video", label: "Video Analysis", icon: Video },
    { id: "about", label: "About", icon: Info },
  ];

  const handleNavClick = (pageId) => {
    setActivePage(pageId);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <header className="navbar-container">
      <div className="navbar-inner">
        {/* Brand */}
        <div className="navbar-brand" onClick={() => handleNavClick("home")} role="button" tabIndex={0}>
          <div className="brand-logo-badge">
            <Leaf className="brand-icon-svg" size={24} />
          </div>
          <div className="brand-text">
            <span className="brand-title">
              PlantCare<span className="brand-title-accent">-AI</span>
            </span>
            <span className="brand-subtitle">Smart Crop Health System</span>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="nav-desktop">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                className={`nav-link-btn ${isActive ? "active" : ""}`}
                onClick={() => handleNavClick(item.id)}
              >
                <Icon className="nav-icon" size={18} />
                <span>{item.label}</span>
                {isActive && <span className="active-pill-dot" />}
              </button>
            );
          })}
        </nav>

        {/* Backend Status Badge */}
        <div className="navbar-right">
          <div
            className={`backend-status-pill ${
              backendHealth.status === "online"
                ? "status-online"
                : backendHealth.status === "offline"
                ? "status-offline"
                : "status-checking"
            }`}
            title={`FastAPI backend status: ${backendHealth.status}`}
          >
            {backendHealth.status === "online" ? (
              <>
                <span className="status-ping-dot" />
                <CheckCircle2 size={14} className="status-icon" />
                <span className="status-text">AI Active (15 Classes)</span>
              </>
            ) : backendHealth.status === "offline" ? (
              <>
                <AlertCircle size={14} className="status-icon" />
                <span className="status-text">Backend Offline</span>
              </>
            ) : (
              <>
                <Activity size={14} className="status-icon spin-slow" />
                <span className="status-text">Connecting...</span>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="nav-mobile-drawer">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                className={`mobile-nav-link ${isActive ? "active" : ""}`}
                onClick={() => handleNavClick(item.id)}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
}
