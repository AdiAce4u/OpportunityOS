import React, { useState, useEffect } from "react";
import {
  Upload,
  Layers,
  FolderGit2,
  Cpu,
  Database,
  Code2,
  Briefcase,
  DollarSign,
  Compass,
  CheckCircle2,
  FileText,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Edit3,
  Check,
  RefreshCw,
} from "lucide-react";
import { api } from "../services/api";

export function MasterCVVault({ profile, onProfileUpdated, onNavigateToSearch }) {
  const [selectedDomain, setSelectedDomain] = useState("all");
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [activeTab, setActiveTab] = useState("projects"); // "projects" | "raw_cv" | "education"
  const [rescoring, setRescoring] = useState(false);

  const projects = profile?.categorized_projects || profile?.projects || [];

  const domainIcons = {
    sde: <Code2 size={16} color="var(--primary)" />,
    data: <Database size={16} color="var(--accent-indigo-text)" />,
    core: <Cpu size={16} color="var(--accent-emerald-text)" />,
    product: <Compass size={16} color="var(--accent-amber-text)" />,
    consult: <Briefcase size={16} color="var(--accent-rose-text)" />,
    finance: <DollarSign size={16} color="var(--accent-cyan-text)" />,
    general: <Layers size={16} color="var(--text-muted)" />,
  };

  const domainLabels = {
    all: "All Projects",
    sde: "SDE & Systems",
    data: "Data & AI / ML",
    core: "Core Engineering & Robotics",
    product: "Product & Strategy",
    consult: "Consulting & BI",
    finance: "Finance & Quant",
  };

  const domainColors = {
    sde: { bg: "var(--primary-subtle)", text: "var(--primary-text)", border: "var(--border-active)" },
    data: { bg: "var(--accent-indigo-subtle)", text: "var(--accent-indigo-text)", border: "var(--accent-indigo-border)" },
    core: { bg: "var(--accent-emerald-subtle)", text: "var(--accent-emerald-text)", border: "var(--accent-emerald-border)" },
    product: { bg: "var(--accent-amber-subtle)", text: "var(--accent-amber-text)", border: "var(--accent-amber-border)" },
    consult: { bg: "var(--accent-rose-subtle)", text: "var(--accent-rose-text)", border: "var(--accent-rose-border)" },
    finance: { bg: "var(--accent-cyan-subtle)", text: "var(--accent-cyan-text)", border: "var(--accent-cyan-border)" },
    general: { bg: "var(--bg-card-subtle)", text: "var(--text-secondary)", border: "var(--border-subtle)" },
  };

  const filteredProjects =
    selectedDomain === "all"
      ? projects
      : projects.filter((p) => (p.domain || "general").toLowerCase() === selectedDomain);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus({ type: "info", text: "Analyzing and categorizing projects across domains..." });

    try {
      const res = await api.uploadMasterCV(file, profile?.id);
      if (res.profile) {
        onProfileUpdated(res.profile);
      }
      setUploadStatus({
        type: "success",
        text: `✓ Master CV parsed! ${res.total_projects || res.projects?.length || 0} projects extracted & categorized across domains.`,
      });
    } catch (err) {
      setUploadStatus({ type: "error", text: `Upload error: ${err.message}` });
    } finally {
      setUploading(false);
    }
  };

  const handleRescoreAll = async () => {
    setRescoring(true);
    try {
      const res = await api.rescoreJobs(profile?.id);
      setUploadStatus({
        type: "success",
        text: `✓ Rescored ${res.rescored_jobs_count} opportunities against your active Master CV!`,
      });
    } catch (e) {
      alert(`Rescore error: ${e.message}`);
    } finally {
      setRescoring(false);
    }
  };

  // Compute counts per domain
  const counts = { all: projects.length };
  projects.forEach((p) => {
    const d = (p.domain || "general").toLowerCase();
    counts[d] = (counts[d] || 0) + 1;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-subtle) 100%)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "16px",
          padding: "24px 28px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
          boxShadow: "var(--card-shadow)",
        }}
      >
        <div>
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
              Master CV & Domain Vault
            </span>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>• Ground Truth Knowledge Base</span>
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: "800", color: "var(--text-primary)" }}>
            {profile?.name || "Candidate"}’s Comprehensive Multi-Domain Portfolio
          </h2>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Contains all projects across SDE, Data & AI, Core Engineering, Product, and Finance. The agent segregates the best projects for each specific job description.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            className="btn btn-secondary"
            onClick={handleRescoreAll}
            disabled={rescoring}
            style={{ fontSize: "12px" }}
          >
            <RefreshCw size={14} className={rescoring ? "spin" : ""} />
            <span>{rescoring ? "Re-scoring..." : "Re-score Discovered Jobs"}</span>
          </button>

          {onNavigateToSearch && (
            <button
              className="btn btn-primary"
              onClick={onNavigateToSearch}
              style={{ fontSize: "12px" }}
            >
              <Sparkles size={14} />
              <span>Search Matching Roles</span>
            </button>
          )}
        </div>
      </div>

      {/* Upload Master CV Section */}
      <div
        className="card"
        style={{
          padding: "24px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "20px",
          alignItems: "center",
        }}
      >
        <div
          style={{
            border: "2px dashed var(--border-active)",
            borderRadius: "12px",
            padding: "20px",
            textAlign: "center",
            background: "var(--bg-card-subtle)",
          }}
        >
          <Upload size={28} color="var(--primary)" style={{ margin: "0 auto 8px" }} />
          <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>
            Upload Master CV (.md, .txt, .pdf)
          </h4>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: "4px 0 12px" }}>
            Upload your complete CV with all multi-domain projects.
          </p>
          <label className="btn btn-secondary" style={{ cursor: "pointer", display: "inline-flex" }}>
            <span>{uploading ? "Parsing Portfolio..." : "Select Master CV File"}</span>
            <input
              type="file"
              accept=".md,.txt,.pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: "none" }}
            />
          </label>
        </div>

        <div>
          <h4 style={{ fontSize: "13.5px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "8px" }}>
            Master Profile Metrics
          </h4>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px" }}>
            <div style={{ background: "var(--bg-card-subtle)", padding: "12px 14px", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Total Projects Cataloged</div>
              <div style={{ fontSize: "18px", fontWeight: "800", color: "var(--primary-text)", marginTop: "2px" }}>
                {projects.length}
              </div>
            </div>
            <div style={{ background: "var(--bg-card-subtle)", padding: "12px 14px", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Institution & Degree</div>
              <div style={{ fontSize: "12.5px", fontWeight: "700", color: "var(--text-primary)", marginTop: "4px" }}>
                {profile?.college || "IIT Kharagpur"}
              </div>
            </div>
            <div style={{ background: "var(--bg-card-subtle)", padding: "12px 14px", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Skills Extracted</div>
              <div style={{ fontSize: "18px", fontWeight: "800", color: "var(--accent-indigo-text)", marginTop: "2px" }}>
                {profile?.skills?.length || 0}
              </div>
            </div>
            <div style={{ background: "var(--bg-card-subtle)", padding: "12px 14px", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>CGPA / Graduation</div>
              <div style={{ fontSize: "12.5px", fontWeight: "700", color: "var(--accent-emerald-text)", marginTop: "4px" }}>
                {profile?.cgpa || 8.39} / 10 ({profile?.graduation_year || 2028})
              </div>
            </div>
          </div>
        </div>
      </div>

      {uploadStatus && (
        <div
          style={{
            padding: "12px 18px",
            borderRadius: "10px",
            background: uploadStatus.type === "error" ? "var(--accent-rose-subtle)" : "var(--accent-emerald-subtle)",
            border: `1px solid ${uploadStatus.type === "error" ? "var(--accent-rose-border)" : "var(--accent-emerald-border)"}`,
            color: uploadStatus.type === "error" ? "var(--accent-rose-text)" : "var(--accent-emerald-text)",
            fontSize: "13px",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span>{uploadStatus.text}</span>
        </div>
      )}

      {/* Domain Category Filter Tabs */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: "800", color: "var(--text-primary)" }}>
            Categorized Project Catalog ({filteredProjects.length})
          </h3>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Click any domain to inspect segregated projects
          </span>
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "20px" }}>
          {["all", "sde", "data", "core", "product", "consult", "finance"].map((dKey) => {
            const isActive = selectedDomain === dKey;
            const count = counts[dKey] || 0;
            return (
              <button
                key={dKey}
                onClick={() => setSelectedDomain(dKey)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "8px 14px",
                  borderRadius: "10px",
                  border: isActive ? "1px solid var(--border-active)" : "1px solid var(--border-subtle)",
                  background: isActive ? "var(--primary-subtle)" : "var(--bg-card-subtle)",
                  color: isActive ? "var(--primary-text)" : "var(--text-secondary)",
                  fontSize: "12.5px",
                  fontWeight: isActive ? "700" : "500",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                {domainIcons[dKey] || <Layers size={14} />}
                <span>{domainLabels[dKey]}</span>
                <span
                  style={{
                    background: isActive ? "var(--primary)" : "var(--bg-card)",
                    color: isActive ? "#ffffff" : "var(--text-muted)",
                    padding: "1px 6px",
                    borderRadius: "10px",
                    fontSize: "10.5px",
                    fontWeight: "800",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Project Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "16px" }}>
          {filteredProjects.map((p, idx) => {
            const domainKey = (p.domain || "general").toLowerCase();
            const colors = domainColors[domainKey] || domainColors.general;

            return (
              <div
                key={idx}
                className="card"
                style={{
                  padding: "20px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  transition: "all 0.15s ease",
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px", gap: "8px" }}>
                    <h4 style={{ fontSize: "14.5px", fontWeight: "700", color: "var(--text-primary)", lineHeight: "1.4" }}>
                      {p.name}
                    </h4>
                    <span
                      style={{
                        background: colors.bg,
                        color: colors.text,
                        border: `1px solid ${colors.border}`,
                        padding: "2px 8px",
                        borderRadius: "6px",
                        fontSize: "10.5px",
                        fontWeight: "800",
                        textTransform: "uppercase",
                        whiteSpace: "nowrap",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                      }}
                    >
                      {domainIcons[domainKey]}
                      {p.domain || "General"}
                    </span>
                  </div>

                  <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", lineHeight: "1.5", marginBottom: "12px" }}>
                    {p.description || (p.bullets && p.bullets[0]) || "Multi-disciplinary engineering project."}
                  </p>

                  {/* Bullets */}
                  {p.bullets && p.bullets.length > 1 && (
                    <div style={{ borderLeft: "2px solid var(--border-active)", paddingLeft: "10px", marginBottom: "12px", display: "flex", flexDirection: "column", gap: "4px" }}>
                      {p.bullets.slice(0, 2).map((b, bIdx) => (
                        <div key={bIdx} style={{ fontSize: "11.5px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                          • {b}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  {/* Tech Stack Tags */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "5px", marginTop: "8px" }}>
                    {(p.tech_stack || []).map((t, tIdx) => (
                      <span
                        key={tIdx}
                        style={{
                          background: "var(--bg-card-subtle)",
                          color: "var(--text-secondary)",
                          border: "1px solid var(--border-subtle)",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "10.5px",
                          fontWeight: "600",
                        }}
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
