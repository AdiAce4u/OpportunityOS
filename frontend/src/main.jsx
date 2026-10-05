import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import { api } from "./services/api";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { StatsOverview } from "./components/StatsOverview";
import { TopOpportunities } from "./components/TopOpportunities";
import { ApplicationReviewModal } from "./components/ApplicationReviewModal";
import { ApplicationsTable } from "./components/ApplicationsTable";
import { ProfileEditor } from "./components/ProfileEditor";
import { CustomJDModal } from "./components/CustomJDModal";
import { MasterCVVault } from "./components/MasterCVVault";
import { PortalJobDiscovery } from "./components/PortalJobDiscovery";

import {
  Sparkles,
  Bot,
  Play,
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

  const handleOpenApplication = async (appIdOrJobId) => {
    try {
      if (typeof appIdOrJobId === "string" && appIdOrJobId.startsWith("job-")) {
        const jId = parseInt(appIdOrJobId.replace("job-", ""));
        await api.markJobBrowsed(jId).catch(() => {});
        const j = jobs.find((jobItem) => jobItem.id === jId) || { id: jId, title: "Target Opportunity", company: "Company" };
        handleTailorJobFromAnywhere(j);
        return;
      }
      try {
        const details = await api.getApplication(appIdOrJobId);
        setSelectedApp(details);
        if (details.job_id) {
          api.markJobBrowsed(details.job_id).catch(() => {});
        }
      } catch (appErr) {
        // Fallback: check if appIdOrJobId matches an existing application by job_id
        const existingApp = applications.find((a) => a.job_id === appIdOrJobId && typeof a.id === "number");
        if (existingApp) {
          const details = await api.getApplication(existingApp.id);
          setSelectedApp(details);
        } else {
          // If it's a job ID without an application, tailor it on demand
          const matchedJob = jobs.find((j) => j.id === appIdOrJobId);
          if (matchedJob) {
            await handleTailorJobFromAnywhere(matchedJob);
            return;
          }
          throw appErr;
        }
      }
      await loadData();
    } catch (err) {
      console.error("Failed to load application details:", err);
    }
  };

  const handleToggleWishlist = async (opportunity) => {
    try {
      const jobId = opportunity.job_id || opportunity.id;
      const isAppRecord = typeof opportunity.id === "number" && !opportunity.site;

      // Optimistic UI update across applications, jobs, and modal
      setApplications((prev) =>
        prev.map((a) => {
          if (a.id === opportunity.id || (jobId && a.job_id === jobId)) {
            return { ...a, is_wishlisted: !a.is_wishlisted };
          }
          return a;
        })
      );

      setJobs((prev) =>
        prev.map((j) => {
          if (j.id === jobId) {
            return { ...j, is_wishlisted: !j.is_wishlisted };
          }
          return j;
        })
      );

      if (selectedApp && (selectedApp.id === opportunity.id || selectedApp.job_id === jobId)) {
        setSelectedApp((prev) => (prev ? { ...prev, is_wishlisted: !prev.is_wishlisted } : null));
      }

      // Backend sync
      if (isAppRecord) {
        await api.toggleApplicationWishlist(opportunity.id);
      } else if (typeof opportunity.id === "string" && opportunity.id.startsWith("job-")) {
        await api.toggleApplicationWishlist(opportunity.id);
      } else if (jobId) {
        await api.toggleJobWishlist(jobId);
      }

      // Refresh applications to ensure wishlist pipeline reflects latest state
      const updatedApps = await api.getApplications();
      setApplications(updatedApps);
    } catch (err) {
      console.error("Failed to toggle wishlist:", err);
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

              {/* Top Opportunities Ranked by Fit */}
              <div style={{ marginTop: "24px" }}>
                <TopOpportunities
                  jobs={applications.length > 0 ? applications : jobs}
                  maxItems={6}
                  onOpenCustomJD={() => setIsCustomJDOpen(true)}
                  onSelectJob={(job) => handleTailorJobFromAnywhere(job)}
                  onToggleWishlist={handleToggleWishlist}
                  onOpenReview={(job) => {
                    const matchedApp = applications.find((a) => a.job_id === job.id || a.title === job.title);
                    if (matchedApp) {
                      handleOpenApplication(matchedApp.id);
                    } else {
                      handleTailorJobFromAnywhere(job);
                    }
                  }}
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
              onToggleWishlist={handleToggleWishlist}
            />
          )}

          {/* TAB: APPLICATIONS */}
          {currentTab === "applications" && (
            <div>
              <div style={{ marginBottom: "24px" }}>
                <h2 style={{ fontSize: "24px", fontWeight: "800", color: "var(--text-primary)" }}>
                  Applications & Review Center
                </h2>
              </div>
              <ApplicationsTable
                applications={applications}
                onOpenApplication={handleOpenApplication}
                onToggleWishlist={handleToggleWishlist}
              />
            </div>
          )}

          {/* TAB: PROFILE */}
          {currentTab === "profile" && (
            <div>
              <ProfileEditor profile={profile} onSaveProfile={handleSaveProfile} />
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
          onProfileUpdated={loadData}
          onToggleWishlist={handleToggleWishlist}
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
