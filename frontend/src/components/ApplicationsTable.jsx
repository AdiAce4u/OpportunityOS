import React from "react";
import { CheckCircle2, Clock, Send, AlertCircle, Eye, ArrowUpRight } from "lucide-react";

export function ApplicationsTable({ applications = [], onOpenApplication }) {
  const getStatusBadge = (status) => {
    switch (status) {
      case "AWAITING_APPROVAL":
        return <span className="badge badge-warning">Awaiting Approval</span>;
      case "SUBMITTED":
        return <span className="badge badge-success">Submitted</span>;
      case "INTERVIEW":
        return <span className="badge badge-primary">Interview Scheduled</span>;
      case "REJECTED_BY_USER":
        return <span className="badge badge-danger">Rejected by User</span>;
      case "UNDER_REVIEW":
        return <span className="badge badge-cyan">Under Review</span>;
      default:
        return <span className="badge badge-secondary">{status}</span>;
    }
  };

  return (
    <div className="card" style={{ padding: "24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h3 style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)" }}>
            Application Pipeline & Tracker
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>
            Tracked across full lifecycle: Discovered → Eligible → Shortlisted → Preparing → Awaiting Approval → Submitted → Interview
          </p>
        </div>
        <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600" }}>
          {applications.length} Total Tracked
        </span>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "13.5px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase" }}>
              <th style={{ padding: "12px 16px" }}>Position & Company</th>
              <th style={{ padding: "12px 16px" }}>Match</th>
              <th style={{ padding: "12px 16px" }}>Status</th>
              <th style={{ padding: "12px 16px" }}>Application ID</th>
              <th style={{ padding: "12px 16px" }}>Last Updated</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {applications.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: "32px", textAlign: "center", color: "var(--text-muted)" }}>
                  No applications prepared yet. Start the agent to discover matches.
                </td>
              </tr>
            ) : (
              applications.map((app) => (
                <tr
                  key={app.id}
                  style={{
                    borderBottom: "1px solid var(--border-subtle)",
                    transition: "background 0.15s ease",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-card-hover)")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                >
                  <td style={{ padding: "14px 16px" }}>
                    <div style={{ fontWeight: "700", color: "var(--text-primary)" }}>{app.title}</div>
                    <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>{app.company} · {app.location}</div>
                  </td>
                  <td style={{ padding: "14px 16px" }}>
                    <span style={{ fontWeight: "800", color: app.match_score >= 85 ? "var(--accent-emerald)" : "var(--primary)" }}>
                      {app.match_score || "—"}%
                    </span>
                  </td>
                  <td style={{ padding: "14px 16px" }}>{getStatusBadge(app.status)}</td>
                  <td style={{ padding: "14px 16px", fontFamily: "'JetBrains Mono', monospace", fontSize: "12px", color: "var(--text-secondary)" }}>
                    {app.external_application_id || "—"}
                  </td>
                  <td style={{ padding: "14px 16px", fontSize: "12px", color: "var(--text-muted)" }}>
                    {app.updated_at || app.applied_date || "Just now"}
                  </td>
                  <td style={{ padding: "14px 16px", textAlign: "right" }}>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: "6px 12px", fontSize: "12px" }}
                      onClick={() => onOpenApplication(app.id)}
                    >
                      <Eye size={13} />
                      <span>{app.status === "AWAITING_APPROVAL" ? "Review" : "Details"}</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
