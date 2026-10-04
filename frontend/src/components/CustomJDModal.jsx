import React, { useState } from "react";
import {
  X,
  FileCode,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Layers,
  MapPin,
  DollarSign,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { api } from "../services/api";

export function CustomJDModal({ isOpen, onClose, onJobCreated, profileId }) {
  if (!isOpen) return null;

  const [jdText, setJdText] = useState("");
  const [customTitle, setCustomTitle] = useState("");
  const [customCompany, setCustomCompany] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState("");

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!jdText.trim()) {
      setError("Please paste a job description first.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await api.analyzeCustomJD(jdText, customTitle, customCompany, profileId);
      setAnalysisResult(res);
      if (onJobCreated) {
        onJobCreated(res);
      }
    } catch (err) {
      setError(err.message || "Failed to analyze custom job description.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setJdText("");
    setCustomTitle("");
    setCustomCompany("");
    setError("");
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "var(--modal-overlay)",
        backdropFilter: "blur(8px)",
        display: "grid",
        placeItems: "center",
        zIndex: 110,
        padding: "20px",
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: "min(880px, 100%)",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          borderRadius: "16px",
          background: "var(--bg-card)",
          border: "1px solid var(--border-subtle)",
          boxShadow: "var(--card-shadow-hover)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px 28px",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "var(--bg-card)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "8px",
                background: "var(--primary-subtle)",
                border: "1px solid var(--border-active)",
                display: "grid",
                placeItems: "center",
                color: "var(--primary)",
              }}
            >
              <FileCode size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "800", color: "var(--text-primary)", margin: 0 }}>
                On-Demand Custom JD Analyzer
              </h3>
              <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
                Paste any external job description to parse requirements, check eligibility, and generate evidence citations.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
              padding: "6px",
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: "24px 28px", overflowY: "auto", flex: 1 }}>
          {error && (
            <div
              style={{
                background: "var(--accent-amber-subtle)",
                border: "1px solid var(--accent-amber-border)",
                color: "var(--accent-amber-text)",
                padding: "10px 14px",
                borderRadius: "8px",
                fontSize: "13px",
                marginBottom: "16px",
              }}
            >
              {error}
            </div>
          )}

          {!analysisResult ? (
            <form onSubmit={handleAnalyze} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
                <div>
                  <label style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                    Job Title (Optional - auto-inferred if blank)
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g. Autonomous Systems Engineer"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                    Company / Organization (Optional)
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g. Boston Dynamics / Agility Robotics"
                    value={customCompany}
                    onChange={(e) => setCustomCompany(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                  Paste Full Job Description Text *
                </label>
                <textarea
                  className="textarea"
                  style={{ minHeight: "220px", fontSize: "13px", fontFamily: "inherit" }}
                  placeholder="Paste the raw text of the job description here, including requirements, responsibilities, and qualifications..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
                <button type="button" className="btn btn-secondary" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  <Sparkles size={15} />
                  <span>{loading ? "Analyzing Requirements..." : "Analyze JD & Generate Citations"}</span>
                </button>
              </div>
            </form>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              {/* Job Header Card */}
              <div
                style={{
                  background: "var(--bg-card-subtle)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "12px",
                  padding: "18px 20px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <span className="badge badge-primary">{analysisResult.job?.company}</span>
                    <span
                      className={`badge ${analysisResult.is_eligible ? "badge-success" : "badge-danger"}`}
                    >
                      {analysisResult.is_eligible ? "Eligible" : "Eligibility Warning"}
                    </span>
                  </div>
                  <h3 style={{ fontSize: "18px", fontWeight: "800", color: "var(--text-primary)", margin: "4px 0" }}>
                    {analysisResult.job?.title}
                  </h3>
                  <div style={{ display: "flex", gap: "16px", fontSize: "12.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <MapPin size={13} /> {analysisResult.job?.location}
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--accent-cyan-text)" }}>
                      <DollarSign size={13} /> {analysisResult.job?.salary_text}
                    </span>
                  </div>
                </div>

                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "32px", fontWeight: "900", color: "var(--accent-emerald)", lineHeight: "1" }}>
                    {analysisResult.match_score}%
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "700", textTransform: "uppercase" }}>
                    Match Score
                  </div>
                </div>
              </div>

              {/* Fit Reason */}
              <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", borderRadius: "10px", padding: "14px 18px" }}>
                <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase" }}>
                  Deterministic Assessment
                </span>
                <p style={{ fontSize: "13px", color: "var(--text-primary)", margin: "4px 0 0" }}>
                  {analysisResult.reason}
                </p>
                {!analysisResult.is_eligible && (
                  <p style={{ fontSize: "12px", color: "var(--accent-rose-text)", margin: "6px 0 0" }}>
                    Eligibility notice: {analysisResult.eligibility_reason}
                  </p>
                )}
              </div>

              {/* 1-to-1 Evidence Citation Table */}
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                  <Layers size={16} color="var(--primary)" />
                  <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)", margin: 0 }}>
                    1-to-1 Evidence Citation Table
                  </h4>
                </div>

                <div style={{ overflowX: "auto", border: "1px solid var(--border-subtle)", borderRadius: "10px" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12.5px" }}>
                    <thead>
                      <tr style={{ background: "var(--bg-well)", borderBottom: "1px solid var(--border-subtle)", textAlign: "left" }}>
                        <th style={{ padding: "10px 14px", color: "var(--text-muted)", fontWeight: "600" }}>Requirement</th>
                        <th style={{ padding: "10px 14px", color: "var(--text-muted)", fontWeight: "600" }}>Candidate Evidence</th>
                        <th style={{ padding: "10px 14px", color: "var(--text-muted)", fontWeight: "600", width: "110px" }}>Rating</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(analysisResult.evidence_table || []).map((item, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: "1px solid var(--border-subtle)",
                            background: idx % 2 === 0 ? "transparent" : "var(--bg-well)",
                          }}
                        >
                          <td style={{ padding: "10px 14px", fontWeight: "600", color: "var(--text-primary)" }}>
                            {item.requirement}
                          </td>
                          <td style={{ padding: "10px 14px", color: "var(--text-secondary)" }}>
                            {item.evidence}
                          </td>
                          <td style={{ padding: "10px 14px" }}>
                            {item.rating === "STRONG" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  background: "var(--accent-emerald-subtle)",
                                  color: "var(--accent-emerald-text)",
                                  border: "1px solid var(--accent-emerald-border)",
                                  padding: "2px 7px",
                                  borderRadius: "4px",
                                  fontSize: "11px",
                                  fontWeight: "700",
                                }}
                              >
                                <CheckCircle2 size={11} /> STRONG
                              </span>
                            )}
                            {item.rating === "MODERATE" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  background: "var(--accent-amber-subtle)",
                                  color: "var(--accent-amber-text)",
                                  border: "1px solid var(--accent-amber-border)",
                                  padding: "2px 7px",
                                  borderRadius: "4px",
                                  fontSize: "11px",
                                  fontWeight: "700",
                                }}
                              >
                                <AlertTriangle size={11} /> MODERATE
                              </span>
                            )}
                            {item.rating === "NONE" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  background: "var(--bg-well)",
                                  color: "var(--text-muted)",
                                  border: "1px solid var(--border-subtle)",
                                  padding: "2px 7px",
                                  borderRadius: "4px",
                                  fontSize: "11px",
                                  fontWeight: "700",
                                }}
                              >
                                NONE
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "8px" }}>
                <button className="btn btn-secondary" onClick={handleReset}>
                  Analyze Another JD
                </button>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    onClose();
                  }}
                >
                  <span>Close & View Dashboard</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
