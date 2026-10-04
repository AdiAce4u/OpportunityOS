import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import { api } from "./services/api";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { StatsOverview } from "./components/StatsOverview";
import { AgentPipeline } from "./components/AgentPipeline";
import { AgentActivityLog } from "./components/AgentActivityLog";
import { TopOpportunities } from "./components/TopOpportunities";
import { ApplicationReviewModal } from "./components/ApplicationReviewModal";
import { ApplicationsTable } from "./components/ApplicationsTable";
import { ProfileEditor } from "./components/ProfileEditor";
import { InterviewPrepModal } from "./components/InterviewPrepModal";
import { CustomJDModal } from "./components/CustomJDModal";

import {
  Sparkles,
  Bot,
  Play,
  Calendar,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Zap,
} from "lucide-react";

function OpportunityOSApp() {
  const [currentTab, setTab] = useState("dashboard");
  const [running, setRunning] = useState(false);
  const [metrics, setMetrics] = useState({});
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [profile, setProfile] = useState(null);
  const [logs, setLogs] = useState([]);
  const [trackerEvents, setTrackerEvents] = useState([]);

  // Modals
  const [selectedApp, setSelectedApp] = useState(null);
  const [interviewEvent, setInterviewEvent] = useState(null);
  const [interviewPrep, setInterviewPrep] = useState(null);
  const [isCustomJDOpen, setIsCustomJDOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 4500);
  };

  const loadData = async () => {
    try {
      const [dashData, appsData, jobsData, profilesData, eventsData] = await Promise.all([
        api.getDashboardMetrics(),
        api.getApplications(),
        api.getJobs(),
        api.getProfiles(),
        api.getTrackerEvents(),
      ]);

      setMetrics(dashData);
      setApplications(appsData);
      setJobs(jobsData);
      if (profilesData && profilesData.length > 0) {
        setProfile(profilesData[0]);
      }
      setTrackerEvents(eventsData);
    } catch (err) {
      console.error("Failed to load initial platform data:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunAgent = async () => {
    setRunning(true);
    setLogs([
      {
        timestamp: new Date().toLocaleTimeString(),
        stage: "Supervisor",
        message: "🧠 Supervisor Agent awakened. Evaluating profile & setting autonomous search targets...",
        level: "INFO",
      },
    ]);

    try {
      let profileId = profile?.id;
      if (!profileId) {
        const profiles = await api.getProfiles();
        if (profiles.length > 0) {
          profileId = profiles[0].id;
          setProfile(profiles[0]);
        }
      }

      const res = await api.runAgent(profileId, {
        roles: profile?.preferred_roles || ["Robotics Intern", "Robotics Software Intern", "ML Intern"],
        locations: profile?.preferred_locations || ["India", "Bangalore", "Hyderabad", "Remote"],
        skills: profile?.skills || ["Python", "C++", "ROS2", "Machine Learning"],
        minimum_salary: profile?.minimum_salary || 40000,
        target_count: 15,
      });

      if (res.logs) {
        setLogs(res.logs);
      }

      await loadData();

      // If application package is ready, prompt Human Approval modal!
      if (res.application_id) {
        const appDetails = await api.getApplication(res.application_id);
        setSelectedApp(appDetails);
        showToast("Application Package Ready! Awaiting your Human-in-the-Loop approval.");
      }
    } catch (err) {
      console.error("Agent run error:", err);
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toLocaleTimeString(),
          stage: "Supervisor",
          message: `Execution issue: ${err.message}`,
          level: "WARNING",
        },
      ]);
    } finally {
      setRunning(false);
    }
  };

  const handleStopAgent = async () => {
    try {
      await api.stopAgent();
      setRunning(false);
      showToast("Emergency kill switch activated. Agent halted safely.");
    } catch (e) {}
  };

  const handleOpenApplication = async (appId) => {
    try {
      const details = await api.getApplication(appId);
      setSelectedApp(details);
    } catch (err) {
      console.error("Failed to load application details:", err);
    }
  };

  const handleApprove = async (appId, approvalPayload) => {
    try {
      const res = await api.approveApplication(appId, approvalPayload);
      setSelectedApp(null);
      await loadData();
      showToast(`✓ Application approved & submitted! Reference: ${res.external_application_id}`);
    } catch (err) {
      alert(`Approval error: ${err.message}`);
    }
  };

  const handleReject = async (appId) => {
    try {
      await api.approveApplication(appId, { approve: false });
      setSelectedApp(null);
      await loadData();
      showToast("Application rejected and archived.");
    } catch (err) {
      alert(`Reject error: ${err.message}`);
    }
  };

  const handleProvideMissingInfo = async (appId, answers) => {
    try {
      await api.provideMissingInfo(appId, answers);
      const updated = await api.getApplication(appId);
      setSelectedApp(updated);
      showToast("Missing information recorded successfully!");
    } catch (err) {
      alert(`Update error: ${err.message}`);
    }
  };

  const handleOpenInterviewPrep = async (event) => {
    setInterviewEvent(event);
    try {
      const prep = await api.getInterviewPrep(event.application_id);
      setInterviewPrep(prep);
    } catch (e) {
      setInterviewPrep(null);
    }
  };

  const handleSaveProfile = async (updatedData) => {
    try {
      if (profile?.id) {
        const res = await api.updateProfile(profile.id, updatedData);
        setProfile(res);
        showToast("Profile credentials updated successfully.");
      }
    } catch (err) {
      alert(`Failed to save profile: ${err.message}`);
    }
  };

  const awaitingCount = applications.filter((a) => a.status === "AWAITING_APPROVAL").length;
  const interviewEvents = trackerEvents.filter((e) => e.event_type === "INTERVIEW_INVITATION");

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            background: "#1e1b4b",
            border: "1px solid #4338ca",
            color: "#e0e7ff",
            padding: "14px 20px",
            borderRadius: "10px",
            zIndex: 200,
            boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
            fontSize: "13.5px",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <Sparkles size={16} color="#818cf8" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setTab={setTab}
        awaitingCount={awaitingCount}
        interviewCount={interviewEvents.length}
      />

      {/* Main Content */}
      <main className="main-content">
        <Navbar
          running={running}
          onRunAgent={handleRunAgent}
          onStopAgent={handleStopAgent}
          onRefresh={loadData}
          onOpenCustomJD={() => setIsCustomJDOpen(true)}
          activeGoal="Robotics or AI Internships in India (≥₹40,000/mo)"
        />

        <div className="page-body">
          {/* Active Interview Banner if invitations detected */}
          {interviewEvents.length > 0 && (
            <div
              style={{
                background: "linear-gradient(90deg, #1e1b4b 0%, #172554 100%)",
                border: "1px solid #3b82f6",
                borderRadius: "12px",
                padding: "16px 24px",
                marginBottom: "24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "16px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                <div
                  style={{
                    width: "40px",
                    height: "40px",
                    borderRadius: "10px",
                    background: "#2563eb",
                    color: "white",
                    display: "grid",
                    placeItems: "center",
                  }}
                >
                  <Calendar size={20} />
                </div>
                <div>
                  <h4 style={{ fontSize: "14.5px", fontWeight: "700", color: "#ffffff" }}>
                    {interviewEvents[0].company} invited you to an interview for {interviewEvents[0].role}!
                  </h4>
                  <p style={{ fontSize: "12.5px", color: "#93c5fd", marginTop: "2px" }}>
                    Follow-up Agent detected an interview invitation: {interviewEvents[0].interview_details?.date || "Scheduled this week"}.
                  </p>
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={() => handleOpenInterviewPrep(interviewEvents[0])}
                style={{ background: "#2563eb", whiteSpace: "nowrap" }}
              >
                <span>[PREPARE INTERVIEW]</span>
              </button>
            </div>
          )}

          {/* TAB: DASHBOARD */}
          {currentTab === "dashboard" && (
            <div>
              {/* Header Hero */}
              <div style={{ marginBottom: "24px" }}>
                <p style={{ fontSize: "12px", fontWeight: "700", color: "#818cf8", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                  Autonomous Agentic Job Application Platform
                </p>
                <h1 style={{ fontSize: "32px", fontWeight: "800", color: "#ffffff", margin: "4px 0 8px" }}>
                  Opportunity<span style={{ color: "#818cf8" }}>OS</span> Engine
                </h1>
                <p style={{ fontSize: "14px", color: "#94a3b8" }}>
                  Autonomously discovers opportunities, verifies eligibility, tailors your resume, prepares answers, pauses for your approval, and executes browser applications.
                </p>
              </div>

              {/* Stats Overview */}
              <StatsOverview metrics={metrics} />

              {/* 14-Stage Visual Workflow */}
              <AgentPipeline />

              {/* Split Grid: Top Opportunities & Real-Time Agent Activity Log */}
              <div className="split-grid">
                <TopOpportunities
                  jobs={applications.length > 0 ? applications : jobs}
                  onOpenCustomJD={() => setIsCustomJDOpen(true)}
                  onOpenReview={(job) => {
                    const matchedApp = applications.find((a) => a.job_id === job.id || a.title === job.title);
                    if (matchedApp) {
                      handleOpenApplication(matchedApp.id);
                    } else {
                      handleRunAgent();
                    }
                  }}
                />

                <AgentActivityLog logs={logs} running={running} />
              </div>

              {/* Applications Table */}
              <div style={{ marginTop: "28px" }}>
                <ApplicationsTable
                  applications={applications}
                  onOpenApplication={handleOpenApplication}
                />
              </div>
            </div>
          )}

          {/* TAB: PIPELINE */}
          {currentTab === "pipeline" && (
            <div>
              <div style={{ marginBottom: "24px" }}>
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "#ffffff" }}>
                  Agentic Multi-Agent Pipeline
                </h2>
                <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "4px" }}>
                  LangGraph workflow orchestration connecting the 9 specialized agents.
                </p>
              </div>
              <AgentPipeline />
              <div style={{ marginTop: "24px" }}>
                <AgentActivityLog logs={logs} running={running} />
              </div>
            </div>
          )}

          {/* TAB: APPLICATIONS */}
          {currentTab === "applications" && (
            <div>
              <div style={{ marginBottom: "24px" }}>
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "#ffffff" }}>
                  Applications & Review Center
                </h2>
                <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "4px" }}>
                  Review prepared packages, inspect tailored resumes, and authorize browser automation.
                </p>
              </div>
              <ApplicationsTable
                applications={applications}
                onOpenApplication={handleOpenApplication}
              />
            </div>
          )}

          {/* TAB: OPPORTUNITIES */}
          {currentTab === "opportunities" && (
            <div>
              <div style={{ marginBottom: "24px" }}>
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "#ffffff" }}>
                  Discovered Opportunities Repository
                </h2>
                <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "4px" }}>
                  Raw and normalized job listings discovered across company career pages and job boards.
                </p>
              </div>
              <TopOpportunities
                jobs={jobs}
                onOpenCustomJD={() => setIsCustomJDOpen(true)}
                onSelectJob={(job) => {
                  const matched = applications.find((a) => a.job_id === job.id);
                  if (matched) handleOpenApplication(matched.id);
                  else handleRunAgent();
                }}
              />
            </div>
          )}

          {/* TAB: PROFILE */}
          {currentTab === "profile" && (
            <div>
              <ProfileEditor profile={profile} onSaveProfile={handleSaveProfile} />
            </div>
          )}

          {/* TAB: INTERVIEW */}
          {currentTab === "interview" && (
            <div>
              <div style={{ marginBottom: "24px" }}>
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "#ffffff" }}>
                  Interview Copilot & Follow-ups
                </h2>
                <p style={{ fontSize: "14px", color: "#94a3b8", marginTop: "4px" }}>
                  Detected invitations, automated reminders, and company research briefings.
                </p>
              </div>

              {interviewEvents.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  {interviewEvents.map((evt) => (
                    <div
                      key={evt.id}
                      className="card"
                      style={{
                        padding: "20px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div>
                        <span className="badge badge-success" style={{ marginBottom: "6px" }}>
                          INVITATION VERIFIED
                        </span>
                        <h4 style={{ fontSize: "16px", fontWeight: "700", color: "#ffffff" }}>
                          {evt.company} — {evt.role}
                        </h4>
                        <p style={{ fontSize: "13px", color: "#94a3b8", marginTop: "4px" }}>
                          {evt.subject} · {evt.interview_details?.date}
                        </p>
                      </div>

                      <button
                        className="btn btn-primary"
                        onClick={() => handleOpenInterviewPrep(evt)}
                      >
                        [PREPARE INTERVIEW]
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card" style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
                  No interview invitations detected yet. The Follow-up agent continuously monitors application portals.
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Human Review Modal */}
      {selectedApp && (
        <ApplicationReviewModal
          application={selectedApp}
          onClose={() => setSelectedApp(null)}
          onApprove={handleApprove}
          onReject={handleReject}
          onProvideMissingInfo={handleProvideMissingInfo}
        />
      )}

      {/* Interview Prep Modal */}
      {interviewEvent && (
        <InterviewPrepModal
          event={interviewEvent}
          prepData={interviewPrep}
          onClose={() => setInterviewEvent(null)}
        />
      )}

      {/* Custom JD Analyzer Modal */}
      <CustomJDModal
        isOpen={isCustomJDOpen}
        onClose={() => setIsCustomJDOpen(false)}
        profileId={profile?.id}
        onJobCreated={async (result) => {
          await loadData();
          showToast(`Custom JD "${result.job?.title}" parsed & analyzed successfully!`);
        }}
      />
    </div>
  );
}

createRoot(document.getElementById("root")).render(<OpportunityOSApp />);
