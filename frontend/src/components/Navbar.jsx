import React from "react";
import { Sparkles, Play, StopCircle, RefreshCw, ShieldCheck } from "lucide-react";

export function Navbar({ running, onRunAgent, onStopAgent, onRefresh, activeGoal }) {
  return (
    <header className="top-navbar">
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              backgroundColor: running ? "#10b981" : "#6366f1",
              boxShadow: running ? "0 0 12px #10b981" : "0 0 8px #6366f1",
            }}
            className={running ? "pulse-indicator" : ""}
          />
          <span style={{ fontSize: "13px", fontWeight: "600", color: "#cbd5e1" }}>
            {running ? "Autonomous Agent Running" : "OpportunityOS Core Ready"}
          </span>
        </div>

        <div
          style={{
            background: "#12192b",
            border: "1px solid #1e293b",
            padding: "6px 14px",
            borderRadius: "8px",
            fontSize: "12px",
            color: "#94a3b8",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <Sparkles size={14} color="#818cf8" />
          <span>
            Goal: <strong style={{ color: "#f8fafc" }}>{activeGoal || "Robotics & AI Internships in India (≥₹40,000/mo)"}</strong>
          </span>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
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
