import React, { useState, useEffect } from "react";
import { Sparkles, Sun, Moon, PanelLeftOpen, PanelLeftClose } from "lucide-react";

export function Navbar({
  running,
  onRunAgent,
  onStopAgent,
  onRefresh,
  activeGoal,
  onUpdateGoal,
  onOpenCustomJD,
  isSidebarCollapsed,
  onToggleSidebar,
}) {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("opportunity_theme") || "dark";
    } catch (e) {
      return "dark";
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("opportunity_theme", theme);
    } catch (e) {}
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <header className="top-navbar">
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
              padding: "6px",
              borderRadius: "6px",
              display: "grid",
              placeItems: "center",
              transition: "all 0.15s ease",
            }}
            title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "var(--text-primary)";
              e.currentTarget.style.background = "var(--bg-card-subtle)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = "var(--text-muted)";
              e.currentTarget.style.background = "transparent";
            }}
          >
            {isSidebarCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
          </button>
        )}
        <div
          style={{
            width: "10px",
            height: "10px",
            borderRadius: "50%",
            backgroundColor: "var(--primary)",
            boxShadow: "0 0 8px var(--primary)",
          }}
        />
        <span style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-secondary)" }}>
          OpportunityOS Core Ready
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginLeft: "auto" }}>
        <button
          className="btn btn-secondary"
          onClick={onOpenCustomJD}
          title="Paste & Analyze any external Job Description"
          style={{ padding: "8px 14px", display: "flex", alignItems: "center", gap: "6px" }}
        >
          <Sparkles size={14} color="#38bdf8" />
          <span>Analyze Custom JD</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={toggleTheme}
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          style={{ padding: "8px 12px", display: "flex", alignItems: "center", gap: "6px" }}
        >
          {theme === "dark" ? <Sun size={15} color="#f59e0b" /> : <Moon size={15} color="#6366f1" />}
          <span style={{ fontSize: "12px", fontWeight: "600" }}>{theme === "dark" ? "Light" : "Dark"}</span>
        </button>
      </div>
    </header>
  );
}
