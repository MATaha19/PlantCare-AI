/**
 * PlantCare-AI API Service
 * Centralized API client for communicating with the FastAPI backend.
 * Uses environment variable VITE_API_URL or defaults to local development URL http://127.0.0.1:8000.
 */

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  SUPPORTED_CLASSES: `${API_BASE_URL}/supported-classes`,
  PREDICT: `${API_BASE_URL}/predict`,
  ANALYZE_VIDEO: `${API_BASE_URL}/analyze-video`,
};

function normalizeApiError(errorData, status) {
  let message = "An error occurred during analysis.";
  let statusType = "generic";
  let details = null;

  if (typeof errorData === "string") {
    message = errorData;
  } else if (errorData?.detail) {
    if (typeof errorData.detail === "string") {
      message = errorData.detail;
    } else if (typeof errorData.detail === "object") {
      details = errorData.detail;
      message =
        details.message ||
        details.error ||
        details.reason ||
        "Analysis could not be completed.";

      const predStatus = (details.prediction_status || "").toLowerCase();
      if (predStatus.includes("unsupported")) {
        statusType = "unsupported";
      } else if (predStatus.includes("uncertain")) {
        statusType = "uncertain";
      } else if (predStatus.includes("mismatch") || predStatus.includes("rejected")) {
        statusType = "mismatch";
      }
    } else if (Array.isArray(errorData.detail)) {
      message = errorData.detail.map((d) => d.msg || d.message).join(", ");
    }
  } else if (errorData?.message) {
    message = errorData.message;
  }

  return {
    isApiError: true,
    status,
    statusType,
    message,
    details,
  };
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(ENDPOINTS.HEALTH, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Health check failed with HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    return {
      status: "offline",
      model_loaded: false,
      error: error.message,
    };
  }
}

export async function getSupportedClasses() {
  try {
    const response = await fetch(ENDPOINTS.SUPPORTED_CLASSES, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Supported classes request failed with HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to fetch supported classes:", error);
    return null;
  }
}

export async function predictImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(ENDPOINTS.PREDICT, {
      method: "POST",
      body: formData,
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw {
        isApiError: true,
        status: response.status,
        statusType: "generic",
        message: "The backend returned an unreadable response format.",
        details: null,
      };
    }

    if (!response.ok) {
      throw normalizeApiError(data, response.status);
    }

    return data;
  } catch (error) {
    if (error.isApiError) {
      throw error;
    }
    throw {
      isApiError: false,
      status: 0,
      statusType: "network",
      message:
        error.message ||
        "Unable to connect to the PlantCare AI backend. Please verify the FastAPI server is running on http://127.0.0.1:8000.",
      details: null,
    };
  }
}

export async function analyzeVideo(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(ENDPOINTS.ANALYZE_VIDEO, {
      method: "POST",
      body: formData,
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw {
        isApiError: true,
        status: response.status,
        statusType: "generic",
        message: "The backend returned an unreadable response format.",
        details: null,
      };
    }

    if (!response.ok) {
      throw normalizeApiError(data, response.status);
    }

    return data;
  } catch (error) {
    if (error.isApiError) {
      throw error;
    }
    throw {
      isApiError: false,
      status: 0,
      statusType: "network",
      message:
        error.message ||
        "Unable to connect to the PlantCare AI backend. Please verify the FastAPI server is running on http://127.0.0.1:8000.",
      details: null,
    };
  }
}
