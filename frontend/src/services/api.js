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
  // Profiles & Master CV
  getProfiles: () => fetchJson("/profiles"),
  getProfile: (id) => fetchJson(`/profiles/${id}`),
  createProfile: (data) => fetchJson("/profiles", { method: "POST", body: JSON.stringify(data) }),
  updateProfile: (id, data) => fetchJson(`/profiles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  getProfileProjects: (profileId) => fetchJson(`/profiles/${profileId}/projects`),
  saveTailoredCV: (profileId, data) => fetchJson(`/profiles/${profileId}/save-tailored-cv`, { method: "POST", body: JSON.stringify(data) }),
  getSavedTailoredCVs: (profileId) => fetchJson(`/profiles/${profileId}/tailored-cvs`),
  deleteSavedTailoredCV: (profileId, cvId) => fetchJson(`/profiles/${profileId}/tailored-cvs/${cvId}`, { method: "DELETE" }),
  
  uploadMasterCV: async (file, profileId = null) => {
    const formData = new FormData();
    formData.append("file", file);
    const url = profileId
      ? `${API_BASE}/profiles/upload-master-cv?profile_id=${profileId}`
      : `${API_BASE}/profiles/upload-master-cv`;
    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Master CV upload failed: ${err}`);
    }
    return res.json();
  },

  uploadResume: async (file, profileId = null) => {
    return api.uploadMasterCV(file, profileId);
  },

  // Real-Time Portal Search (LinkedIn, Wellfound, Indeed, Glassdoor)
  getJobCategories: () => fetchJson("/jobs/categories"),
  searchJobPortals: (searchParams) =>
    fetchJson("/jobs/portal-search", {
      method: "POST",
      body: JSON.stringify(searchParams),
    }),
  rescoreJobs: (profileId = null) =>
    fetchJson(`/jobs/rescore${profileId ? `?profile_id=${profileId}` : ""}`, {
      method: "POST",
    }),

  // Jobs
  getJobs: () => fetchJson("/jobs"),
  getJob: (id) => fetchJson(`/jobs/${id}`),
  toggleJobWishlist: (jobId) => fetchJson(`/jobs/${jobId}/wishlist`, { method: "POST" }),
  markJobBrowsed: (jobId) => fetchJson(`/jobs/${jobId}/browse`, { method: "POST" }),
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

  // Applications & JD-Tailored ATS CV
  getApplications: () => fetchJson("/applications"),
  getApplication: (id) => fetchJson(`/applications/${id}`),
  toggleApplicationWishlist: (appId) => fetchJson(`/applications/${appId}/wishlist`, { method: "POST" }),
  tailorForJob: (jobId, profileId = null) =>
    fetchJson(`/applications/tailor-for-job/${jobId}${profileId ? `?profile_id=${profileId}` : ""}`, {
      method: "POST",
    }),
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
  getResumePdfUrl: (applicationId) =>
    `${API_BASE}/applications/${applicationId}/resume-pdf`,

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
