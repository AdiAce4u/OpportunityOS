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
        backgroundColor: "rgba(3, 7, 18, 0.8)",
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
          background: "#0c1324",
          border: "1px solid #1e293b",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.7)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px 28px",
            borderBottom: "1px solid #1e293b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "#090f1d",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "8px",
                background: "#1e1b4b",
                border: "1px solid #4338ca",
                display: "grid",
                placeItems: "center",
                color: "#818cf8",
              }}
            >
              <FileCode size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "800", color: "#ffffff", margin: 0 }}>
                On-Demand Custom JD Analyzer
              </h3>
              <p style={{ fontSize: "12px", color: "#94a3b8", margin: 0 }}>
                Paste any external job description to parse requirements, check eligibility, and generate evidence citations.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "#64748b",
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
                background: "#451a03",
                border: "1px solid #78350f",
                color: "#fef3c7",
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
                  <label style={{ fontSize: "12px", fontWeight: "600", color: "#94a3b8", display: "block", marginBottom: "6px" }}>
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
                  <label style={{ fontSize: "12px", fontWeight: "600", color: "#94a3b8", display: "block", marginBottom: "6px" }}>
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
                <label style={{ fontSize: "12px", fontWeight: "600", color: "#94a3b8", display: "block", marginBottom: "6px" }}>
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
                  background: "#080c16",
                  border: "1px solid #1a233a",
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
                  <h3 style={{ fontSize: "18px", fontWeight: "800", color: "#ffffff", margin: "4px 0" }}>
                    {analysisResult.job?.title}
                  </h3>
                  <div style={{ display: "flex", gap: "16px", fontSize: "12.5px", color: "#94a3b8", marginTop: "4px" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <MapPin size={13} /> {analysisResult.job?.location}
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "#38bdf8" }}>
                      <DollarSign size={13} /> {analysisResult.job?.salary_text}
                    </span>
                  </div>
                </div>

                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "32px", fontWeight: "900", color: "#10b981", lineHeight: "1" }}>
                    {analysisResult.match_score}%
                  </div>
                  <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "700", textTransform: "uppercase" }}>
                    Match Score
                  </div>
                </div>
              </div>

              {/* Fit Reason */}
              <div style={{ background: "#080c16", border: "1px solid #1a233a", borderRadius: "10px", padding: "14px 18px" }}>
                <span style={{ fontSize: "11px", fontWeight: "700", color: "#818cf8", textTransform: "uppercase" }}>
                  Deterministic Assessment
                </span>
                <p style={{ fontSize: "13px", color: "#e2e8f0", margin: "4px 0 0" }}>
                  {analysisResult.reason}
                </p>
                {!analysisResult.is_eligible && (
                  <p style={{ fontSize: "12px", color: "#f87171", margin: "6px 0 0" }}>
                    Eligibility notice: {analysisResult.eligibility_reason}
                  </p>
                )}
              </div>

              {/* 1-to-1 Evidence Citation Table */}
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                  <Layers size={16} color="#818cf8" />
                  <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff", margin: 0 }}>
                    1-to-1 Evidence Citation Table
                  </h4>
                </div>

                <div style={{ overflowX: "auto", border: "1px solid #1a233a", borderRadius: "10px" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12.5px" }}>
                    <thead>
                      <tr style={{ background: "#090f1d", borderBottom: "1px solid #1e293b", textAlign: "left" }}>
                        <th style={{ padding: "10px 14px", color: "#94a3b8", fontWeight: "600" }}>Requirement</th>
                        <th style={{ padding: "10px 14px", color: "#94a3b8", fontWeight: "600" }}>Candidate Evidence</th>
                        <th style={{ padding: "10px 14px", color: "#94a3b8", fontWeight: "600", width: "110px" }}>Rating</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(analysisResult.evidence_table || []).map((item, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: "1px solid #162032",
                            background: idx % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                          }}
                        >
                          <td style={{ padding: "10px 14px", fontWeight: "600", color: "#f1f5f9" }}>
                            {item.requirement}
                          </td>
                          <td style={{ padding: "10px 14px", color: "#cbd5e1" }}>
                            {item.evidence}
                          </td>
                          <td style={{ padding: "10px 14px" }}>
                            {item.rating === "STRONG" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  background: "#064e3b",
                                  color: "#34d399",
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
                                  background: "#451a03",
                                  color: "#fbbf24",
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
                                  background: "#1e293b",
                                  color: "#94a3b8",
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
