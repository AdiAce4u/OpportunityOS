import React from "react";
import { X, Calendar, Video, BookOpen, MessageSquare, HelpCircle, CheckCircle } from "lucide-react";

export function InterviewPrepModal({ event, prepData, onClose }) {
  if (!event) return null;

  const details = event.interview_details || {};
  const company = event.company || "Company";
  const role = event.role || "Role";

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "var(--modal-overlay)",
        backdropFilter: "blur(8px)",
        display: "grid",
        placeItems: "center",
        zIndex: 100,
        padding: "20px",
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: "min(800px, 100%)",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          borderRadius: "16px",
          background: "var(--bg-card)",
          border: "1px solid var(--border-subtle)",
          boxShadow: "var(--card-shadow-hover)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "24px 28px",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            background: "var(--bg-card)",
          }}
        >
          <div>
            <span className="badge badge-success" style={{ marginBottom: "6px" }}>
              INTERVIEW INVITATION DETECTED
            </span>
            <h2 style={{ fontSize: "20px", fontWeight: "800", color: "var(--text-primary)" }}>
              Interview Copilot: {company}
            </h2>
            <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>
              Role: <strong style={{ color: "var(--text-primary)" }}>{role}</strong>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
            }}
          >
            <X size={22} />
          </button>
        </div>

        {/* Schedule Pill Banner */}
        <div
          style={{
            background: "var(--banner-interview-bg)",
            borderBottom: "1px solid var(--banner-interview-border)",
            padding: "14px 28px",
            display: "flex",
            alignItems: "center",
            gap: "24px",
            fontSize: "13px",
            color: "var(--banner-interview-title)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Calendar size={16} color="var(--primary)" />
            <span>Scheduled: <strong>{details.date || "Upcoming"}</strong></span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Video size={16} color="var(--primary)" />
            <span>Round: <strong>{details.round || "Technical Discussion"}</strong></span>
          </div>
        </div>

        {/* Prep Content */}
        <div style={{ padding: "24px 28px", overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: "18px" }}>
          {/* Company Briefing */}
          <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "16px", borderRadius: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <BookOpen size={16} color="var(--primary)" />
              <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>Company Architecture & Domain</h4>
            </div>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
              {prepData?.company_briefing || `${company} specializes in high-reliability autonomous systems and robotics pipelines.`}
            </p>
          </div>

          {/* Recommended Talking Points */}
          <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "16px", borderRadius: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <CheckCircle size={16} color="var(--accent-emerald)" />
              <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>Tailored Talking Points (Based on Your Resume)</h4>
            </div>
            <ul style={{ paddingLeft: "18px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
              {(prepData?.recommended_talking_points || [
                "Highlight your dynamic quadruped locomotion controllers and low-latency ROS2 nodes.",
                "Discuss LiDAR Cartographer SLAM tuning and Nav2 costmap parameter configuration.",
                "Emphasize practical C++ memory safety and ROS2 inter-process communication."
              ]).map((point, idx) => (
                <li key={idx} style={{ marginBottom: "6px" }}>{point}</li>
              ))}
            </ul>
          </div>

          {/* Probable Technical Questions */}
          <div style={{ background: "var(--bg-card-subtle)", border: "1px solid var(--border-subtle)", padding: "16px", borderRadius: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <HelpCircle size={16} color="var(--accent-amber)" />
              <h4 style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>Expected Technical Interview Questions</h4>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {(prepData?.probable_technical_questions || [
                "Explain the architectural differences between ROS2 nodes, executors, and lifecycle nodes.",
                "How do you address sensor noise and odometry drift when integrating IMU and wheel encoders?",
                "What strategies do you use for profiling and optimizing real-time C++ routines on embedded hardware?"
              ]).map((q, idx) => (
                <div key={idx} style={{ background: "var(--bg-card-hover)", border: "1px solid var(--border-subtle)", padding: "10px 14px", borderRadius: "6px", fontSize: "12.5px", color: "var(--text-primary)" }}>
                  <strong>Q{idx + 1}:</strong> {q}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "16px 28px",
            background: "var(--bg-card)",
            borderTop: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <button className="btn btn-primary" onClick={onClose}>
            Done & Ready
          </button>
        </div>
      </div>
    </div>
  );
}
