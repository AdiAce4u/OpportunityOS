import React, { useState } from "react";
import {
  UserCheck,
  Bot,
  Search,
  FileSpreadsheet,
  ShieldCheck,
  Award,
  Building2,
  FileText,
  PenTool,
  CheckCircle2,
  Globe,
  Database,
  BellRing,
  LayoutDashboard,
  ArrowRight,
  Info,
} from "lucide-react";

export function AgentPipeline({ currentStage = "idle" }) {
  const [selectedStage, setSelectedStage] = useState(null);

  const stages = [
    {
      num: 1,
      id: "input",
      title: "1. User Input & Setup",
      agent: "User Profile Store",
      icon: <UserCheck size={18} />,
      color: "#3b82f6",
      summary: "Resume PDF, target roles, locations, minimum stipend requirements.",
      details: "Parses candidate resume, extracts skills & coursework, stores hard constraints into database.",
    },
    {
      num: 2,
      id: "supervisor",
      title: "2. Supervisor Agent",
      agent: "LangGraph Orchestrator",
      icon: <Bot size={18} />,
      color: "#8b5cf6",
      summary: "Converts user goal to structured search plan, controls loop limits.",
      details: "Formulates search strategy, sets role/location matrix, decides agent calling order and loop thresholds.",
    },
    {
      num: 3,
      id: "search",
      title: "3. Job Search Agent",
      agent: "Autonomous Search Loop",
      icon: <Search size={18} />,
      color: "#06b6d4",
      summary: "Generates multi-queries iteratively until opportunity quota met.",
      details: "Searches multiple sources (career pages, job boards, web), inspects count, and loops to generate new specialized queries.",
    },
    {
      num: 4,
      id: "extraction",
      title: "4. Job Info Extraction",
      agent: "Information Extractor",
      icon: <FileSpreadsheet size={18} />,
      color: "#10b981",
      summary: "Extracts normalized JD, skills, deadlines, and application links.",
      details: "Parses job specifications into structured records and stores in the job repository.",
    },
    {
      num: 5,
      id: "eligibility",
      title: "5. Eligibility & Filtering",
      agent: "Eligibility Agent",
      icon: <ShieldCheck size={18} />,
      color: "#f43f5e",
      summary: "Discards clearly ineligible opportunities with zero hallucination.",
      details: "Strictly checks graduation year, degree requirements, minimum experience, and work authorization floor.",
    },
    {
      num: 6,
      id: "matching",
      title: "6. Matching & Ranking",
      agent: "Fit & Scoring Agent",
      icon: <Award size={18} />,
      color: "#3b82f6",
      summary: "Calculates fit % and produces 'Why this job?' explanation.",
      details: "Evaluates skills, projects, coursework, location fit. Explains matched vs missing requirements.",
    },
    {
      num: 7,
      id: "research",
      title: "7. Company Research",
      agent: "Company Intelligence",
      icon: <Building2 size={18} />,
      color: "#a855f7",
      summary: "Researches domain, tech stack, size, and recent news.",
      details: "Inspects company background and engineering culture to provide context for tailored applications.",
    },
    {
      num: 8,
      id: "resume",
      title: "8. Resume Tailoring",
      agent: "Resume Agent",
      icon: <FileText size={18} />,
      color: "#10b981",
      summary: "Reorders and highlights truthful experience. Renders PDF.",
      details: "Strict rule: NEVER invent experience or skills. Reorganizes candidate's real facts to match target JD.",
    },
    {
      num: 9,
      id: "prep",
      title: "9. Application Prep",
      agent: "Application Agent",
      icon: <PenTool size={18} />,
      color: "#f59e0b",
      summary: "Generates cover letter, 'Why this role?' answers, checks missing info.",
      details: "Prepares tailored motivation statements. If critical info is missing, stops and prompts user.",
    },
    {
      num: 10,
      id: "review",
      title: "10. Human Review & Approval",
      agent: "Human-in-the-Loop Gate",
      icon: <CheckCircle2 size={18} />,
      color: "#06b6d4",
      summary: "Critical pause point. User reviews, edits, and explicitly approves.",
      details: "The agent will NEVER submit without explicit candidate authorization. Full preview of resume and answers.",
    },
    {
      num: 11,
      id: "browser",
      title: "11. Browser Automation",
      agent: "Playwright Agent",
      icon: <Globe size={18} />,
      color: "#ec4899",
      summary: "Fills form fields, uploads tailored resume, captures confirmation ID.",
      details: "Autonomously interacts with application forms, uploads documents, submits, and records confirmation proof.",
    },
    {
      num: 12,
      id: "tracker",
      title: "12. Application Tracker",
      agent: "Tracker Agent",
      icon: <Database size={18} />,
      color: "#10b981",
      summary: "Stores submission receipt and monitors status lifecycle.",
      details: "Tracks status from AWAITING_APPROVAL -> SUBMITTED -> UNDER_REVIEW -> INTERVIEW -> OFFER.",
    },
    {
      num: 13,
      id: "followup",
      title: "13. Follow-up & Reminders",
      agent: "Follow-up Agent",
      icon: <BellRing size={18} />,
      color: "#f59e0b",
      summary: "Automated follow-ups and application tracking.",
      details: "Tracks status updates, interview invitations, and drafts polite follow-up emails.",
    },
    {
      num: 14,
      id: "dashboard",
      title: "14. Dashboard & Analytics",
      agent: "OpportunityOS Hub",
      icon: <LayoutDashboard size={18} />,
      color: "#8b5cf6",
      summary: "Real-time metrics, live activity log, pipeline tracking.",
      details: "Unified control room showing all applications, top opportunities, and estimated hours saved.",
    },
  ];

  return (
    <div className="card" style={{ padding: "24px", marginBottom: "28px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px" }}>
        <div>
          <span className="badge badge-primary" style={{ marginBottom: "8px" }}>
            14-Stage Multi-Agent Architecture
          </span>
          <h3 style={{ fontSize: "18px", fontWeight: "700", color: "var(--text-primary)" }}>
            Autonomous End-to-End Agent Workflow
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
            User Goal → Autonomous Multi-Query Search → Hard Eligibility Filtering → Fit Ranking → Truthful Resume Tailoring → Human Approval Gate → Playwright Automation → Tracking
          </p>
        </div>
      </div>

      {/* Pipeline Grid of Nodes */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "12px",
        }}
      >
        {stages.map((stage) => {
          const isSelected = selectedStage?.id === stage.id;
          return (
            <div
              key={stage.id}
              onClick={() => setSelectedStage(stage)}
              style={{
                background: isSelected ? "var(--bg-card-hover)" : "var(--bg-card-subtle)",
                border: isSelected ? `1.5px solid ${stage.color}` : "1px solid var(--border-subtle)",
                borderRadius: "10px",
                padding: "14px",
                cursor: "pointer",
                transition: "all 0.18s ease",
                position: "relative",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
                <div
                  style={{
                    width: "32px",
                    height: "32px",
                    borderRadius: "8px",
                    background: `${stage.color}1a`,
                    color: stage.color,
                    display: "grid",
                    placeItems: "center",
                  }}
                >
                  {stage.icon}
                </div>
                <span
                  style={{
                    fontSize: "10.5px",
                    fontWeight: "700",
                    color: stage.color,
                    background: `${stage.color}15`,
                    padding: "2px 6px",
                    borderRadius: "4px",
                  }}
                >
                  Stage {stage.num}
                </span>
              </div>

              <div style={{ fontSize: "13px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "4px" }}>
                {stage.title.split(". ")[1]}
              </div>
              <div style={{ fontSize: "11px", color: "var(--primary-text)", fontWeight: "600", marginBottom: "6px" }}>
                {stage.agent}
              </div>
              <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                {stage.summary}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected stage details drawer */}
      {selectedStage && (
        <div
          style={{
            marginTop: "18px",
            padding: "16px 20px",
            background: "var(--bg-card-hover)",
            borderRadius: "10px",
            border: `1px solid ${selectedStage.color}40`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "10px",
                background: selectedStage.color,
                color: "#ffffff",
                display: "grid",
                placeItems: "center",
              }}
            >
              {selectedStage.icon}
            </div>
            <div>
              <div style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-primary)" }}>
                {selectedStage.title} · <span style={{ color: selectedStage.color }}>{selectedStage.agent}</span>
              </div>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
                {selectedStage.details}
              </div>
            </div>
          </div>
          <button className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => setSelectedStage(null)}>
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
