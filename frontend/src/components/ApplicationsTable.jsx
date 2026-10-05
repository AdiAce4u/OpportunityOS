import React, { useState } from "react";
import {
  CheckCircle2,
  Clock,
  Send,
  AlertCircle,
  Eye,
  ArrowUpRight,
  Heart,
  Bookmark,
  Sparkles,
  Layers,
} from "lucide-react";

export function ApplicationsTable({ applications = [], onOpenApplication, onToggleWishlist }) {
  const [filterType, setFilterType] = useState("all"); // "all" | "submitted" | "wishlisted" | "browsed"

  // Counts
  const submittedCount = applications.filter(
    (a) => a.is_applied || a.status === "SUBMITTED" || a.status === "APPLIED" || a.applied_date
  ).length;

  const wishlistedCount = applications.filter((a) => a.is_wishlisted).length;

  const browsedCount = applications.filter((a) => a.recently_browsed).length;

  const awaitingCount = applications.filter((a) => a.status === "AWAITING_APPROVAL").length;

  // Filtered applications
  const filteredApps = applications.filter((app) => {
    if (filterType === "submitted") {
      return app.is_applied || app.status === "SUBMITTED" || app.status === "APPLIED" || app.applied_date;
    }
    if (filterType === "wishlisted") {
      return app.is_wishlisted;
    }
    if (filterType === "browsed") {
      return app.recently_browsed;
    }
    return true; // "all"
  });

  const getStatusBadge = (status, isWishlisted, isBrowsed) => {
    switch (status) {
      case "AWAITING_APPROVAL":
        return <span className="badge badge-warning">Awaiting Approval</span>;
      case "SUBMITTED":
      case "APPLIED":
        return <span className="badge badge-success">Applied</span>;
      case "INTERVIEW":
        return <span className="badge badge-primary">Interview Scheduled</span>;
      case "REJECTED_BY_USER":
        return <span className="badge badge-danger">Rejected by User</span>;
      case "UNDER_REVIEW":
        return <span className="badge badge-cyan">Under Review</span>;
      case "WISHLISTED":
        return (
          <span
            style={{
              background: "rgba(244, 63, 94, 0.12)",
              color: "var(--accent-rose-text)",
              border: "1px solid var(--accent-rose-border)",
              padding: "2px 8px",
              borderRadius: "6px",
              fontSize: "11px",
              fontWeight: "700",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <Heart size={11} fill="#f43f5e" color="#f43f5e" /> Wishlisted
          </span>
        );
      case "RECENTLY_BROWSED":
        return (
          <span
            style={{
              background: "var(--accent-indigo-subtle)",
              color: "var(--accent-indigo-text)",
              border: "1px solid var(--accent-indigo-border)",
              padding: "2px 8px",
              borderRadius: "6px",
              fontSize: "11px",
              fontWeight: "700",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <Eye size={11} /> Browsed
          </span>
        );
      default:
        return <span className="badge badge-secondary">{status}</span>;
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Top Application Review Summary Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
        {/* Card 1: Submitted Applications */}
        <div
          className="card"
          onClick={() => setFilterType("submitted")}
          style={{
            padding: "18px 20px",
            cursor: "pointer",
            border: filterType === "submitted" ? "1px solid var(--primary)" : "1px solid var(--border-subtle)",
            background: filterType === "submitted" ? "var(--primary-subtle)" : "var(--bg-card)",
            boxShadow: filterType === "submitted" ? "0 4px 14px var(--primary-glow)" : "none",
            transition: "all 0.15s ease",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
              Applications Submitted
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--primary-subtle)", display: "grid", placeItems: "center", color: "var(--primary)" }}>
              <Send size={16} />
            </div>
          </div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--primary-text)" }}>
            {submittedCount}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Target portal submissions
          </div>
        </div>

        {/* Card 2: Wishlisted Opportunities */}
        <div
          className="card"
          onClick={() => setFilterType("wishlisted")}
          style={{
            padding: "18px 20px",
            cursor: "pointer",
            border: filterType === "wishlisted" ? "1px solid var(--accent-rose-border)" : "1px solid var(--border-subtle)",
            background: filterType === "wishlisted" ? "var(--accent-rose-subtle)" : "var(--bg-card)",
            boxShadow: filterType === "wishlisted" ? "0 4px 14px rgba(244, 63, 94, 0.18)" : "none",
            transition: "all 0.15s ease",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
              Wishlisted Roles
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "rgba(244, 63, 94, 0.12)", display: "grid", placeItems: "center", color: "var(--accent-rose)" }}>
              <Heart size={16} fill="#f43f5e" color="#f43f5e" />
            </div>
          </div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--accent-rose-text)" }}>
            {wishlistedCount}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Curated target positions
          </div>
        </div>

        {/* Card 3: Recently Browsed */}
        <div
          className="card"
          onClick={() => setFilterType("browsed")}
          style={{
            padding: "18px 20px",
            cursor: "pointer",
            border: filterType === "browsed" ? "1px solid var(--accent-indigo-border)" : "1px solid var(--border-subtle)",
            background: filterType === "browsed" ? "var(--accent-indigo-subtle)" : "var(--bg-card)",
            boxShadow: filterType === "browsed" ? "0 4px 14px rgba(99, 102, 241, 0.18)" : "none",
            transition: "all 0.15s ease",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
              Recently Browsed
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--accent-indigo-subtle)", display: "grid", placeItems: "center", color: "var(--accent-indigo-text)" }}>
              <Eye size={16} />
            </div>
          </div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--accent-indigo-text)" }}>
            {browsedCount}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Roles you explored
          </div>
        </div>

        {/* Card 4: Awaiting Approval */}
        <div
          className="card"
          onClick={() => setFilterType("all")}
          style={{
            padding: "18px 20px",
            cursor: "pointer",
            border: "1px solid var(--border-subtle)",
            background: "var(--bg-card)",
            transition: "all 0.15s ease",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
              Awaiting Review
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "rgba(245, 158, 11, 0.12)", display: "grid", placeItems: "center", color: "var(--accent-amber)" }}>
              <Clock size={16} />
            </div>
          </div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--accent-amber-text)" }}>
            {awaitingCount}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
            1-Page ATS packages ready
          </div>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="card" style={{ padding: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h3 style={{ fontSize: "17px", fontWeight: "800", color: "var(--text-primary)" }}>
              Application Pipeline & Tracker
            </h3>
          </div>

          {/* Filter Pills */}
          <div style={{ display: "flex", gap: "6px", background: "var(--bg-card-subtle)", padding: "4px", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
            <button
              type="button"
              onClick={() => setFilterType("all")}
              style={{
                padding: "5px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "700",
                border: "none",
                cursor: "pointer",
                background: filterType === "all" ? "var(--primary)" : "transparent",
                color: filterType === "all" ? "#fff" : "var(--text-secondary)",
              }}
            >
              All Tracked ({applications.length})
            </button>
            <button
              type="button"
              onClick={() => setFilterType("submitted")}
              style={{
                padding: "5px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "700",
                border: "none",
                cursor: "pointer",
                background: filterType === "submitted" ? "var(--primary)" : "transparent",
                color: filterType === "submitted" ? "#fff" : "var(--text-secondary)",
              }}
            >
              Submitted ({submittedCount})
            </button>
            <button
              type="button"
              onClick={() => setFilterType("wishlisted")}
              style={{
                padding: "5px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "700",
                border: "none",
                cursor: "pointer",
                background: filterType === "wishlisted" ? "var(--accent-rose)" : "transparent",
                color: filterType === "wishlisted" ? "#fff" : "var(--text-secondary)",
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <Heart size={12} fill={filterType === "wishlisted" ? "#fff" : "#f43f5e"} color={filterType === "wishlisted" ? "#fff" : "#f43f5e"} />
              Wishlisted ({wishlistedCount})
            </button>
            <button
              type="button"
              onClick={() => setFilterType("browsed")}
              style={{
                padding: "5px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "700",
                border: "none",
                cursor: "pointer",
                background: filterType === "browsed" ? "var(--primary)" : "transparent",
                color: filterType === "browsed" ? "#fff" : "var(--text-secondary)",
              }}
            >
              Browsed ({browsedCount})
            </button>
          </div>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "13.5px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase" }}>
                <th style={{ padding: "12px 14px", width: "40px", textAlign: "center" }}>Wishlist</th>
                <th style={{ padding: "12px 16px" }}>Position & Company</th>
                <th style={{ padding: "12px 16px" }}>Match</th>
                <th style={{ padding: "12px 16px" }}>Status</th>
                <th style={{ padding: "12px 16px" }}>Last Activity</th>
                <th style={{ padding: "12px 16px", textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredApps.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}>
                      <Heart size={28} style={{ opacity: 0.4 }} />
                      <div style={{ fontWeight: "600", fontSize: "14px" }}>
                        {filterType === "wishlisted"
                          ? "No wishlisted opportunities yet."
                          : filterType === "submitted"
                          ? "No applications submitted yet."
                          : "No opportunities tracked yet."}
                      </div>
                      <div style={{ fontSize: "12.5px" }}>
                        Click the heart icon on any job in Top Opportunities or Job Discovery Engine to add it here.
                      </div>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredApps.map((app) => (
                  <tr
                    key={app.id}
                    style={{
                      borderBottom: "1px solid var(--border-subtle)",
                      transition: "background 0.15s ease",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                  >
                    {/* Heart-shaped Wishlist Button */}
                    <td style={{ padding: "14px 14px", textAlign: "center" }}>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onToggleWishlist) onToggleWishlist(app);
                        }}
                        style={{
                          background: "transparent",
                          border: "none",
                          cursor: "pointer",
                          padding: "6px",
                          borderRadius: "50%",
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                          transition: "transform 0.15s ease",
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.2)")}
                        onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
                        title={app.is_wishlisted ? "Remove from Wishlist" : "Add to Wishlist"}
                      >
                        <Heart
                          size={18}
                          fill={app.is_wishlisted ? "#f43f5e" : "transparent"}
                          color={app.is_wishlisted ? "#f43f5e" : "var(--text-muted)"}
                        />
                      </button>
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      <div style={{ fontWeight: "700", color: "var(--text-primary)" }}>{app.title}</div>
                      <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        {app.company} · {app.location || "Remote"} · {app.salary_text || "Competitive"}
                      </div>
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      <span style={{ fontWeight: "800", color: app.match_score >= 85 ? "var(--accent-emerald)" : "var(--primary)" }}>
                        {app.match_score ? `${app.match_score}%` : "—"}
                      </span>
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      {getStatusBadge(app.status, app.is_wishlisted, app.recently_browsed)}
                    </td>

                    <td style={{ padding: "14px 16px", fontSize: "12px", color: "var(--text-muted)" }}>
                      {app.updated_at || app.applied_date || "Recently"}
                    </td>

                    <td style={{ padding: "14px 16px", textAlign: "right" }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: "6px 12px", fontSize: "12px" }}
                        onClick={() => onOpenApplication(app.id)}
                      >
                        <Eye size={13} />
                        <span>
                          {app.status === "AWAITING_APPROVAL"
                            ? "Review & Apply"
                            : app.is_applied
                            ? "View Receipt"
                            : "Details & Tailor"}
                        </span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
