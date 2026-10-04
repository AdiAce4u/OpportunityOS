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
import { MasterCVVault } from "./components/MasterCVVault";
import { PortalJobDiscovery } from "./components/PortalJobDiscovery";

import {
  Sparkles,
  Bot,
  Play,
  Calendar,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Zap,
  Globe,
  FolderGit2,
  Award,
} from "lucide-react";

function OpportunityOSApp() {
  const [currentTab, setTab] = useState("dashboard"); // "dashboard" | "master_cv" | "portal_discovery" | "applications" | "opportunities" | "pipeline" | "profile" | "interview"
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
  const [activeGoal, setActiveGoal] = useState("Robotics or AI Internships in India (≥₹40,000/mo)");
  const [toastMessage, setToastMessage] = useState("");

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 5000);
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
      console.error("Failed to load platform data:", err);
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
        message: "🧠 Supervisor Agent awakened. Evaluating multi-domain master CV & executing targeted portal searches...",
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

      const res = await api.runAgent(
        profileId,
        {
          roles: profile?.preferred_roles || ["Software Development Engineer", "Machine Learning Engineer", "Robotics Software Intern"],
          locations: profile?.preferred_locations || ["India", "Bangalore", "Hyderabad", "Remote"],
          skills: profile?.skills || ["Python", "C++", "PyTorch", "FastAPI"],
          minimum_salary: profile?.minimum_salary || 40000,
          target_count: 15,
        },
        activeGoal
      );

      if (res.logs) {
        setLogs(res.logs);
      }

      await loadData();

      if (res.application_id) {
        const appDetails = await api.getApplication(res.application_id);
        setSelectedApp(appDetails);
        showToast("🎯 1-Page ATS CV & Application Package Ready! Awaiting your Human Approval.");
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

  const handleTailorJobFromAnywhere = async (job) => {
    try {
      showToast(`Generating 1-Page ATS CV for ${job.title} at ${job.company}...`);
      const res = await api.tailorForJob(job.id, profile?.id);
      if (res.application_id) {
        const appDetails = await api.getApplication(res.application_id);
        setSelectedApp(appDetails);
        await loadData();
        showToast(`✓ ATS CV Ready for ${job.company}! Review and grant permission to apply.`);
      }
    } catch (err) {
      alert(`Tailoring error: ${err.message}`);
    }
  };

  const handleApprove = async (appId, approvalPayload) => {
    try {
      const res = await api.approveApplication(appId, approvalPayload);
      setSelectedApp(null);
      await loadData();
      showToast(`✓ Application approved & submitted! Reference: ${res.external_application_id || "APP-PORTAL-SUBMITTED"}`);
    } catch (err) {
      alert(`Approval error: ${err.message}`);
    }
  };

  const handleReject = async (appId) => {
    try {
      await api.approveApplication(appId, { approve: false });
      setSelectedApp(null);
      await loadData();
      showToast("Application archived.");
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
  const projectsCount = (profile?.categorized_projects || profile?.projects || []).length;

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            background: "var(--bg-card)",
            border: "1px solid var(--border-active)",
            color: "var(--text-primary)",
            padding: "14px 20px",
            borderRadius: "10px",
            zIndex: 200,
            boxShadow: "var(--card-shadow-hover)",
            fontSize: "13.5px",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <Sparkles size={16} color="var(--primary)" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setTab={setTab}
        awaitingCount={awaitingCount}
        interviewCount={interviewEvents.length}
        projectsCount={projectsCount}
      />

      {/* Main Content */}
      <main className="main-content">
        <Navbar
          running={running}
          onRunAgent={handleRunAgent}
          onStopAgent={handleStopAgent}
          onRefresh={loadData}
          onOpenCustomJD={() => setIsCustomJDOpen(true)}
          activeGoal={activeGoal}
          onUpdateGoal={(newGoal) => {
            setActiveGoal(newGoal);
            showToast(`Autonomous target goal updated: "${newGoal}"`);
          }}
        />

        <div className="page-body">
          {/* Active Interview Banner if invitations detected */}
          {interviewEvents.length > 0 && (
            <div
              style={{
                background: "var(--banner-interview-bg)",
                border: "1px solid var(--banner-interview-border)",
                borderRadius: "12px",
                padding: "16px 24px",
                marginBottom: "24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "16px",
                boxShadow: "var(--card-shadow)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                <div
                  style={{
                    width: "40px",
                    height: "40px",
                    borderRadius: "10px",
                    background: "var(--primary)",
                    color: "white",
                    display: "grid",
                    placeItems: "center",
                  }}
                >
                  <Calendar size={20} />
                </div>
                <div>
                  <h4 style={{ fontSize: "15px", fontWeight: "700", color: "var(--banner-interview-title)" }}>
                    {interviewEvents[0].company} invited you to an interview for {interviewEvents[0].role}!
                  </h4>
                  <p style={{ fontSize: "12.5px", color: "var(--banner-interview-sub)", marginTop: "2px", fontWeight: "500" }}>
                    Follow-up Agent detected an interview invitation: {interviewEvents[0].interview_details?.date || "Scheduled this week"}.
                  </p>
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={() => handleOpenInterviewPrep(interviewEvents[0])}
                style={{ whiteSpace: "nowrap" }}
              >
                <span>[PREPARE INTERVIEW]</span>
              </button>
            </div>
          )}

          {/* TAB: DASHBOARD */}
          {currentTab === "dashboard" && (
            <div>
              {/* Header Hero */}
              <div style={{ marginBottom: "24px", display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
                <div>
                  <p style={{ fontSize: "12px", fontWeight: "700", color: "var(--primary)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                    Autonomous Multi-Portal Discovery & ATS Tailoring Engine
                  </p>
                  <h1 style={{ fontSize: "30px", fontWeight: "800", color: "var(--text-primary)", margin: "4px 0 8px" }}>
                    Opportunity<span style={{ color: "var(--primary)" }}>OS</span> Dashboard
                  </h1>
                  <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                    Upload your master CV with multi-domain projects, discover roles across LinkedIn, Wellfound & Indeed, generate 1-page ATS resumes, and review before applying.
                  </p>
                </div>

                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setTab("master_cv")}
                    style={{ fontSize: "13px" }}
                  >
                    <FolderGit2 size={16} />
                    <span>Master CV Vault ({projectsCount})</span>
                  </button>

                  <button
                    className="btn btn-primary"
                    onClick={() => setTab("portal_discovery")}
                    style={{ fontSize: "13px" }}
                  >
                    <Globe size={16} />
                    <span>Live Portal Search</span>
                  </button>
                </div>
              </div>

              {/* Stats Overview */}
              <StatsOverview metrics={metrics} />

              {/* 14-Stage Visual Workflow */}
              <AgentPipeline />

              {/* Split Grid: Top Opportunities & Real-Time Agent Activity Log */}
              <div className="split-grid">
                <TopOpportunities
                  jobs={applications.length > 0 ? applications : jobs}
                  maxItems={4}
                  onOpenCustomJD={() => setIsCustomJDOpen(true)}
                  onSelectJob={(job) => handleTailorJobFromAnywhere(job)}
                  onOpenReview={(job) => {
                    const matchedApp = applications.find((a) => a.job_id === job.id || a.title === job.title);
                    if (matchedApp) {
                      handleOpenApplication(matchedApp.id);
                    } else {
                      handleTailorJobFromAnywhere(job);
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

          {/* TAB: MASTER CV & PROJECTS VAULT */}
          {currentTab === "master_cv" && (
            <MasterCVVault
              profile={profile}
              onProfileUpdated={(updated) => {
                setProfile(updated);
                loadData();
              }}
              onNavigateToSearch={() => setTab("portal_discovery")}
            />
          )}

          {/* TAB: JOB DISCOVERY ENGINE (Merged job-search-agent) */}
          {currentTab === "portal_discovery" && (
            <PortalJobDiscovery
              profile={profile}
              onOpenReviewModal={(app) => {
                setSelectedApp(app);
                loadData();
              }}
              onTailorAndApply={(job) => handleTailorJobFromAnywhere(job)}
            />
          )}

          {/* TAB: APPLICATIONS */}
          {currentTab === "applications" && (
            <div>
              <div style={{ marginBottom: "24px" }}>
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "var(--text-primary)" }}>
                  Applications & Review Center
                </h2>
                <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Review prepared 1-page ATS resumes, inspect project match citations, and authorize browser automation.
                </p>
              </div>
              <ApplicationsTable
                applications={applications}
                onOpenApplication={handleOpenApplication}
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
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "var(--text-primary)" }}>
                  Interview Copilot & Follow-ups
                </h2>
                <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
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
                        <h4 style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)" }}>
                          {evt.company} — {evt.role}
                        </h4>
                        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
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
                <div className="card" style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
                  No interview invitations detected yet. The Follow-up agent continuously monitors application portals.
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Human Review & Permission Modal */}
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
          if (result.job_id) {
            handleTailorJobFromAnywhere({ id: result.job_id, title: result.job?.title, company: result.job?.company });
          }
        }}
      />
    </div>
  );
}

createRoot(document.getElementById("root")).render(<OpportunityOSApp />);
