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
        backgroundColor: "rgba(3, 7, 18, 0.8)",
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
          background: "#0c1324",
          border: "1px solid #1e293b",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.7)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "24px 28px",
            borderBottom: "1px solid #1e293b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            background: "#090f1d",
          }}
        >
          <div>
            <span className="badge badge-success" style={{ marginBottom: "6px" }}>
              INTERVIEW INVITATION DETECTED
            </span>
            <h2 style={{ fontSize: "20px", fontWeight: "800", color: "#ffffff" }}>
              Interview Copilot: {company}
            </h2>
            <div style={{ fontSize: "13px", color: "#94a3b8", marginTop: "2px" }}>
              Role: <strong style={{ color: "#cbd5e1" }}>{role}</strong>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "#64748b",
              cursor: "pointer",
            }}
          >
            <X size={22} />
          </button>
        </div>

        {/* Schedule Pill Banner */}
        <div
          style={{
            background: "#1e1b4b",
            borderBottom: "1px solid #312e81",
            padding: "14px 28px",
            display: "flex",
            alignItems: "center",
            gap: "24px",
            fontSize: "13px",
            color: "#c7d2fe",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Calendar size={16} color="#818cf8" />
            <span>Scheduled: <strong>{details.date || "Upcoming"}</strong></span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Video size={16} color="#818cf8" />
            <span>Round: <strong>{details.round || "Technical Discussion"}</strong></span>
          </div>
        </div>

        {/* Prep Content */}
        <div style={{ padding: "24px 28px", overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: "18px" }}>
          {/* Company Briefing */}
          <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "16px", borderRadius: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <BookOpen size={16} color="#818cf8" />
              <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff" }}>Company Architecture & Domain</h4>
            </div>
            <p style={{ fontSize: "13px", color: "#cbd5e1", lineHeight: "1.6" }}>
              {prepData?.company_briefing || `${company} specializes in high-reliability autonomous systems and robotics pipelines.`}
            </p>
          </div>

          {/* Recommended Talking Points */}
          <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "16px", borderRadius: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <CheckCircle size={16} color="#10b981" />
              <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff" }}>Tailored Talking Points (Based on Your Resume)</h4>
            </div>
            <ul style={{ paddingLeft: "18px", fontSize: "13px", color: "#cbd5e1", lineHeight: "1.6" }}>
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
          <div style={{ background: "#080c16", border: "1px solid #1a233a", padding: "16px", borderRadius: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <HelpCircle size={16} color="#f59e0b" />
              <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#ffffff" }}>Expected Technical Interview Questions</h4>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {(prepData?.probable_technical_questions || [
                "Explain the architectural differences between ROS2 nodes, executors, and lifecycle nodes.",
                "How do you address sensor noise and odometry drift when integrating IMU and wheel encoders?",
                "What strategies do you use for profiling and optimizing real-time C++ routines on embedded hardware?"
              ]).map((q, idx) => (
                <div key={idx} style={{ background: "#111827", padding: "10px 14px", borderRadius: "6px", fontSize: "12.5px", color: "#e2e8f0" }}>
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
            background: "#090f1d",
            borderTop: "1px solid #1e293b",
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
