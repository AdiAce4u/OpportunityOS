import React from "react";
import { MapPin, DollarSign, Check, AlertCircle, ArrowUpRight, Award } from "lucide-react";

export function TopOpportunities({ jobs = [], onSelectJob, onOpenReview, onOpenCustomJD, maxItems }) {
  const displayJobs = maxItems ? jobs.slice(0, maxItems) : jobs;

  return (
    <div className="card" style={{ padding: "20px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Award size={18} color="var(--primary)" />
          <h3 style={{ fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>Top Opportunities</h3>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {onOpenCustomJD && (
            <button
              className="btn btn-secondary"
              style={{ fontSize: "11.5px", padding: "4px 10px", height: "auto" }}
              onClick={onOpenCustomJD}
            >
              + Paste Custom JD
            </button>
          )}
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Ranked by Multi-Factor Fit</span>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {displayJobs.length === 0 ? (
          <div style={{ color: "var(--text-muted)", padding: "20px", textAlign: "center" }}>
            No opportunities shortlisted yet. Run the agent to discover and match roles.
          </div>
        ) : (
          displayJobs.map((item, idx) => {
            const job = item.job || item;
            const score = item.score || item.match_score || 91;
            const why = item.why_this_job || {};
            const present = why.required_present || job.required_skills?.slice(0, 3) || [];
            const missing = why.missing || [];

            return (
              <div
                key={idx}
                style={{
                  background: "var(--bg-card-subtle)",
                  border: "1px solid var(--border-subtle)",
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
                    <span style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>
                      {job.title}
                    </span>
                    <span className="badge badge-success" style={{ fontSize: "11px", fontWeight: "800", padding: "2px 8px" }}>
                      {score}% Match
                    </span>
                  </div>

                  <div style={{ fontSize: "12.5px", color: "var(--text-secondary)", display: "flex", gap: "14px", alignItems: "center", marginBottom: "8px" }}>
                    <span style={{ fontWeight: "600", color: "var(--text-primary)" }}>{job.company}</span>
                    <span style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                      <MapPin size={13} color="var(--text-muted)" /> {job.location || "Remote"}
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: "3px", color: "var(--accent-cyan-text)", fontWeight: "600" }}>
                      <DollarSign size={13} /> {job.salary_text || "Competitive"}
                    </span>
                  </div>

                  {/* Why this job tag breakdown */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
                    {present.map((skill, sIdx) => (
                      <span
                        key={sIdx}
                        style={{
                          background: "var(--accent-emerald-subtle)",
                          color: "var(--accent-emerald-text)",
                          border: "1px solid var(--accent-emerald-border)",
                          fontSize: "11px",
                          fontWeight: "600",
                          padding: "2px 8px",
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
                          background: "var(--accent-rose-subtle)",
                          color: "var(--accent-rose-text)",
                          border: "1px solid var(--accent-rose-border)",
                          fontSize: "11px",
                          fontWeight: "600",
                          padding: "2px 8px",
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
