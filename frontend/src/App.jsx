import { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import SupportedPlantsModal from "./components/SupportedPlantsModal";
import HomePage from "./pages/HomePage";
import ImageAnalysisPage from "./pages/ImageAnalysisPage";
import VideoAnalysisPage from "./pages/VideoAnalysisPage";
import AboutPage from "./pages/AboutPage";

export default function App() {
  const [activePage, setActivePage] = useState("home"); // "home" | "image" | "video" | "about"
  const [isSupportedModalOpen, setIsSupportedModalOpen] = useState(false);

  return (
    <div className="app-root">
      {/* Navigation */}
      <Navbar activePage={activePage} setActivePage={setActivePage} />

      {/* Page Content */}
      <main className="main-content">
        {activePage === "home" && (
          <HomePage
            setActivePage={setActivePage}
            onOpenSupportedModal={() => setIsSupportedModalOpen(true)}
          />
        )}

        {activePage === "image" && (
          <ImageAnalysisPage
            onOpenSupportedModal={() => setIsSupportedModalOpen(true)}
          />
        )}

        {activePage === "video" && (
          <VideoAnalysisPage
            onOpenSupportedModal={() => setIsSupportedModalOpen(true)}
          />
        )}

        {activePage === "about" && (
          <AboutPage
            onOpenSupportedModal={() => setIsSupportedModalOpen(true)}
          />
        )}
      </main>

      {/* Footer */}
      <Footer
        setActivePage={setActivePage}
        onOpenSupportedModal={() => setIsSupportedModalOpen(true)}
      />

      {/* Supported Plants Modal */}
      <SupportedPlantsModal
        isOpen={isSupportedModalOpen}
        onClose={() => setIsSupportedModalOpen(false)}
      />
    </div>
  );
}
