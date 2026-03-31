const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null
        ? data.detail || "Request failed."
        : "Request failed.";
    throw new Error(detail);
  }

  return data;
}

export async function generateFullDraft(payload) {
  return request("/generate-full", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function generateSection(payload) {
  return request("/generate-section", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function verifyCitations(payload) {
  return request("/verify-citations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function exportMarkdown(payload) {
  return request("/export-md", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function exportLatex(payload) {
  return request("/export-latex", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/upload-pdf", {
    method: "POST",
    body: formData,
  });
}
