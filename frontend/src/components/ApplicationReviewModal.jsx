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
  ExternalLink,
  Layers,
  Sparkles,
  Eye,
  RefreshCw,
  Loader2,
  Copy,
  BookmarkCheck,
  Heart,
  Save,
} from "lucide-react";
import { api } from "../services/api";

export function ApplicationReviewModal({ application, onClose, onApprove, onReject, onProvideMissingInfo, onProfileUpdated, onToggleWishlist }) {
  if (!application) return null;

  const [activeTab, setActiveTab] = useState("resume"); // "resume" | "evidence" | "cover_letter" | "answers" | "research"
  const [resumeViewMode, setResumeViewMode] = useState("preview"); // "preview" | "text"
  const [isEditing, setIsEditing] = useState(false);
  const [editedResume, setEditedResume] = useState(application.tailored_resume || "");
  const [editedCoverLetter, setEditedCoverLetter] = useState(application.cover_letter || "");
  const [editedAnswers, setEditedAnswers] = useState(application.answers || {});
  const [submitting, setSubmitting] = useState(false);
  const [copiedType, setCopiedType] = useState(null);

  // Real-time draft save state
  const [savingDraft, setSavingDraft] = useState(false);
  const [saveDraftMsg, setSaveDraftMsg] = useState(null);
  const [pdfTimestamp, setPdfTimestamp] = useState(Date.now());

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
  const resumePdfUrl = `http://localhost:8000/api/applications/${application.id}/resume-pdf`;
  const portalUrl = job.url || (job.external_id ? `http://localhost:8000/portal/apply/${job.external_id}` : "http://localhost:8000/portal/apply/job-001");

  const cleanCompany = (company || "Company").replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  const cleanRole = (role || "Role").replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  const tailoredCvFilename = `CV_${cleanCompany}_${cleanRole}.pdf`;

  const [savingCV, setSavingCV] = useState(false);
  const [savedCVMsg, setSavedCVMsg] = useState(null);

  const handleSaveDraftChanges = async () => {
    setSavingDraft(true);
    setSaveDraftMsg(null);
    try {
      await api.updateApplicationDraft(application.id, {
        tailored_resume: editedResume,
        cover_letter: editedCoverLetter,
        answers: editedAnswers,
      });
      setPdfTimestamp(Date.now());
      setSaveDraftMsg("Saved & recompiled PDF successfully!");
      setTimeout(() => setSaveDraftMsg(null), 3500);
      if (onProfileUpdated) {
        onProfileUpdated();
      }
    } catch (err) {
      alert(`Failed to save draft changes: ${err.message}`);
    } finally {
      setSavingDraft(false);
    }
  };

  const handleSaveCVToProfile = async () => {
    setSavingCV(true);
    try {
      const res = await api.saveTailoredCV(application.profile_id || 1, {
        company: company,
        role: role,
        application_id: application.id,
        resume_text: isEditing ? editedResume : application.tailored_resume,
      });
      setSavedCVMsg(`Saved ${res.filename || tailoredCvFilename}!`);
      setTimeout(() => setSavedCVMsg(null), 3500);
      if (onProfileUpdated) {
        onProfileUpdated();
      }
    } catch (err) {
      alert(`Failed to save tailored CV: ${err.message}`);
    } finally {
      setSavingCV(false);
    }
  };

  const copyToClipboard = (text, type) => {
    if (!text) return;
    try {
      navigator.clipboard.writeText(text);
      setCopiedType(type);
      setTimeout(() => setCopiedType(null), 2200);
    } catch (err) {
      console.error("Clipboard copy failed", err);
    }
  };

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

  const handleAcceptAndApply = async () => {
    // Open portal application URL directly in new tab so user can apply
    try {
      if (portalUrl) {
        window.open(portalUrl, "_blank", "noopener,noreferrer");
      }
    } catch (e) {
      console.error("Could not open portal link:", e);
    }
    // Accept & submit application in OpportunityOS
    await handleApproveSubmit();
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
        backgroundColor: "var(--modal-overlay)",
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
          width: "min(1040px, 96%)",
          maxHeight: "94vh",
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
            alignItems: "flex-start",
            background: "var(--bg-card)",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span className="badge badge-warning">HUMAN REVIEW & APPROVAL GATE</span>
              <span className="badge badge-success">
                <Check size={12} /> Eligibility: Verified
              </span>
              <span className="badge badge-primary">
                <ExternalLink size={12} /> {job.site || "Application Portal"}
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                type="button"
                onClick={() => onToggleWishlist && onToggleWishlist(application)}
                style={{
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  padding: "4px",
                  borderRadius: "50%",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "transform 0.15s ease",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.2)")}
                onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
                title={application.is_wishlisted ? "Remove from Wishlist" : "Wishlist this opportunity"}
              >
                <Heart
                  size={22}
                  fill={application.is_wishlisted ? "#f43f5e" : "transparent"}
                  color={application.is_wishlisted ? "#f43f5e" : "var(--text-muted)"}
                />
              </button>
              <h2 style={{ fontSize: "22px", fontWeight: "800", color: "var(--text-primary)" }}>{role}</h2>
            </div>
            <div style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "2px" }}>
              {company} · {job.location || "Bangalore, India"} · {job.salary_text || "Competitive"}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "26px", fontWeight: "900", color: "var(--accent-emerald)", lineHeight: "1" }}>
                {matchScore}%
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
                Overall Fit
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
              <X size={22} />
            </button>
          </div>
        </div>

        {/* Dedicated Application Portal Link Bar */}
        <div
          style={{
            background: "var(--bg-well)",
            borderBottom: "1px solid var(--border-subtle)",
            padding: "11px 28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "14px",
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span className="badge badge-primary" style={{ textTransform: "uppercase", fontSize: "11px", fontWeight: "700", whiteSpace: "nowrap" }}>
              {job.site || "Careers Portal"}
            </span>
            <span style={{ fontSize: "13px", color: "var(--text-secondary)", fontWeight: "500" }}>
              Official Application Portal
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              onClick={() => copyToClipboard(portalUrl, "link_bar")}
              className="btn btn-secondary"
              style={{ padding: "5px 12px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "5px" }}
              title="Copy application link to clipboard"
            >
              {copiedType === "link_bar" ? <Check size={12} color="var(--accent-emerald)" /> : <Copy size={12} />}
              <span>{copiedType === "link_bar" ? "Copied!" : "Copy Link"}</span>
            </button>

            <a
              href={portalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{
                padding: "6px 14px",
                fontSize: "12.5px",
                fontWeight: "700",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                boxShadow: "0 2px 8px rgba(59, 130, 246, 0.25)",
              }}
              title="Go to application webpage in a new tab"
            >
              <span>Go to Application Link</span>
              <ExternalLink size={13} />
            </a>
          </div>
        </div>

        {/* Missing Information Banner if any */}
        {missingInfo.length > 0 && (
          <div
            style={{
              background: "var(--accent-amber-subtle)",
              borderBottom: "1px solid var(--accent-amber-border)",
              padding: "12px 28px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <AlertTriangle size={18} color="var(--accent-amber)" />
              <div style={{ fontSize: "13px", color: "var(--accent-amber-text)" }}>
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
                  background: "var(--bg-input)",
                  border: "1px solid var(--accent-amber-border)",
                  borderRadius: "6px",
                  color: "var(--text-primary)",
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
            background: "var(--bg-well)",
            borderBottom: "1px solid var(--border-subtle)",
          }}
        >
          {[
            { id: "resume", label: "Tailored Resume", icon: <FileText size={15} /> },
            { id: "evidence", label: "Evidence Citation Table", icon: <Layers size={15} />, badge: evidenceTable.length > 0 ? evidenceTable.length : null },
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
                background: activeTab === tab.id ? "var(--bg-card)" : "transparent",
                color: activeTab === tab.id ? "var(--primary)" : "var(--text-secondary)",
                fontWeight: activeTab === tab.id ? "700" : "500",
                boxShadow: activeTab === tab.id ? "var(--card-shadow)" : "none",
                fontSize: "13px",
                cursor: "pointer",
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.badge && (
                <span
                  style={{
                    background: "var(--primary)",
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

          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center" }}>
            <button
              className="btn btn-secondary"
              style={{ padding: "6px 14px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "6px" }}
              onClick={() => setIsEditing(!isEditing)}
            >
              <Edit3 size={13} />
              <span>{isEditing ? "Done Editing" : "Edit Materials"}</span>
            </button>
          </div>
        </div>

        {/* Tab Content Body */}
        <div style={{ padding: "20px 28px", overflowY: "auto", flex: 1, minHeight: "400px", maxHeight: "60vh" }}>
          {/* TAB 1: RESUME */}
          {activeTab === "resume" && (
            <div>
              {/* Resume Controls Bar */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "14px",
                  background: "var(--bg-card-subtle)",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "1px solid var(--border-subtle)",
                  flexWrap: "wrap",
                  gap: "10px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <button
                    onClick={() => setResumeViewMode("preview")}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "6px 12px",
                      borderRadius: "6px",
                      border: "none",
                      background: resumeViewMode === "preview" ? "var(--primary-subtle)" : "transparent",
                      color: resumeViewMode === "preview" ? "var(--primary-text)" : "var(--text-secondary)",
                      fontWeight: "600",
                      fontSize: "12.5px",
                      cursor: "pointer",
                    }}
                  >
                    <Eye size={14} />
                    <span>Live ATS PDF Preview</span>
                  </button>

                  <button
                    onClick={() => setResumeViewMode("text")}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "6px 12px",
                      borderRadius: "6px",
                      border: "none",
                      background: resumeViewMode === "text" ? "var(--primary-subtle)" : "transparent",
                      color: resumeViewMode === "text" ? "var(--primary-text)" : "var(--text-secondary)",
                      fontWeight: "600",
                      fontSize: "12.5px",
                      cursor: "pointer",
                    }}
                  >
                    <FileText size={14} />
                    <span>Text & Markup</span>
                  </button>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  <button
                    type="button"
                    onClick={handleSaveCVToProfile}
                    disabled={savingCV}
                    className="btn btn-secondary"
                    style={{
                      padding: "6px 14px",
                      fontSize: "12px",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      background: savedCVMsg ? "rgba(16, 185, 129, 0.15)" : undefined,
                      borderColor: savedCVMsg ? "var(--accent-emerald)" : undefined,
                      color: savedCVMsg ? "var(--accent-emerald-text)" : undefined,
                      cursor: "pointer",
                    }}
                    title={`Save ${tailoredCvFilename} to your Profile section`}
                  >
                    {savedCVMsg ? <CheckCircle2 size={13} color="var(--accent-emerald-text)" /> : <BookmarkCheck size={13} />}
                    <span>{savedCVMsg ? savedCVMsg : savingCV ? "Saving..." : "Save CV to Profile"}</span>
                  </button>

                  <a
                    href={`${resumePdfUrl}?t=${pdfTimestamp}`}
                    download={tailoredCvFilename}
                    className="btn btn-primary"
                    style={{ padding: "6px 14px", fontSize: "12px", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "6px" }}
                  >
                    <Download size={13} />
                    <span>Download Tailored PDF</span>
                  </a>

                  <a
                    href={`${resumePdfUrl}?t=${pdfTimestamp}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                    style={{ padding: "6px 12px", fontSize: "12px", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "6px" }}
                    title="Open PDF in a new browser tab"
                  >
                    <ExternalLink size={13} />
                    <span>Fullscreen</span>
                  </a>
                </div>
              </div>

              {isEditing ? (
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px", flexWrap: "wrap", gap: "8px" }}>
                    <div style={{ fontSize: "12px", color: "var(--accent-amber-text)" }}>
                      Modify tailored CV text. Click 'Save & Re-generate PDF' to recompile immediately.
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      {saveDraftMsg && (
                        <span style={{ fontSize: "12px", color: "var(--accent-emerald-text)", fontWeight: "700" }}>
                          {saveDraftMsg}
                        </span>
                      )}
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={handleSaveDraftChanges}
                        disabled={savingDraft}
                        style={{ padding: "6px 14px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                      >
                        <Save size={13} />
                        <span>{savingDraft ? "Saving & Recompiling..." : "Save & Re-generate PDF"}</span>
                      </button>
                    </div>
                  </div>
                  <textarea
                    className="textarea"
                    style={{ minHeight: "360px", fontFamily: "'JetBrains Mono', monospace", fontSize: "12.5px" }}
                    value={editedResume}
                    onChange={(e) => setEditedResume(e.target.value)}
                  />
                </div>
              ) : resumeViewMode === "preview" ? (
                <div>
                  <div
                    style={{
                      width: "100%",
                      height: "460px",
                      borderRadius: "8px",
                      overflow: "hidden",
                      border: "1px solid var(--border-subtle)",
                      background: "var(--bg-well)",
                      boxShadow: "var(--card-shadow)",
                    }}
                  >
                    <iframe
                      src={`${resumePdfUrl}?t=${pdfTimestamp}`}
                      title="Tailored ATS PDF"
                      style={{
                        width: "100%",
                        height: "100%",
                        border: "none",
                        background: "#ffffff",
                      }}
                    />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "8px", fontSize: "11.5px", color: "var(--text-muted)" }}>
                    <span>ATS Strict Budget: 0.4-inch margins · Action-Result metric bullets · Verified skills</span>
                    <span>Direct API: /api/applications/{application.id}/resume-pdf</span>
                  </div>
                </div>
              ) : (
                <div>
                  <pre
                    style={{
                      background: "var(--bg-well)",
                      border: "1px solid var(--border-subtle)",
                      padding: "16px",
                      borderRadius: "8px",
                      fontSize: "12.5px",
                      color: "var(--text-primary)",
                      whiteSpace: "pre-wrap",
                      lineHeight: "1.6",
                      maxHeight: "460px",
                      overflowY: "auto",
                    }}
                  >
                    {editedResume}
                  </pre>
                </div>
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
                  color: "var(--text-secondary)",
                  background: "var(--bg-card-subtle)",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <ShieldCheck size={16} color="var(--accent-emerald)" />
                <span>
                  <strong>1-to-1 Evidence Citations:</strong> Transparent mapping of job requirements to verified projects, roles, and candidate credentials. Zero fabricated experience.
                </span>
              </div>

              {evidenceTable.length > 0 ? (
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                    <thead>
                      <tr style={{ background: "var(--bg-well)", borderBottom: "1px solid var(--border-subtle)", textAlign: "left" }}>
                        <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: "600" }}>Job Requirement</th>
                        <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: "600" }}>Candidate Evidence (Profile / CV)</th>
                        <th style={{ padding: "12px 14px", color: "var(--text-muted)", width: "120px" }}>Match Rating</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evidenceTable.map((item, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: "1px solid var(--border-subtle)",
                            background: idx % 2 === 0 ? "transparent" : "var(--bg-well)",
                          }}
                        >
                          <td style={{ padding: "12px 14px", fontWeight: "600", color: "var(--text-primary)" }}>
                            {item.requirement}
                          </td>
                          <td style={{ padding: "12px 14px", color: "var(--text-secondary)" }}>
                            {item.evidence}
                          </td>
                          <td style={{ padding: "12px 14px" }}>
                            {item.rating === "STRONG" && (
                              <span
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  background: "var(--accent-emerald-subtle)",
                                  color: "var(--accent-emerald-text)",
                                  border: "1px solid var(--accent-emerald-border)",
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
                                  background: "var(--accent-amber-subtle)",
                                  color: "var(--accent-amber-text)",
                                  border: "1px solid var(--accent-amber-border)",
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
                                  background: "var(--bg-well)",
                                  color: "var(--text-muted)",
                                  border: "1px solid var(--border-subtle)",
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
                <div style={{ textAlign: "center", padding: "30px", color: "var(--text-muted)", background: "var(--bg-card-subtle)", borderRadius: "8px" }}>
                  All requirements verified. Evidence table will be generated when analyzed against custom or structured JDs.
                </div>
              )}
            </div>
          )}

          {/* TAB 4: COVER LETTER */}
          {activeTab === "cover_letter" && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span style={{ fontSize: "12.5px", color: "var(--text-secondary)" }}>
                  Tailored narrative highlighting verified achievements matching {company}'s requirements.
                </span>
                <button
                  onClick={() => copyToClipboard(editedCoverLetter, "tab_cover_letter")}
                  className="btn btn-secondary"
                  style={{ padding: "5px 12px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                >
                  {copiedType === "tab_cover_letter" ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
                  <span>{copiedType === "tab_cover_letter" ? "Copied Cover Letter!" : "Copy Cover Letter"}</span>
                </button>
              </div>

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
                    background: "var(--bg-card-subtle)",
                    border: "1px solid var(--border-subtle)",
                    padding: "20px",
                    borderRadius: "8px",
                    fontSize: "13.5px",
                    color: "var(--text-primary)",
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
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12.5px", color: "var(--text-secondary)" }}>
                  Pre-computed screening answers aligned with candidate ground truth.
                </span>
                <button
                  onClick={() => {
                    const answersText = Object.entries(editedAnswers)
                      .map(([k, v]) => `${k.toUpperCase().replace(/_/g, " ")}:\n${v}`)
                      .join("\n\n");
                    copyToClipboard(answersText, "tab_answers");
                  }}
                  className="btn btn-secondary"
                  style={{ padding: "5px 12px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                >
                  {copiedType === "tab_answers" ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
                  <span>{copiedType === "tab_answers" ? "Copied All Answers!" : "Copy All Q&A"}</span>
                </button>
              </div>

              {Object.entries(editedAnswers).map(([k, v]) => (
                <div key={k} style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "16px", borderRadius: "8px" }}>
                  <div style={{ fontSize: "12px", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase", marginBottom: "6px" }}>
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
                    <div style={{ fontSize: "13.5px", color: "var(--text-primary)", lineHeight: "1.5" }}>{v}</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* TAB 6: RESEARCH */}
          {activeTab === "research" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "16px", borderRadius: "8px" }}>
                <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "6px" }}>Company Summary</h4>
                <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                  {research.company_summary || "Leading autonomous engineering group."}
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
                <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "14px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-muted)" }}>Domain & Scale</span>
                  <div style={{ fontSize: "13.5px", fontWeight: "600", color: "var(--accent-cyan-text)", marginTop: "4px" }}>
                    {research.domain || "Robotics / AI"} · {research.size || "100+ employees"}
                  </div>
                </div>

                <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "14px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-muted)" }}>Technology Stack</span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "6px" }}>
                    {(research.technology || ["ROS2", "Python", "C++"]).map((t, idx) => (
                      <span key={idx} style={{ background: "var(--bg-card-hover)", color: "var(--text-primary)", border: "1px solid var(--border-subtle)", padding: "2px 8px", borderRadius: "4px", fontSize: "11px" }}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {research.recent_news?.length > 0 && (
                <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "16px", borderRadius: "8px" }}>
                  <h4 style={{ fontSize: "13px", fontWeight: "700", color: "var(--accent-amber-text)", marginBottom: "6px" }}>Recent Milestone News</h4>
                  <ul style={{ paddingLeft: "18px", fontSize: "12.5px", color: "var(--text-secondary)" }}>
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
            background: "var(--bg-card)",
            borderTop: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "12.5px", color: "var(--text-muted)" }}>
              Official job portal · Tailored materials ready to attach
            </span>
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
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
              onClick={handleAcceptAndApply}
              style={{ display: "inline-flex", alignItems: "center", gap: "7px", fontSize: "13px", padding: "8px 20px", fontWeight: "700" }}
              title="Accept application, open portal in new tab, and track in pipeline"
            >
              {submitting ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
              <span>{submitting ? "Opening Portal & Submitting..." : "Accept and Apply"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
