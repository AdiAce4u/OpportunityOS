import React from "react";
import {
  LayoutDashboard,
  GitFork,
  FileCheck,
  Briefcase,
  User,
  GraduationCap,
  ShieldCheck,
  Zap,
} from "lucide-react";

export function Sidebar({ currentTab, setTab, awaitingCount, interviewCount }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} /> },
    { id: "pipeline", label: "Agent Pipeline", icon: <GitFork size={18} /> },
    {
      id: "applications",
      label: "Applications & Review",
      icon: <FileCheck size={18} />,
      badge: awaitingCount > 0 ? awaitingCount : null,
      badgeColor: "#f59e0b",
    },
    { id: "opportunities", label: "Discovered Jobs", icon: <Briefcase size={18} /> },
    { id: "profile", label: "Profile & Resume", icon: <User size={18} /> },
    {
      id: "interview",
      label: "Interview Copilot",
      icon: <GraduationCap size={18} />,
      badge: interviewCount > 0 ? interviewCount : null,
      badgeColor: "#10b981",
    },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "36px", padding: "0 8px" }}>
        <div
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            background: "linear-gradient(135deg, #6366f1 0%, #3b82f6 100%)",
            display: "grid",
            placeItems: "center",
            color: "white",
            boxShadow: "0 4px 15px rgba(99, 102, 241, 0.4)",
          }}
        >
          <Zap size={20} />
        </div>
        <div>
          <h2 style={{ fontSize: "18px", fontWeight: "800", letterSpacing: "-0.02em", color: "#f8fafc" }} className="brand-text">
            Opportunity<span style={{ color: "#818cf8" }}>OS</span>
          </h2>
          <p style={{ fontSize: "11px", color: "#64748b", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.08em" }} className="brand-text">
            Agentic Job Engine
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ display: "flex", flexDirection: "column", gap: "6px", flex: 1 }}>
        {navItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setTab(item.id)}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "12px 14px",
                borderRadius: "10px",
                border: "none",
                background: isActive ? "#18223a" : "transparent",
                color: isActive ? "#ffffff" : "#94a3b8",
                fontWeight: isActive ? "600" : "500",
                fontSize: "14px",
                cursor: "pointer",
                transition: "all 0.15s ease",
                textAlign: "left",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <span style={{ color: isActive ? "#818cf8" : "#64748b" }}>{item.icon}</span>
                <span className="nav-text">{item.label}</span>
              </div>
              {item.badge && (
                <span
                  style={{
                    background: item.badgeColor,
                    color: "#000",
                    fontWeight: "800",
                    fontSize: "11px",
                    padding: "2px 7px",
                    borderRadius: "10px",
                  }}
                  className="nav-text"
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Safety Notice Footer */}
      <div
        style={{
          background: "#0d1322",
          border: "1px solid #1c2742",
          borderRadius: "10px",
          padding: "14px",
          display: "flex",
          gap: "10px",
          alignItems: "flex-start",
        }}
        className="nav-text"
      >
        <ShieldCheck size={18} color="#10b981" style={{ flexShrink: 0, marginTop: "2px" }} />
        <div>
          <div style={{ fontSize: "11px", fontWeight: "700", color: "#e2e8f0" }}>Safety Guaranteed</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", lineHeight: "1.4" }}>
            Strictly zero qualification fabrication. Human approval enforced.
          </div>
        </div>
      </div>
    </aside>
  );
}
