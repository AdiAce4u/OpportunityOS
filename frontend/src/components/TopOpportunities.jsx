import React from "react";
import { MapPin, DollarSign, Check, AlertCircle, ArrowUpRight, Award } from "lucide-react";

export function TopOpportunities({ jobs = [], onSelectJob, onOpenReview }) {
  return (
    <div className="card" style={{ padding: "20px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Award size={18} color="#818cf8" />
          <h3 style={{ fontSize: "15px", fontWeight: "700", color: "#f8fafc" }}>Top Opportunities</h3>
        </div>
        <span style={{ fontSize: "12px", color: "#64748b" }}>Ranked by Multi-Factor Fit</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {jobs.length === 0 ? (
          <div style={{ color: "#64748b", padding: "20px", textAlign: "center" }}>
            No opportunities shortlisted yet. Run the agent to discover and match roles.
          </div>
        ) : (
          jobs.slice(0, 4).map((item, idx) => {
            const job = item.job || item;
            const score = item.score || item.match_score || 91;
            const why = item.why_this_job || {};
            const present = why.required_present || job.required_skills?.slice(0, 3) || [];
            const missing = why.missing || [];

            return (
              <div
                key={idx}
                style={{
                  background: "#080c16",
                  border: "1px solid #1a233a",
                  borderRadius: "10px",
                  padding: "16px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  transition: "all 0.15s ease",
                }}
              >
                <div style={{ flex: 1, minWidth: 0, paddingRight: "16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
                    <span style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff" }}>
                      {job.title}
                    </span>
                    <span
                      style={{
                        background: "rgba(16, 185, 129, 0.15)",
                        color: "#34d399",
                        border: "1px solid rgba(16, 185, 129, 0.3)",
                        padding: "2px 8px",
                        borderRadius: "12px",
                        fontSize: "11px",
                        fontWeight: "800",
                      }}
                    >
                      {score}% Match
                    </span>
                  </div>

                  <div style={{ fontSize: "12.5px", color: "#94a3b8", display: "flex", gap: "14px", alignItems: "center", marginBottom: "8px" }}>
                    <span style={{ fontWeight: "600", color: "#cbd5e1" }}>{job.company}</span>
                    <span style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                      <MapPin size={13} color="#64748b" /> {job.location || "Remote"}
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: "3px", color: "#38bdf8" }}>
                      <DollarSign size={13} /> {job.salary_text || "Competitive"}
                    </span>
                  </div>

                  {/* Why this job tag breakdown */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
                    {present.map((skill, sIdx) => (
                      <span
                        key={sIdx}
                        style={{
                          background: "#064e3b33",
                          color: "#34d399",
                          fontSize: "10.5px",
                          fontWeight: "600",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "3px",
                        }}
                      >
                        <Check size={10} /> {skill}
                      </span>
                    ))}
                    {missing.slice(0, 2).map((skill, mIdx) => (
                      <span
                        key={mIdx}
                        style={{
                          background: "#7f1d1d33",
                          color: "#fca5a5",
                          fontSize: "10.5px",
                          fontWeight: "600",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "3px",
                        }}
                      >
                        <AlertCircle size={10} /> Missing: {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <button
                    className="btn btn-secondary"
                    style={{ fontSize: "12px", padding: "8px 12px" }}
                    onClick={() => (onOpenReview ? onOpenReview(job) : onSelectJob && onSelectJob(job))}
                  >
                    <span>View Application</span>
                    <ArrowUpRight size={14} />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
