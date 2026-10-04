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
      icon: <Search size={18} color="var(--primary)" />,
      badgeBg: "var(--primary-subtle)",
    },
    {
      label: "Eligible Opportunities",
      value: metrics.eligible_opportunities ?? "—",
      sub: "Passed constraints",
      icon: <CheckCircle size={18} color="var(--accent-emerald)" />,
      badgeBg: "var(--accent-emerald-subtle)",
    },
    {
      label: "Shortlisted Roles",
      value: metrics.shortlisted ?? "—",
      sub: "Match score ≥ 70%",
      icon: <Filter size={18} color="var(--accent-cyan)" />,
      badgeBg: "var(--accent-cyan-subtle)",
    },
    {
      label: "Applications Prepared",
      value: metrics.applications_prepared ?? "—",
      sub: "Tailored & reviewed",
      icon: <FileText size={18} color="var(--accent-amber)" />,
      badgeBg: "var(--accent-amber-subtle)",
    },
    {
      label: "Applications Submitted",
      value: metrics.applications_submitted ?? "—",
      sub: "Automated submission",
      icon: <Send size={18} color="var(--primary)" />,
      badgeBg: "var(--primary-subtle)",
    },
    {
      label: "Interviews Detected",
      value: metrics.interviews ?? "0",
      sub: "Invitations received",
      icon: <Calendar size={18} color="var(--primary)" />,
      badgeBg: "var(--primary-subtle)",
    },
    {
      label: "Offers & Milestones",
      value: metrics.offers ?? "0",
      sub: "Accepted offers",
      icon: <Award size={18} color="var(--accent-emerald)" />,
      badgeBg: "var(--accent-emerald-subtle)",
    },
    {
      label: "Time Saved",
      value: `${metrics.estimated_time_saved_hours || 0} hrs`,
      sub: "Autonomous execution",
      icon: <Clock size={18} color="var(--accent-rose)" />,
      badgeBg: "var(--accent-rose-subtle)",
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
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            position: "relative",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
            <span style={{ fontSize: "12.5px", fontWeight: "600", color: "var(--text-secondary)" }}>{c.label}</span>
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "8px",
                background: c.badgeBg,
                display: "grid",
                placeItems: "center",
              }}
            >
              {c.icon}
            </div>
          </div>

          <div>
            <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--text-primary)", lineHeight: "1.1" }}>
              {c.value}
            </div>
            <div style={{ fontSize: "11.5px", color: "var(--text-muted)", marginTop: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
              <TrendingUp size={12} color="var(--accent-emerald)" />
              <span>{c.sub}</span>
            </div>
          </div>
        </div>
      ))}
    </section>
  );
}
