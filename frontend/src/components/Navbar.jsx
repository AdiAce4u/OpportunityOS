import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Play,
  StopCircle,
  RefreshCw,
  Edit2,
  Check,
  X,
  Target,
  ChevronDown,
  Sun,
  Moon,
} from "lucide-react";

export function Navbar({
  running,
  onRunAgent,
  onStopAgent,
  onRefresh,
  activeGoal,
  onUpdateGoal,
  onOpenCustomJD,
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

  const [isEditingGoal, setIsEditingGoal] = useState(false);
  const [goalText, setGoalText] = useState(activeGoal || "Robotics or AI Internships in India (≥₹40,000/mo)");
  const dropdownRef = useRef(null);

  useEffect(() => {
    if (activeGoal) {
      setGoalText(activeGoal);
    }
  }, [activeGoal]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsEditingGoal(false);
      }
    }
    if (isEditingGoal) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isEditingGoal]);

  const presetGoals = [
    {
      title: "Robotics & Autonomous Systems Internships (≥₹40,000/mo)",
      category: "Robotics / ROS2",
      icon: "🤖",
    },
    {
      title: "AI & Machine Learning Engineer (PyTorch / Vision / LLMs)",
      category: "Machine Learning",
      icon: "🧠",
    },
    {
      title: "Embedded Systems, Controls & Firmware Engineering",
      category: "Embedded & Hardware",
      icon: "⚡",
    },
    {
      title: "Full-Stack Software Development (Python, React, FastAPI)",
      category: "Software Engineering",
      icon: "💻",
    },
    {
      title: "High-Growth Robotics & AI Startups (Bangalore / Remote)",
      category: "Tech Startups",
      icon: "🚀",
    },
    {
      title: "2026/2027 New Graduate Software Engineering Roles",
      category: "New Grad / Campus",
      icon: "🎓",
    },
  ];

  const handleSaveCustom = (e) => {
    if (e) e.preventDefault();
    if (goalText.trim()) {
      if (onUpdateGoal) onUpdateGoal(goalText.trim());
      setIsEditingGoal(false);
    }
  };

  const handleSelectPreset = (preset) => {
    setGoalText(preset.title);
    if (onUpdateGoal) onUpdateGoal(preset.title);
    setIsEditingGoal(false);
  };

  return (
    <header className="top-navbar">
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {/* Status Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              backgroundColor: running ? "var(--accent-emerald)" : "var(--primary)",
              boxShadow: running ? "0 0 10px var(--accent-emerald)" : "0 0 8px var(--primary)",
            }}
            className={running ? "pulse-indicator" : ""}
          />
          <span style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-secondary)" }}>
            {running ? "Autonomous Agent Running" : "OpportunityOS Core Ready"}
          </span>
        </div>

        {/* Clickable Goal Container & Popover */}
        <div style={{ position: "relative" }} ref={dropdownRef}>
          <div
            onClick={() => setIsEditingGoal(!isEditingGoal)}
            title="Click to change your autonomous goal or select from presets"
            style={{
              background: isEditingGoal ? "var(--bg-card-hover)" : "var(--bg-card-subtle)",
              border: `1px solid ${isEditingGoal ? "var(--border-active)" : "var(--border-subtle)"}`,
              padding: "6px 14px",
              borderRadius: "8px",
              fontSize: "12px",
              color: "var(--text-secondary)",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              cursor: "pointer",
              transition: "all 0.15s ease",
              userSelect: "none",
            }}
          >
            <Sparkles size={14} color="var(--primary)" />
            <span>
              Goal:{" "}
              <strong style={{ color: "var(--text-primary)" }}>
                {activeGoal || "Robotics & AI Internships in India (≥₹40,000/mo)"}
              </strong>
            </span>
            <Edit2 size={12} color="var(--primary)" style={{ marginLeft: "4px", opacity: 0.8 }} />
          </div>

          {/* Goal Editor Dropdown */}
          {isEditingGoal && (
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 8px)",
                left: 0,
                width: "min(460px, 92vw)",
                background: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "12px",
                padding: "16px",
                boxShadow: "var(--card-shadow-hover)",
                zIndex: 150,
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Target size={16} color="var(--primary)" />
                  <span style={{ fontSize: "13px", fontWeight: "700", color: "var(--text-primary)" }}>
                    Configure Autonomous Search Goal
                  </span>
                </div>
                <button
                  onClick={() => setIsEditingGoal(false)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "var(--text-muted)",
                    cursor: "pointer",
                    padding: "4px",
                  }}
                >
                  <X size={16} />
                </button>
              </div>

              {/* Custom Input Form */}
              <form onSubmit={handleSaveCustom} style={{ display: "flex", gap: "8px" }}>
                <input
                  type="text"
                  className="input"
                  autoFocus
                  placeholder="Type custom role, criteria, or stipend requirement..."
                  value={goalText}
                  onChange={(e) => setGoalText(e.target.value)}
                  style={{ fontSize: "12.5px", padding: "8px 12px", flex: 1 }}
                />
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ padding: "8px 14px", fontSize: "12px", whiteSpace: "nowrap" }}
                >
                  <Check size={14} />
                  <span>Apply</span>
                </button>
              </form>

              {/* Presets List */}
              <div>
                <div style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "8px" }}>
                  Or Choose from Curated Presets
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", maxHeight: "240px", overflowY: "auto" }}>
                  {presetGoals.map((p, idx) => {
                    const isSelected = activeGoal === p.title;
                    return (
                      <div
                        key={idx}
                        onClick={() => handleSelectPreset(p)}
                        style={{
                          background: isSelected ? "var(--primary-subtle)" : "var(--bg-card-subtle)",
                          border: `1px solid ${isSelected ? "var(--border-active)" : "var(--border-subtle)"}`,
                          borderRadius: "8px",
                          padding: "10px 12px",
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          transition: "all 0.15s ease",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                          <span style={{ fontSize: "16px" }}>{p.icon}</span>
                          <div>
                            <div style={{ fontSize: "12.5px", fontWeight: "600", color: isSelected ? "var(--primary-text)" : "var(--text-primary)" }}>
                              {p.title}
                            </div>
                            <span style={{ fontSize: "10.5px", color: "var(--primary)" }}>{p.category}</span>
                          </div>
                        </div>
                        {isSelected && <Check size={15} color="var(--primary)" />}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <button
          className="btn btn-secondary"
          onClick={toggleTheme}
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          style={{ padding: "8px 12px", display: "flex", alignItems: "center", gap: "6px" }}
        >
          {theme === "dark" ? <Sun size={15} color="#f59e0b" /> : <Moon size={15} color="#6366f1" />}
          <span style={{ fontSize: "12px", fontWeight: "600" }}>{theme === "dark" ? "Light" : "Dark"}</span>
        </button>

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
          onClick={onRefresh}
          title="Refresh Data"
          style={{ padding: "8px 12px" }}
        >
          <RefreshCw size={15} />
        </button>

        {running ? (
          <button className="btn btn-danger" onClick={onStopAgent}>
            <StopCircle size={16} />
            <span>Kill Switch</span>
          </button>
        ) : (
          <button className="btn btn-primary" onClick={onRunAgent}>
            <Play size={15} fill="currentColor" />
            <span>Start Autonomous Agent</span>
          </button>
        )}
      </div>
    </header>
  );
}
