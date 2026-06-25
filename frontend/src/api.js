// Thin client for the SEALION backend (localhost:8000).
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function json(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  base: BASE,

  listPapers: () => fetch(`${BASE}/papers`).then(json),
  graph: () => fetch(`${BASE}/graph`).then(json),

  ingestUrl: (url) =>
    fetch(`${BASE}/papers/ingest-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }).then(json),

  uploadPdf: (file) => {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${BASE}/papers/upload`, { method: "POST", body: fd }).then(json);
  },

  pdfUrl: (id) => `${BASE}/papers/${id}/pdf`,

  chat: (question, paperIds) =>
    fetch(`${BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, paper_ids: paperIds }),
    }).then(json),
};
