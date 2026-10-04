import React, { useRef, useEffect } from "react";
import { Terminal, Check, AlertTriangle, Info, Bot } from "lucide-react";

export function AgentActivityLog({ logs = [], running = false }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="card" style={{ padding: "20px", display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Terminal size={18} color="#818cf8" />
          <h3 style={{ fontSize: "15px", fontWeight: "700", color: "#f8fafc" }}>Agent Activity Log</h3>
        </div>
        {running && (
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981" }} className="pulse-indicator" />
            <span style={{ fontSize: "11px", color: "#10b981", fontWeight: "600" }}>Live Streaming</span>
          </div>
        )}
      </div>

      <div
        ref={scrollRef}
        style={{
          flex: 1,
          maxHeight: "360px",
          minHeight: "260px",
          overflowY: "auto",
          background: "#080c16",
          border: "1px solid #1a233a",
          borderRadius: "8px",
          padding: "12px",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: "12px",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        {logs.length === 0 ? (
          <div style={{ color: "#64748b", margin: "auto", textAlign: "center", padding: "24px" }}>
            <Bot size={28} color="#334155" style={{ margin: "0 auto 8px" }} />
            <p>Click "Start Autonomous Agent" to begin discovery & application preparation.</p>
          </div>
        ) : (
          logs.map((log, index) => {
            const isWarn = log.level === "WARNING";
            const stage = log.stage || "Agent";
            return (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "10px",
                  lineHeight: "1.5",
                  color: isWarn ? "#fbbf24" : "#e2e8f0",
                  paddingBottom: "4px",
                  borderBottom: "1px solid #111a2e",
                }}
              >
                <span style={{ color: "#64748b", flexShrink: 0, fontSize: "11px" }}>
                  {log.timestamp || "14:31:02"}
                </span>

                <span
                  style={{
                    background: isWarn ? "#f59e0b22" : "#6366f122",
                    color: isWarn ? "#fbbf24" : "#818cf8",
                    padding: "1px 6px",
                    borderRadius: "4px",
                    fontSize: "10.5px",
                    fontWeight: "600",
                    flexShrink: 0,
                  }}
                >
                  {stage}
                </span>

                <div style={{ flex: 1 }}>
                  <span>{log.message}</span>
                  {log.metadata && Object.keys(log.metadata).length > 0 && (
                    <div style={{ color: "#94a3b8", fontSize: "11px", marginTop: "2px" }}>
                      {JSON.stringify(log.metadata)}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
