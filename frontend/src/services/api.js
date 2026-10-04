const API_BASE = "http://localhost:8000/api";

export async function fetchJson(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export const api = {
  // Profiles
  getProfiles: () => fetchJson("/profiles"),
  getProfile: (id) => fetchJson(`/profiles/${id}`),
  createProfile: (data) => fetchJson("/profiles", { method: "POST", body: JSON.stringify(data) }),
  updateProfile: (id, data) => fetchJson(`/profiles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  uploadResume: async (file, profileId = null) => {
    const formData = new FormData();
    formData.append("file", file);
    const url = profileId ? `${API_BASE}/profiles/upload-resume?profile_id=${profileId}` : `${API_BASE}/profiles/upload-resume`;
    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Resume upload failed");
    return res.json();
  },

  // Jobs
  getJobs: () => fetchJson("/jobs"),
  getJob: (id) => fetchJson(`/jobs/${id}`),
  searchJobsPreview: (q) => fetchJson(`/jobs/search/preview?q=${encodeURIComponent(q)}`),
  analyzeCustomJD: (jdText, title = "", company = "", profileId = null) =>
    fetchJson("/jobs/analyze-custom-jd", {
      method: "POST",
      body: JSON.stringify({
        jd_text: jdText,
        title,
        company,
        profile_id: profileId,
      }),
    }),

  // Applications
  getApplications: () => fetchJson("/applications"),
  getApplication: (id) => fetchJson(`/applications/${id}`),
  preparePortalPrefill: (id) =>
    fetchJson(`/applications/${id}/prepare-portal`, { method: "POST" }),
  approveApplication: (id, approvalData) =>
    fetchJson(`/applications/${id}/approval`, {
      method: "POST",
      body: JSON.stringify(approvalData),
    }),
  provideMissingInfo: (id, answers) =>
    fetchJson(`/applications/${id}/provide-missing-info`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),

  // Autonomous Agent
  runAgent: (profileId, goal, freeFormGoal = null) =>
    fetchJson("/agent/run", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, goal, free_form_goal: freeFormGoal }),
    }),
  stopAgent: () => fetchJson("/agent/stop", { method: "POST" }),

  // Tracker & Dashboard
  getDashboardMetrics: () => fetchJson("/tracker/dashboard"),
  getTrackerEvents: () => fetchJson("/tracker/events"),
  getInterviewPrep: (appId) => fetchJson(`/tracker/interview-prep/${appId}`),
};
