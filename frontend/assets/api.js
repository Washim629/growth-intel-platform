/* Use same-origin requests by default. Set window.API_BASE before this
   script when the frontend and backend are hosted separately. */
const API_BASE = (window.API_BASE || "").replace(/\/$/, "");

const Api = {
  token: localStorage.getItem("access_token") || null,

  setToken(token) {
    this.token = token;
    if (token) localStorage.setItem("access_token", token);
    else localStorage.removeItem("access_token");
  },

  async request(path, { method = "GET", body, isForm = false, isBlob = false, handleUnauthorized = true } = {}) {
    const headers = {};
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;
    if (!isForm && body !== undefined) headers["Content-Type"] = "application/json";

    const resp = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: isForm ? body : body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (resp.status === 401 && handleUnauthorized) {
      Api.setToken(null);
      State.user = null;
      Router.go("login");
      throw new Error("Session expired. Please log in again.");
    }

    if (isBlob) {
      if (!resp.ok) throw new Error(`Request failed (${resp.status})`);
      return resp.blob();
    }

    let data = null;
    try { data = await resp.json(); } catch (_) { /* no body */ }

    if (!resp.ok) {
      const detail = (data && data.detail) || `Request failed (${resp.status})`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return data;
  },

  // --- Auth ---
  register: (payload) => Api.request("/api/auth/register", { method: "POST", body: payload }),
  requestRegistrationOTP: (email) => Api.request("/api/auth/register/otp/request", { method: "POST", body: { email }, handleUnauthorized: false }),
  verifyRegistrationOTP: (email, code) => Api.request("/api/auth/register/otp/verify", { method: "POST", body: { email, code }, handleUnauthorized: false }),
  login: (payload) => Api.request("/api/auth/login", { method: "POST", body: payload }),
  requestLoginOTP: (email) => Api.request("/api/auth/login/otp/request", { method: "POST", body: { email }, handleUnauthorized: false }),
  verifyLoginOTP: (email, code) => Api.request("/api/auth/login/otp/verify", { method: "POST", body: { email, code }, handleUnauthorized: false }),
  me: () => Api.request("/api/auth/me"),
  changePassword: (payload) => Api.request("/api/auth/change-password", { method: "POST", body: payload }),

  // --- Datasets ---
  uploadDataset: (file) => {
    const form = new FormData();
    form.append("file", file);
    return Api.request("/api/datasets/upload", { method: "POST", body: form, isForm: true });
  },
  confirmMapping: (datasetId, mapping) =>
    Api.request(`/api/datasets/${datasetId}/mapping`, { method: "POST", body: { mapping } }),
  listDatasets: () => Api.request("/api/datasets"),
  getDataset: (id) => Api.request(`/api/datasets/${id}`),
  getDatasetRows: (id, page = 1, pageSize = 25, search = "") =>
    Api.request(`/api/datasets/${id}/rows?page=${page}&page_size=${pageSize}&search=${encodeURIComponent(search)}`),

  // --- Analysis ---
  startAnalysis: (datasetId) => Api.request(`/api/analysis/${datasetId}`, { method: "POST" }),
  getAnalysisStatus: (runId) => Api.request(`/api/analysis/${runId}`),

  // --- Analytics ---
  getKpis: (datasetId, params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return Api.request(`/api/kpis/${datasetId}${qs ? "?" + qs : ""}`);
  },
  getFunnel: (datasetId) => Api.request(`/api/funnel/${datasetId}`),
  getSegments: (datasetId, method = "rule_based") => Api.request(`/api/segments/${datasetId}?method=${method}`),
  getTrends: (datasetId, days = 30) => Api.request(`/api/trends/${datasetId}?days=${days}`),
  getAnomalies: (datasetId, days = 90) => Api.request(`/api/anomalies/${datasetId}?days=${days}`),

  // --- AI ---
  generateInsights: (datasetId) => Api.request(`/api/ai/insights/${datasetId}`, { method: "POST" }),
  getLatestInsights: (datasetId) => Api.request(`/api/ai/insights/${datasetId}/latest`),
  chat: (datasetId, question) => Api.request("/api/ai/chat", { method: "POST", body: { dataset_id: datasetId, question } }),

  // --- Experiments ---
  listExperiments: () => Api.request("/api/experiments"),
  createExperiment: (payload) => Api.request("/api/experiments", { method: "POST", body: payload }),
  updateExperiment: (id, payload) => Api.request(`/api/experiments/${id}`, { method: "PATCH", body: payload }),
  deleteExperiment: (id) => Api.request(`/api/experiments/${id}`, { method: "DELETE" }),

  // --- Reports ---
  createReport: (datasetId, title) => Api.request("/api/reports", { method: "POST", body: { dataset_id: datasetId, title } }),
  listReports: () => Api.request("/api/reports"),
  getReport: (id) => Api.request(`/api/reports/${id}`),
  // Export requires the auth header, so this returns a Blob (via Api.request)
  // rather than a plain URL - a bare <a href> would hit the API with no
  // token and get a 401. Callers turn the blob into a download themselves
  // (see downloadReportExport in app.js).
  exportReport: (id, format) => Api.request(`/api/reports/${id}/export?fmt=${encodeURIComponent(format)}`, { isBlob: true }),
};
