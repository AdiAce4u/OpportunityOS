import React, { useState, useEffect } from "react";
import {
  Search,
  Globe,
  DollarSign,
  MapPin,
  ExternalLink,
  Sparkles,
  Layers,
  Briefcase,
  Cpu,
  Database,
  Code2,
  TrendingUp,
} from "lucide-react";
import { api } from "../services/api";

export function PortalJobDiscovery({ profile, onOpenReviewModal, onTailorAndApply }) {
  // 5 Tracks requested: "software", "data", "consult", "finance", "core"
  const [selectedTrack, setSelectedTrack] = useState("software");
  const [location, setLocation] = useState("India");
  const [isRemote, setIsRemote] = useState(false);
  const [resultsCount, setResultsCount] = useState(15);
  const [selectedSites, setSelectedSites] = useState(["linkedin", "indeed", "glassdoor", "wellfound"]);

  const [searching, setSearching] = useState(false);
  const [discoveredJobs, setDiscoveredJobs] = useState([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [tailoringJobId, setTailoringJobId] = useState(null);

  // The 5 Tracks
  const tracks = [
    { id: "software", label: "Software (SDE, Backend, Full Stack, DevOps)", icon: <Code2 size={16} color="var(--primary)" />, countLabel: "SDE" },
    { id: "data", label: "Data (Data Science, ML, AI, Analytics)", icon: <Database size={16} color="var(--accent-indigo-text)" />, countLabel: "Data" },
    { id: "consult", label: "Consult (Management, Strategy, Business Analyst)", icon: <Briefcase size={16} color="var(--accent-rose-text)" />, countLabel: "Consult" },
    { id: "finance", label: "Finance (Quantitative Analyst, Risk, Fintech)", icon: <TrendingUp size={16} color="var(--accent-cyan-text)" />, countLabel: "Finance" },
    { id: "core", label: "Core (Robotics, Embedded, Hardware, Mechanical)", icon: <Cpu size={16} color="var(--accent-emerald-text)" />, countLabel: "Core" },
  ];

  const portalsList = [
    { id: "linkedin", label: "LinkedIn", color: "#0077b5" },
    { id: "wellfound", label: "Wellfound (AngelList)", color: "#e11d48" },
    { id: "indeed", label: "Indeed", color: "#2563eb" },
    { id: "glassdoor", label: "Glassdoor", color: "#10b981" },
  ];

  const toggleSite = (siteId) => {
    if (selectedSites.includes(siteId)) {
      if (selectedSites.length > 1) {
        setSelectedSites(selectedSites.filter((s) => s !== siteId));
      }
    } else {
      setSelectedSites([...selectedSites, siteId]);
    }
  };

  // Fetch jobs for track
  const executeSearch = async (trackToSearch = selectedTrack) => {
    setSearching(true);
    setStatusMessage(`Searching portals for [${trackToSearch.toUpperCase()}] openings...`);

    try {
      const payload = {
        category: trackToSearch,
        query: trackToSearch,
        location: location,
        results_wanted: parseInt(resultsCount),
        is_remote: isRemote,
        sites: selectedSites,
        profile_id: profile?.id,
      };

      const res = await api.searchJobPortals(payload);
      const jobsList = res.jobs || [];
      setDiscoveredJobs(jobsList);
      setStatusMessage(`✓ Loaded ${jobsList.length} current job openings for [${trackToSearch.toUpperCase()}] track.`);
    } catch (err) {
      setStatusMessage(`Search notice: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  // Trigger search on mount and when selectedTrack changes
  useEffect(() => {
    executeSearch(selectedTrack);
  }, [selectedTrack]);

  const handleTrackChange = (newTrack) => {
    setSelectedTrack(newTrack);
  };

  const handleFormSubmit = (e) => {
    if (e) e.preventDefault();
    executeSearch(selectedTrack);
  };

  const handleTailorAndApply = async (job) => {
    setTailoringJobId(job.id);
    try {
      const res = await api.tailorForJob(job.id, profile?.id);
      if (res.application_id) {
        const fullApp = await api.getApplication(res.application_id);
        if (onOpenReviewModal) {
          onOpenReviewModal(fullApp);
        }
      }
    } catch (err) {
      alert(`Tailoring error: ${err.message}`);
    } finally {
      setTailoringJobId(null);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Search Header Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-subtle) 100%)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "16px",
          padding: "24px 28px",
          boxShadow: "var(--card-shadow)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
          <span
            style={{
              background: "var(--primary-subtle)",
              color: "var(--primary-text)",
              border: "1px solid var(--border-active)",
              padding: "2px 8px",
              borderRadius: "6px",
              fontSize: "11px",
              fontWeight: "700",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            Autonomous Discovery Engine
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>• Multi-Portal Search</span>
        </div>
        <h2 style={{ fontSize: "22px", fontWeight: "800", color: "var(--text-primary)" }}>
          Multi-Portal Job Discovery & CV Project Matcher
        </h2>
        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Select any of the 5 tracks (Software, Data, Consult, Finance, Core) to view all current job openings from LinkedIn, Wellfound, Indeed, and Glassdoor scored against your Master CV.
        </p>

        {/* 5 Track Shortcut Pills */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "16px" }}>
          {tracks.map((t) => {
            const isSelected = selectedTrack === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => handleTrackChange(t.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "7px",
                  padding: "7px 14px",
                  borderRadius: "8px",
                  border: isSelected ? "1px solid var(--border-active)" : "1px solid var(--border-subtle)",
                  background: isSelected ? "var(--primary-subtle)" : "var(--bg-card-subtle)",
                  color: isSelected ? "var(--primary-text)" : "var(--text-secondary)",
                  fontSize: "12.5px",
                  fontWeight: isSelected ? "700" : "500",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                {t.icon}
                <span>{t.label.split(" (")[0]}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Search Filter Controls Card */}
      <div className="card" style={{ padding: "22px" }}>
        <form onSubmit={handleFormSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>
            
            {/* 5-Track Dropdown */}
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "var(--primary-text)", marginBottom: "6px" }}>
                Target Job Profile (5 Tracks)
              </label>
              <select
                className="input"
                style={{
                  fontWeight: "700",
                  color: "var(--text-primary)",
                  background: "var(--bg-input)",
                  border: "1px solid var(--border-subtle)",
                  fontSize: "13.5px",
                }}
                value={selectedTrack}
                onChange={(e) => handleTrackChange(e.target.value)}
              >
                <option value="software">💻 Software (SDE, Backend, Full Stack, DevOps)</option>
                <option value="data">🧠 Data (Data Science, ML, AI, Analytics)</option>
                <option value="consult">💼 Consult (Management, Strategy, Business Analyst)</option>
                <option value="finance">📈 Finance (Quantitative Analyst, Risk, Fintech)</option>
                <option value="core">🦾 Core (Robotics, Embedded, Hardware, Mechanical)</option>
              </select>
            </div>

            {/* Location Input */}
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Location / City
              </label>
              <input
                type="text"
                className="input"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="India, Bangalore, Remote..."
                style={{ background: "var(--bg-input)", color: "var(--text-primary)", border: "1px solid var(--border-subtle)" }}
              />
            </div>

            {/* Results Count */}
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Max Results to Display
              </label>
              <select
                className="input"
                value={resultsCount}
                onChange={(e) => setResultsCount(e.target.value)}
                style={{ background: "var(--bg-input)", color: "var(--text-primary)", border: "1px solid var(--border-subtle)" }}
              >
                <option value={10}>10 Opportunities</option>
                <option value={15}>15 Opportunities</option>
                <option value={25}>25 Opportunities</option>
                <option value={50}>50 Opportunities (All)</option>
              </select>
            </div>
          </div>

          {/* Portals Selectors & Remote Toggle */}
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "12px", paddingTop: "8px", borderTop: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
              <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600" }}>Portals:</span>
              {portalsList.map((portal) => {
                const isChecked = selectedSites.includes(portal.id);
                return (
                  <button
                    key={portal.id}
                    type="button"
                    onClick={() => toggleSite(portal.id)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "4px 10px",
                      borderRadius: "6px",
                      border: isChecked ? `1px solid ${portal.color}` : "1px solid var(--border-subtle)",
                      background: isChecked ? "var(--bg-card-hover)" : "var(--bg-card-subtle)",
                      color: isChecked ? "var(--text-primary)" : "var(--text-muted)",
                      fontSize: "11.5px",
                      fontWeight: "600",
                      cursor: "pointer",
                      transition: "all 0.15s ease",
                    }}
                  >
                    <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: isChecked ? portal.color : "var(--text-muted)" }} />
                    {portal.label}
                  </button>
                );
              })}

              <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "var(--text-secondary)", cursor: "pointer", marginLeft: "10px" }}>
                <input
                  type="checkbox"
                  checked={isRemote}
                  onChange={(e) => setIsRemote(e.target.checked)}
                />
                <span>Remote Only</span>
              </label>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={searching}
              style={{ minWidth: "190px", justifyContent: "center" }}
            >
              <Search size={16} className={searching ? "spin" : ""} />
              <span>{searching ? "Searching..." : "Search Portals in Real-Time"}</span>
            </button>
          </div>
        </form>

        {statusMessage && (
          <div
            style={{
              marginTop: "14px",
              padding: "10px 16px",
              borderRadius: "8px",
              background: "var(--bg-card-subtle)",
              border: "1px solid var(--border-subtle)",
              color: statusMessage.includes("✓") ? "var(--accent-emerald-text)" : "var(--primary-text)",
              fontSize: "12.5px",
              fontWeight: "600",
            }}
          >
            {statusMessage}
          </div>
        )}
      </div>

      {/* Discovered Opportunities Grid */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <div>
            <h3 style={{ fontSize: "17px", fontWeight: "800", color: "var(--text-primary)" }}>
              {selectedTrack.toUpperCase()} Openings ({discoveredJobs.length})
            </h3>
            <p style={{ fontSize: "12.5px", color: "var(--text-secondary)" }}>
              All currently available roles ranked by Master CV project similarity.
            </p>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {discoveredJobs.length === 0 ? (
            <div className="card" style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
              {searching ? "Searching portals and loading openings..." : "No job openings found. Click 'Search Portals in Real-Time' to refresh."}
            </div>
          ) : (
            discoveredJobs.map((job, idx) => {
              const score = job.match_score || 88.0;
              const isTailoring = tailoringJobId === job.id;

              return (
                <div
                  key={idx}
                  className="card"
                  style={{
                    padding: "20px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "18px",
                    flexWrap: "wrap",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div style={{ flex: 1, minWidth: "280px" }}>
                    {/* Header line: Title, Portal, Match badge */}
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px", flexWrap: "wrap" }}>
                      <span style={{ fontSize: "15.5px", fontWeight: "800", color: "var(--text-primary)" }}>
                        {job.title}
                      </span>

                      {/* Match Score Badge */}
                      <span
                        className={score >= 90 ? "badge badge-success" : "badge badge-primary"}
                        style={{
                          fontSize: "11px",
                          fontWeight: "800",
                          padding: "2px 8px",
                          borderRadius: "12px",
                        }}
                      >
                        {score.toFixed(0)}% Match
                      </span>

                      {/* Portal Badge */}
                      <span
                        style={{
                          background: "var(--bg-card-subtle)",
                          color: "var(--text-secondary)",
                          border: "1px solid var(--border-subtle)",
                          padding: "2px 8px",
                          borderRadius: "6px",
                          fontSize: "11px",
                          fontWeight: "600",
                          textTransform: "capitalize",
                        }}
                      >
                        {job.site || "LinkedIn"}
                      </span>
                    </div>

                    {/* Company, Location & Compensation */}
                    <div style={{ display: "flex", gap: "16px", alignItems: "center", fontSize: "13px", color: "var(--text-secondary)", marginBottom: "10px", flexWrap: "wrap" }}>
                      <span style={{ fontWeight: "700", color: "var(--text-primary)" }}>{job.company}</span>
                      <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                        <MapPin size={14} color="var(--text-muted)" /> {job.location || "Remote"}
                      </span>
                      <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--accent-cyan-text)", fontWeight: "700" }}>
                        <DollarSign size={14} /> {job.display_salary || job.salary_text || "Competitive"}
                      </span>
                    </div>

                    {/* Best Matching Project Citation */}
                    {job.best_matching_project && job.best_matching_project !== "N/A" && (
                      <div
                        style={{
                          background: "var(--bg-card-subtle)",
                          border: "1px solid var(--border-subtle)",
                          borderRadius: "8px",
                          padding: "8px 12px",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "8px",
                          marginBottom: "10px",
                        }}
                      >
                        <Sparkles size={14} color="var(--primary)" />
                        <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                          <b style={{ color: "var(--primary-text)" }}>Top Project Match:</b> {job.best_matching_project}
                        </span>
                      </div>
                    )}

                    {/* Matched Keywords Tags */}
                    {job.matched_keywords && job.matched_keywords.length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                        {job.matched_keywords.map((kw, kwIdx) => (
                          <span
                            key={kwIdx}
                            style={{
                              background: "var(--primary-subtle)",
                              color: "var(--primary-text)",
                              border: "1px solid var(--border-subtle)",
                              padding: "2px 6px",
                              borderRadius: "4px",
                              fontSize: "10.5px",
                              fontWeight: "600",
                            }}
                          >
                            ✓ {kw}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", minWidth: "170px" }}>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleTailorAndApply(job)}
                      disabled={isTailoring}
                      style={{ fontSize: "12.5px", justifyContent: "center", padding: "10px 14px" }}
                    >
                      <Sparkles size={14} className={isTailoring ? "spin" : ""} />
                      <span>{isTailoring ? "Tailoring ATS CV..." : "⚡ Tailor 1-Page ATS CV"}</span>
                    </button>

                    {job.url && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary"
                        style={{ fontSize: "11.5px", justifyContent: "center", padding: "6px 10px" }}
                      >
                        <span>View on {job.site || "Portal"}</span>
                        <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
