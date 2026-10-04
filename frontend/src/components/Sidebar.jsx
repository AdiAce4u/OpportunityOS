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
  FolderGit2,
  Globe,
} from "lucide-react";

export function Sidebar({ currentTab, setTab, awaitingCount, interviewCount, projectsCount }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} /> },
    {
      id: "master_cv",
      label: "Master CV & Projects",
      icon: <FolderGit2 size={18} />,
      badge: projectsCount > 0 ? `${projectsCount}` : null,
      badgeColor: "#38bdf8",
    },
    {
      id: "portal_discovery",
      label: "Job Discovery Engine",
      icon: <Globe size={18} />,
      badge: "5 Tracks",
      badgeColor: "#818cf8",
    },
    {
      id: "applications",
      label: "Applications & Review",
      icon: <FileCheck size={18} />,
      badge: awaitingCount > 0 ? awaitingCount : null,
      badgeColor: "#f59e0b",
    },
    { id: "opportunities", label: "Discovered Jobs", icon: <Briefcase size={18} /> },
    { id: "pipeline", label: "Agent Pipeline", icon: <GitFork size={18} /> },
    { id: "profile", label: "Profile & Ground Truth", icon: <User size={18} /> },
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
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "32px", padding: "0 8px" }}>
        <div
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            background: "var(--primary)",
            display: "grid",
            placeItems: "center",
            color: "white",
            boxShadow: "0 4px 14px var(--primary-glow)",
          }}
        >
          <Zap size={20} />
        </div>
        <div>
          <h2 style={{ fontSize: "18px", fontWeight: "800", letterSpacing: "-0.02em", color: "var(--text-primary)" }} className="brand-text">
            Opportunity<span style={{ color: "var(--primary)" }}>OS</span>
          </h2>
          <p style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.08em" }} className="brand-text">
            Agentic Job Engine
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ display: "flex", flexDirection: "column", gap: "5px", flex: 1 }}>
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
                padding: "11px 14px",
                borderRadius: "10px",
                border: "none",
                background: isActive ? "var(--primary-subtle)" : "transparent",
                color: isActive ? "var(--primary-text)" : "var(--text-secondary)",
                fontWeight: isActive ? "700" : "500",
                fontSize: "13.5px",
                cursor: "pointer",
                transition: "all 0.15s ease",
                textAlign: "left",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <span style={{ color: isActive ? "var(--primary)" : "var(--text-muted)" }}>{item.icon}</span>
                <span className="nav-text">{item.label}</span>
              </div>
              {item.badge && (
                <span
                  style={{
                    background: item.badgeColor,
                    color: item.badgeColor === "#38bdf8" || item.badgeColor === "#818cf8" ? "#0f172a" : "#ffffff",
                    fontWeight: "800",
                    fontSize: "10.5px",
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
          background: "var(--bg-card-subtle)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "10px",
          padding: "12px",
          display: "flex",
          gap: "10px",
          alignItems: "flex-start",
        }}
        className="nav-text"
      >
        <ShieldCheck size={18} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: "2px" }} />
        <div>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-primary)" }}>Human Approval Enforced</div>
          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px", lineHeight: "1.35" }}>
            Zero synthetic qualifications. Permission required before submission.
          </div>
        </div>
      </div>
    </aside>
  );
}
