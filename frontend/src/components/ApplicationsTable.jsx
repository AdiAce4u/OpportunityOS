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
          <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#f8fafc" }}>
            Application Pipeline & Tracker
          </h3>
          <p style={{ fontSize: "13px", color: "#94a3b8", marginTop: "2px" }}>
            Tracked across full lifecycle: Discovered → Eligible → Shortlisted → Preparing → Awaiting Approval → Submitted → Interview
          </p>
        </div>
        <span style={{ fontSize: "12px", color: "#64748b", fontWeight: "600" }}>
          {applications.length} Total Tracked
        </span>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "13.5px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #1e293b", color: "#64748b", fontSize: "12px", textTransform: "uppercase" }}>
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
                <td colSpan={6} style={{ padding: "32px", textAlign: "center", color: "#64748b" }}>
                  No applications prepared yet. Start the agent to discover matches.
                </td>
              </tr>
            ) : (
              applications.map((app) => (
                <tr
                  key={app.id}
                  style={{
                    borderBottom: "1px solid #111a2e",
                    transition: "background 0.15s ease",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "#0c1324")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                >
                  <td style={{ padding: "14px 16px" }}>
                    <div style={{ fontWeight: "700", color: "#ffffff" }}>{app.title}</div>
                    <div style={{ fontSize: "12px", color: "#94a3b8" }}>{app.company} · {app.location}</div>
                  </td>
                  <td style={{ padding: "14px 16px" }}>
                    <span style={{ fontWeight: "800", color: app.match_score >= 85 ? "#10b981" : "#38bdf8" }}>
                      {app.match_score || "—"}%
                    </span>
                  </td>
                  <td style={{ padding: "14px 16px" }}>{getStatusBadge(app.status)}</td>
                  <td style={{ padding: "14px 16px", fontFamily: "'JetBrains Mono', monospace", fontSize: "12px", color: "#cbd5e1" }}>
                    {app.external_application_id || "—"}
                  </td>
                  <td style={{ padding: "14px 16px", fontSize: "12px", color: "#64748b" }}>
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
