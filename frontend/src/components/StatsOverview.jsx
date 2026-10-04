import React from "react";
import {
  Search,
  CheckCircle,
  Filter,
  FileText,
  Send,
  Calendar,
  Award,
  Clock,
  TrendingUp,
} from "lucide-react";

export function StatsOverview({ metrics = {} }) {
  const cards = [
    {
      label: "Opportunities Found",
      value: metrics.total_opportunities_found ?? "—",
      sub: "Across all sources",
      icon: <Search size={20} color="#818cf8" />,
      glow: "rgba(99, 102, 241, 0.15)",
    },
    {
      label: "Eligible Opportunities",
      value: metrics.eligible_opportunities ?? "—",
      sub: "Passed constraints",
      icon: <CheckCircle size={20} color="#10b981" />,
      glow: "rgba(16, 185, 129, 0.15)",
    },
    {
      label: "Shortlisted Roles",
      value: metrics.shortlisted ?? "—",
      sub: "Match score ≥ 70%",
      icon: <Filter size={20} color="#06b6d4" />,
      glow: "rgba(6, 182, 212, 0.15)",
    },
    {
      label: "Applications Prepared",
      value: metrics.applications_prepared ?? "—",
      sub: "Tailored & reviewed",
      icon: <FileText size={20} color="#f59e0b" />,
      glow: "rgba(245, 158, 11, 0.15)",
    },
    {
      label: "Applications Submitted",
      value: metrics.applications_submitted ?? "—",
      sub: "Automated submission",
      icon: <Send size={20} color="#3b82f6" />,
      glow: "rgba(59, 130, 246, 0.15)",
    },
    {
      label: "Interviews Detected",
      value: metrics.interviews ?? "0",
      sub: "Invitations received",
      icon: <Calendar size={20} color="#a855f7" />,
      glow: "rgba(168, 85, 247, 0.15)",
    },
    {
      label: "Offers & Milestones",
      value: metrics.offers ?? "0",
      sub: "Accepted offers",
      icon: <Award size={20} color="#10b981" />,
      glow: "rgba(16, 185, 129, 0.15)",
    },
    {
      label: "Time Saved",
      value: `${metrics.estimated_time_saved_hours || 0} hrs`,
      sub: "Autonomous execution",
      icon: <Clock size={20} color="#f43f5e" />,
      glow: "rgba(244, 63, 94, 0.15)",
    },
  ];

  return (
    <section className="stats-grid">
      {cards.map((c, i) => (
        <div
          key={i}
          className="card"
          style={{
            padding: "18px 20px",
            background: "#0c1221",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-15px",
              right: "-15px",
              width: "70px",
              height: "70px",
              borderRadius: "50%",
              background: c.glow,
              filter: "blur(20px)",
              pointerEvents: "none",
            }}
          />

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
            <span style={{ fontSize: "12.5px", fontWeight: "600", color: "#94a3b8" }}>{c.label}</span>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "8px",
                background: "#161f36",
                display: "grid",
                placeItems: "center",
              }}
            >
              {c.icon}
            </div>
          </div>

          <div>
            <div style={{ fontSize: "28px", fontWeight: "800", color: "#f8fafc", lineHeight: "1.1" }}>
              {c.value}
            </div>
            <div style={{ fontSize: "11.5px", color: "#64748b", marginTop: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
              <TrendingUp size={12} color="#10b981" />
              <span>{c.sub}</span>
            </div>
          </div>
        </div>
      ))}
    </section>
  );
}
