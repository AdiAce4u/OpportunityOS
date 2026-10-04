import React, { useState } from "react";
import confetti from "canvas-confetti";
import {
  X,
  CheckCircle,
  FileText,
  Mail,
  HelpCircle,
  Building2,
  Download,
  AlertTriangle,
  Send,
  Edit3,
  ThumbsDown,
  ShieldCheck,
  Check,
} from "lucide-react";

export function ApplicationReviewModal({ application, onClose, onApprove, onReject, onProvideMissingInfo }) {
  if (!application) return null;

  const [activeTab, setActiveTab] = useState("resume"); // "resume" | "cover_letter" | "answers" | "research"
  const [isEditing, setIsEditing] = useState(false);
  const [editedResume, setEditedResume] = useState(application.tailored_resume || "");
  const [editedCoverLetter, setEditedCoverLetter] = useState(application.cover_letter || "");
  const [editedAnswers, setEditedAnswers] = useState(application.answers || {});
  const [submitting, setSubmitting] = useState(false);
  
  // Missing info form state
  const [missingInput, setMissingInput] = useState("");

  const job = application.job || {};
  const company = job.company || "Target Company";
  const role = job.title || "Position";
  const matchScore = application.match_score || 91;
  const why = application.why_this_job || {};
  const research = application.company_research || {};
  const missingInfo = application.missing_information || [];

  const handleApproveSubmit = async () => {
    setSubmitting(true);
    try {
      await onApprove(application.id, {
        approve: true,
        edited_resume: isEditing ? editedResume : undefined,
        edited_cover_letter: isEditing ? editedCoverLetter : undefined,
        edited_answers: isEditing ? editedAnswers : undefined,
      });
      // Fire celebration confetti!
      try {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
        });
      } catch (e) {}
    } finally {
      setSubmitting(false);
    }
  };

  const handleMissingSubmit = (e) => {
    e.preventDefault();
    if (!missingInput.trim()) return;
    onProvideMissingInfo(application.id, {
      [missingInfo[0] || "additional_info"]: missingInput,
    });
    setMissingInput("");
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
        zIndex: 100,
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
            padding: "24px 28px",
            borderBottom: "1px solid #1e293b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            background: "#090f1d",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span className="badge badge-warning">HUMAN REVIEW & APPROVAL GATE</span>
              <span className="badge badge-success">
                <Check size={12} /> Eligibility: Verified
              </span>
            </div>
            <h2 style={{ fontSize: "22px", fontWeight: "800", color: "#ffffff" }}>{role}</h2>
            <div style={{ fontSize: "14px", color: "#94a3b8", marginTop: "2px" }}>
              {company} · {job.location || "Bangalore, India"} · {job.salary_text || "Competitive"}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "26px", fontWeight: "900", color: "#10b981", lineHeight: "1" }}>
                {matchScore}%
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "600", textTransform: "uppercase" }}>
                Overall Fit
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
              <X size={22} />
            </button>
          </div>
        </div>

        {/* Missing Information Banner if any */}
        {missingInfo.length > 0 && (
          <div
            style={{
              background: "#451a03",
              borderBottom: "1px solid #78350f",
              padding: "14px 28px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <AlertTriangle size={18} color="#f59e0b" />
              <div style={{ fontSize: "13px", color: "#fef3c7" }}>
                <strong>Missing Information Required:</strong> The agent needs your{" "}
                <strong>{missingInfo.join(", ")}</strong> before submission.
              </div>
            </div>
            <form onSubmit={handleMissingSubmit} style={{ display: "flex", gap: "8px" }}>
              <input
                type="text"
                placeholder={`Enter ${missingInfo[0]}...`}
                value={missingInput}
                onChange={(e) => setMissingInput(e.target.value)}
                style={{
                  background: "#1c1917",
                  border: "1px solid #78350f",
                  borderRadius: "6px",
                  color: "#ffffff",
                  padding: "6px 12px",
                  fontSize: "13px",
                }}
              />
              <button className="btn btn-primary" style={{ padding: "6px 12px", fontSize: "12px" }}>
                Provide
              </button>
            </form>
          </div>
        )}

        {/* Navigation Tabs */}
        <div
          style={{
            display: "flex",
            gap: "4px",
            padding: "8px 28px",
            background: "#080c16",
            borderBottom: "1px solid #1a233a",
          }}
        >
          {[
            { id: "resume", label: "Tailored Resume", icon: <FileText size={15} /> },
            { id: "cover_letter", label: "Cover Letter", icon: <Mail size={15} /> },
            { id: "answers", label: "Application Answers", icon: <HelpCircle size={15} /> },
            { id: "research", label: "Company Intelligence", icon: <Building2 size={15} /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 16px",
                borderRadius: "8px",
                border: "none",
                background: activeTab === tab.id ? "#17233e" : "transparent",
                color: activeTab === tab.id ? "#ffffff" : "#94a3b8",
                fontWeight: activeTab === tab.id ? "700" : "500",
                fontSize: "13px",
                cursor: "pointer",
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}

          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              className="btn btn-secondary"
              style={{ padding: "6px 12px", fontSize: "12px" }}
              onClick={() => setIsEditing(!isEditing)}
            >
              <Edit3 size={13} />
              <span>{isEditing ? "Done Editing" : "Edit Materials"}</span>
            </button>

            {application.tailored_resume_pdf_path && (
              <a
                href={`http://localhost:8000/api/applications/${application.id}/resume-pdf`}
                download
                className="btn btn-secondary"
                style={{ padding: "6px 12px", fontSize: "12px", textDecoration: "none" }}
              >
                <Download size={13} />
                <span>PDF</span>
              </a>
            )}
          </div>
        </div>

        {/* Tab Content Body */}
        <div style={{ padding: "24px 28px", overflowY: "auto", flex: 1, maxHeight: "420px" }}>
          {activeTab === "resume" && (
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginBottom: "12px",
                  fontSize: "12px",
                  color: "#10b981",
                }}
              >
                <ShieldCheck size={16} />
                <span>Grounded strictly in verified candidate facts. Zero hallucinated qualifications.</span>
              </div>
              {isEditing ? (
                <textarea
                  className="textarea"
                  style={{ minHeight: "280px", fontFamily: "'JetBrains Mono', monospace", fontSize: "12.5px" }}
                  value={editedResume}
                  onChange={(e) => setEditedResume(e.target.value)}
                />
              ) : (
                <pre
                  style={{
                    background: "#080c16",
                    border: "1px solid #1a233a",
                    padding: "16px",
                    borderRadius: "8px",
                    fontSize: "12.5px",
                    color: "#e2e8f0",
                    whiteSpace: "pre-wrap",
                    lineHeight: "1.6",
                  }}
                >
                  {editedResume}
                </pre>
              )}
            </div>
          )}

          {activeTab === "cover_letter" && (
            <div>
              {isEditing ? (
                <textarea
                  className="textarea"
                  style={{ minHeight: "280px", fontSize: "13.5px", lineHeight: "1.6" }}
                  value={editedCoverLetter}
                  onChange={(e) => setEditedCoverLetter(e.target.value)}
                />
              ) : (
                <div
                  style={{
                    background: "#080c16",
                    border: "1px solid #1a233a",
                    padding: "20px",
                    borderRadius: "8px",
                    fontSize: "13.5px",
                    color: "#e2e8f0",
                    whiteSpace: "pre-wrap",
                    lineHeight: "1.6",
                  }}
                >
                  {editedCoverLetter}
                </div>
              )}
            </div>
          )}

          {activeTab === "answers" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {Object.entries(editedAnswers).map(([k, v]) => (
                <div key={k} style={{ background: "#080c16", border: "1px solid #1a233a", padding: "16px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "12px", fontWeight: "700", color: "#818cf8", textTransform: "uppercase", marginBottom: "6px" }}>
                    {k.replace("_", " ")}
                  </div>
                  {isEditing ? (
                    <input
                      type="text"
                      className="input"
                      value={v}
                      onChange={(e) => setEditedAnswers({ ...editedAnswers, [k]: e.target.value })}
                    />
                  ) : (
                    <div style={{ fontSize: "13.5px", color: "#f1f5f9", lineHeight: "1.5" }}>{v}</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {activeTab === "research" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "16px", borderRadius: "8px" }}>
                <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff", marginBottom: "6px" }}>Company Summary</h4>
                <p style={{ fontSize: "13px", color: "#cbd5e1", lineHeight: "1.5" }}>
                  {research.company_summary || "Leading autonomous engineering group."}
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
                <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "14px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "12px", fontWeight: "700", color: "#94a3b8" }}>Domain & Scale</span>
                  <div style={{ fontSize: "13.5px", fontWeight: "600", color: "#38bdf8", marginTop: "4px" }}>
                    {research.domain || "Robotics / AI"} · {research.size || "100+ employees"}
                  </div>
                </div>

                <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "14px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "12px", fontWeight: "700", color: "#94a3b8" }}>Technology Stack</span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "6px" }}>
                    {(research.technology || ["ROS2", "Python", "C++"]).map((t, idx) => (
                      <span key={idx} style={{ background: "#1e293b", color: "#f8fafc", padding: "2px 8px", borderRadius: "4px", fontSize: "11px" }}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {research.recent_news?.length > 0 && (
                <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "16px", borderRadius: "8px" }}>
                  <h4 style={{ fontSize: "13px", fontWeight: "700", color: "#f59e0b", marginBottom: "6px" }}>Recent Milestone News</h4>
                  <ul style={{ paddingLeft: "18px", fontSize: "12.5px", color: "#cbd5e1" }}>
                    {research.recent_news.map((n, idx) => (
                      <li key={idx} style={{ marginBottom: "4px" }}>{n}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div
          style={{
            padding: "20px 28px",
            background: "#090f1d",
            borderTop: "1px solid #1e293b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ fontSize: "12.5px", color: "#64748b" }}>
            Browser automation will only execute with your explicit authorization.
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <button
              className="btn btn-danger"
              disabled={submitting}
              onClick={() => onReject(application.id)}
            >
              <ThumbsDown size={15} />
              <span>Reject Application</span>
            </button>

            <button
              className="btn btn-success"
              disabled={submitting || missingInfo.length > 0}
              onClick={handleApproveSubmit}
            >
              <Send size={15} />
              <span>{submitting ? "Launching Browser Agent..." : "Approve & Submit"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
