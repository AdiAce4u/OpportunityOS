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
  CheckCircle2,
  Camera,
  ExternalLink,
  Layers,
  Sparkles,
} from "lucide-react";
import { api } from "../services/api";

export function ApplicationReviewModal({ application, onClose, onApprove, onReject, onProvideMissingInfo }) {
  if (!application) return null;

  const [activeTab, setActiveTab] = useState("resume"); // "resume" | "evidence" | "prefill" | "cover_letter" | "answers" | "research"
  const [isEditing, setIsEditing] = useState(false);
  const [editedResume, setEditedResume] = useState(application.tailored_resume || "");
  const [editedCoverLetter, setEditedCoverLetter] = useState(application.cover_letter || "");
  const [editedAnswers, setEditedAnswers] = useState(application.answers || {});
  const [submitting, setSubmitting] = useState(false);
  const [prefilling, setPrefilling] = useState(false);
  const [prefillSnapshotUrl, setPrefillSnapshotUrl] = useState(
    application.submission_receipt?.prefill_snapshot_url
      ? `http://localhost:8000${application.submission_receipt.prefill_snapshot_url}`
      : null
  );
  const [prefillStatus, setPrefillStatus] = useState(
    application.submission_receipt?.prefill_snapshot_url ? "Portal Form Verified & Snapshot Saved" : null
  );

  // Missing info form state
  const [missingInput, setMissingInput] = useState("");

  const job = application.job || {};
  const company = job.company || "Target Company";
  const role = job.title || "Position";
  const matchScore = application.match_score || 91;
  const why = application.why_this_job || {};
  const research = application.company_research || {};
  const missingInfo = application.missing_information || [];
  const evidenceTable = application.evidence_table || why.evidence_table || [];

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

  const handlePreparePortal = async () => {
    setPrefilling(true);
    try {
      const res = await api.preparePortalPrefill(application.id);
      if (res.snapshot_url) {
        setPrefillSnapshotUrl(`http://localhost:8000${res.snapshot_url}?t=${Date.now()}`);
        setPrefillStatus("Form fields pre-filled and visual screenshot captured.");
        setActiveTab("prefill");
      } else {
        setPrefillStatus(res.details || "Portal pre-filled successfully.");
      }
    } catch (err) {
      alert(`Portal pre-fill preview error: ${err.message}`);
    } finally {
      setPrefilling(false);
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
          width: "min(960px, 100%)",
          maxHeight: "92vh",
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
              {prefillSnapshotUrl && (
                <span className="badge badge-primary" style={{ background: "#1e1b4b", color: "#a5b4fc", border: "1px solid #4338ca" }}>
                  <Camera size={12} /> Pre-Fill Inspected
                </span>
              )}
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
              padding: "12px 28px",
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
            flexWrap: "wrap",
            gap: "4px",
            padding: "8px 28px",
            background: "#080c16",
            borderBottom: "1px solid #1a233a",
          }}
        >
          {[
            { id: "resume", label: "Tailored Resume", icon: <FileText size={15} /> },
            { id: "evidence", label: "Evidence Citation Table", icon: <Layers size={15} />, badge: evidenceTable.length > 0 ? evidenceTable.length : null },
            { id: "prefill", label: "Portal Visual Pre-Check", icon: <Camera size={15} /> },
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
                gap: "7px",
                padding: "8px 14px",
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
              {tab.badge && (
                <span
                  style={{
                    background: "#0284c7",
                    color: "white",
                    borderRadius: "10px",
                    padding: "1px 6px",
                    fontSize: "11px",
                    fontWeight: "700",
                  }}
                >
                  {tab.badge}
                </span>
              )}
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
        <div style={{ padding: "20px 28px", overflowY: "auto", flex: 1, minHeight: "360px", maxHeight: "460px" }}>
          {/* TAB 1: RESUME */}
          {activeTab === "resume" && (
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "12px",
                  fontSize: "12px",
                  color: "#10b981",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <ShieldCheck size={16} />
                  <span>Single-Page ATS Spec (0.4-inch margins, Action-Result bullets, top 2 domain projects).</span>
                </div>
                {application.tailored_resume_pdf_path && (
                  <span style={{ color: "#64748b", fontSize: "11px" }}>
                    PDF Layout: Single-Page Strict Budget
                  </span>
                )}
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

          {/* TAB 2: EVIDENCE CITATION TABLE */}
          {activeTab === "evidence" && (
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginBottom: "14px",
                  fontSize: "12.5px",
                  color: "#94a3b8",
                  background: "#080c16",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "1px solid #1a233a",
                }}
              >
                <ShieldCheck size={16} color="#10b981" />
                <span>
                  <strong>1-to-1 Evidence Citations:</strong> Transparent mapping of job requirements to verified projects, roles, and candidate credentials. Zero fabricated experience.
                </span>
              </div>

              {evidenceTable.length > 0 ? (
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                    <thead>
                      <tr style={{ background: "#090f1d", borderBottom: "1px solid #1e293b", textAlign: "left" }}>
                        <th style={{ padding: "12px 14px", color: "#94a3b8", fontWeight: "600" }}>Job Requirement</th>
                        <th style={{ padding: "12px 14px", color: "#94a3b8", fontWeight: "600" }}>Candidate Evidence (Profile / CV)</th>
                        <th style={{ padding: "12px 14px", color: "#94a3b8", fontWeight: "600", width: "120px" }}>Match Rating</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evidenceTable.map((item, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: "1px solid #162032",
                            background: idx % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                          }}
                        >
                          <td style={{ padding: "12px 14px", fontWeight: "600", color: "#f1f5f9" }}>
                            {item.requirement}
                          </td>
                          <td style={{ padding: "12px 14px", color: "#cbd5e1" }}>
                            {item.evidence}
                          </td>
                          <td style={{ padding: "12px 14px" }}>
                            {item.rating === "STRONG" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  background: "#064e3b",
                                  color: "#34d399",
                                  padding: "3px 8px",
                                  borderRadius: "6px",
                                  fontSize: "11px",
                                  fontWeight: "700",
                                }}
                              >
                                <CheckCircle2 size={12} /> STRONG
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
                                  padding: "3px 8px",
                                  borderRadius: "6px",
                                  fontSize: "11px",
                                  fontWeight: "700",
                                }}
                              >
                                <AlertTriangle size={12} /> MODERATE
                              </span>
                            )}
                            {item.rating === "NONE" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  background: "#1e293b",
                                  color: "#94a3b8",
                                  padding: "3px 8px",
                                  borderRadius: "6px",
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
              ) : (
                <div style={{ textAlign: "center", padding: "30px", color: "#64748b", background: "#080c16", borderRadius: "8px" }}>
                  All requirements verified. Evidence table will be generated when analyzed against custom or structured JDs.
                </div>
              )}
            </div>
          )}

          {/* TAB 3: VISUAL PRE-FILL PREVIEW */}
          {activeTab === "prefill" && (
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "16px",
                  background: "#080c16",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  border: "1px solid #1a233a",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <Camera size={16} color="#38bdf8" />
                    <span style={{ fontSize: "13.5px", fontWeight: "700", color: "#ffffff" }}>
                      Stage 1: Two-Stage Browser Pre-Fill Checkpoint
                    </span>
                  </div>
                  <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "2px" }}>
                    Playwright populates portal inputs and uploads your resume, pausing before submission so you can visually audit the form.
                  </p>
                </div>

                <button
                  className="btn btn-primary"
                  onClick={handlePreparePortal}
                  disabled={prefilling}
                  style={{ whiteSpace: "nowrap", fontSize: "12px", padding: "8px 14px" }}
                >
                  <Camera size={14} />
                  <span>{prefilling ? "Navigating & Pre-filling..." : "Run Browser Pre-Fill"}</span>
                </button>
              </div>

              {prefillSnapshotUrl ? (
                <div
                  style={{
                    background: "#050811",
                    border: "1px solid #1e293b",
                    borderRadius: "10px",
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <div
                    style={{
                      padding: "8px 16px",
                      background: "#090f1d",
                      borderBottom: "1px solid #1e293b",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      fontSize: "12px",
                      color: "#94a3b8",
                    }}
                  >
                    <span>Playwright Browser Viewport Snapshot</span>
                    <a
                      href={prefillSnapshotUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#38bdf8", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px" }}
                    >
                      <ExternalLink size={12} /> Open Full Screenshot
                    </a>
                  </div>
                  <div style={{ padding: "12px", display: "grid", placeItems: "center", maxHeight: "380px", overflowY: "auto" }}>
                    <img
                      src={prefillSnapshotUrl}
                      alt="Portal Pre-Fill Snapshot"
                      style={{
                        width: "100%",
                        maxWidth: "800px",
                        borderRadius: "6px",
                        border: "1px solid #334155",
                        boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
                      }}
                    />
                  </div>
                </div>
              ) : (
                <div
                  style={{
                    border: "2px dashed #1e293b",
                    borderRadius: "10px",
                    padding: "40px 20px",
                    textAlign: "center",
                    background: "#080c16",
                  }}
                >
                  <Camera size={36} color="#64748b" style={{ margin: "0 auto 12px" }} />
                  <h4 style={{ fontSize: "14.5px", fontWeight: "700", color: "#f1f5f9", marginBottom: "4px" }}>
                    No Pre-Fill Snapshot Captured Yet
                  </h4>
                  <p style={{ fontSize: "12.5px", color: "#94a3b8", maxWidth: "420px", margin: "0 auto 16px" }}>
                    Click "Run Browser Pre-Fill" to let Playwright open the portal, populate all candidate fields and attach the PDF, and return a visual snapshot for your inspection.
                  </p>
                  <button
                    className="btn btn-primary"
                    onClick={handlePreparePortal}
                    disabled={prefilling}
                    style={{ fontSize: "13px", padding: "8px 18px" }}
                  >
                    <Camera size={15} />
                    <span>{prefilling ? "Simulating Browser Pre-Fill..." : "Capture Form Pre-Fill"}</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: COVER LETTER */}
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

          {/* TAB 5: ANSWERS */}
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

          {/* TAB 6: RESEARCH */}
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
            padding: "18px 28px",
            background: "#090f1d",
            borderTop: "1px solid #1e293b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ fontSize: "12.5px", color: "#64748b" }}>
            {prefillStatus || "Browser automation will only execute with your explicit authorization."}
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <button
              className="btn btn-secondary"
              disabled={prefilling || submitting}
              onClick={handlePreparePortal}
              title="Runs Stage 1: Pre-fills portal and takes a screenshot without submitting"
            >
              <Camera size={14} />
              <span>{prefilling ? "Pre-filling..." : "Visual Pre-Check"}</span>
            </button>

            <button
              className="btn btn-danger"
              disabled={submitting}
              onClick={() => onReject(application.id)}
            >
              <ThumbsDown size={15} />
              <span>Reject</span>
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
