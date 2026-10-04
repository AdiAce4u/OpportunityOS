import React, { useState, useEffect } from "react";
import {
  Upload,
  CheckCircle2,
  User,
  BookOpen,
  MapPin,
  DollarSign,
  ShieldCheck,
  Plus,
  X,
  FileText,
  Copy,
  Check,
  Edit3,
  Eye,
  Download,
  ExternalLink,
  Trash2,
  BookmarkCheck,
  Sparkles,
} from "lucide-react";
import { api } from "../services/api";

export function ProfileEditor({ profile, onSaveProfile }) {
  const [formData, setFormData] = useState(profile || {
    name: "Aarav Sharma",
    email: "aarav.sharma@example.com",
    phone: "+91 9876543210",
    graduation_year: 2027,
    degree: "B.Tech in Computer Science & Robotics",
    college: "IIT Kharagpur",
    cgpa: 8.92,
    skills: ["Python", "C++", "ROS2", "Machine Learning", "Robotics", "Controls", "Linux", "PyTorch"],
    projects: [
      {
        name: "Quadruped Robot Dynamic Locomotion",
        description: "12-DOF quadruped robot simulation with ROS2 and Gazebo.",
        tech_stack: ["ROS2", "C++", "Python", "Gazebo"],
      },
    ],
    preferred_roles: ["Robotics Intern", "Robotics Software Intern", "ML Intern"],
    preferred_locations: ["India", "Bangalore", "Hyderabad", "Remote"],
    minimum_salary: 40000,
    work_authorization: "Citizen of India, fully authorized to work in India",
    prefer_companies: ["XYZ Robotics", "ABC AI", "DEF Autonomy"],
    avoid_companies: [],
    resume_text: "",
    master_cv_markdown: "",
    resume_filename: "mastercv.pdf",
    master_cv_pdf_path: "uploads/mastercv.pdf",
    saved_tailored_cvs: [],
  });

  useEffect(() => {
    if (profile) {
      setFormData((prev) => ({
        ...prev,
        ...profile,
        resume_text: profile.resume_text || profile.master_cv_markdown || prev.resume_text || "",
        master_cv_markdown: profile.master_cv_markdown || profile.resume_text || prev.master_cv_markdown || "",
        resume_filename: profile.resume_filename || prev.resume_filename || "mastercv.pdf",
        master_cv_pdf_path: profile.master_cv_pdf_path || prev.master_cv_pdf_path || "uploads/mastercv.pdf",
        saved_tailored_cvs: profile.saved_tailored_cvs || prev.saved_tailored_cvs || [],
      }));
    }
  }, [profile]);

  const [newSkill, setNewSkill] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [copiedResume, setCopiedResume] = useState(false);
  const [viewFormat, setViewFormat] = useState("pdf"); // "pdf" | "text"
  const [selectedCvKey, setSelectedCvKey] = useState("master"); // "master" or cv.id / cv.filename

  const savedTailoredCvs = formData.saved_tailored_cvs || profile?.saved_tailored_cvs || [];

  // Determine active document
  let activePdfUrl = `http://localhost:8000/api/profiles/${formData.id || profile?.id || 1}/master-cv-pdf`;
  let activeFilename = formData.resume_filename || profile?.resume_filename || "mastercv.pdf";
  let activeTitle = "Master CV";
  let activeSubtitle = "Active Ground Truth Source";
  let isTailored = false;
  let activeTailoredCv = null;

  if (selectedCvKey !== "master") {
    const found = savedTailoredCvs.find((c) => c.id === selectedCvKey || c.filename === selectedCvKey);
    if (found) {
      activeTailoredCv = found;
      activePdfUrl = found.pdf_url.startsWith("http") ? found.pdf_url : `http://localhost:8000${found.pdf_url}`;
      activeFilename = found.filename;
      activeTitle = found.filename;
      activeSubtitle = `${found.company} • ${found.role}`;
      isTailored = true;
    }
  }

  const handleCopyResume = () => {
    const textToCopy = formData.resume_text || formData.master_cv_markdown || profile?.resume_text || profile?.master_cv_markdown || "";
    if (!textToCopy) return;
    navigator.clipboard.writeText(textToCopy);
    setCopiedResume(true);
    setTimeout(() => setCopiedResume(false), 2000);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg("Parsing resume and updating Master CV PDF...");
    try {
      const res = await api.uploadResume(file, formData?.id);
      if (res.profile) {
        setFormData(res.profile);
        if (onSaveProfile) {
          onSaveProfile(res.profile);
        }
      } else {
        const updated = {
          ...formData,
          name: res.extracted_name || formData.name,
          email: res.extracted_email || formData.email,
          phone: res.extracted_phone || formData.phone,
          college: res.extracted_college || formData.college,
          degree: res.extracted_degree || formData.degree,
          graduation_year: res.extracted_graduation_year || formData.graduation_year,
          cgpa: res.extracted_cgpa !== undefined && res.extracted_cgpa !== null ? res.extracted_cgpa : formData.cgpa,
          skills: Array.from(new Set([...(formData.skills || []), ...(res.extracted_skills || [])])),
          projects: res.extracted_projects?.length ? res.extracted_projects : formData.projects,
          experience: res.extracted_experience?.length ? res.extracted_experience : formData.experience,
          resume_filename: res.resume_filename || file.name,
          resume_text: res.resume_text || formData.resume_text,
          master_cv_markdown: res.master_cv_markdown || formData.master_cv_markdown,
          master_cv_pdf_path: res.master_cv_pdf_path || formData.master_cv_pdf_path,
          saved_tailored_cvs: res.saved_tailored_cvs || formData.saved_tailored_cvs || [],
        };
        setFormData(updated);
        if (onSaveProfile) {
          onSaveProfile(updated);
        }
      }
      setSelectedCvKey("master");
      setUploadMsg(`✓ Successfully uploaded ${file.name}! Master CV PDF is ready.`);
    } catch (err) {
      setUploadMsg(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteTailoredCV = async (cvId) => {
    if (!window.confirm("Remove this tailored CV from your profile vault?")) return;
    try {
      const res = await api.deleteSavedTailoredCV(formData.id || profile?.id || 1, cvId);
      setFormData((prev) => ({
        ...prev,
        saved_tailored_cvs: res.saved_tailored_cvs || [],
      }));
      setSelectedCvKey("master");
      if (onSaveProfile) {
        onSaveProfile({
          ...formData,
          saved_tailored_cvs: res.saved_tailored_cvs || [],
        });
      }
    } catch (e) {
      alert(`Could not remove CV: ${e.message}`);
    }
  };

  const addSkill = () => {
    if (!newSkill.trim()) return;
    if (!formData.skills.includes(newSkill.trim())) {
      setFormData({ ...formData, skills: [...formData.skills, newSkill.trim()] });
    }
    setNewSkill("");
  };

  const removeSkill = (skillToRemove) => {
    setFormData({ ...formData, skills: formData.skills.filter((s) => s !== skillToRemove) });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveProfile(formData);
  };

  const activeMasterResumeText =
    formData.resume_text || formData.master_cv_markdown || profile?.resume_text || profile?.master_cv_markdown || "";

  return (
    <div className="card" style={{ padding: "28px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px" }}>
        <div>
          <h3 style={{ fontSize: "20px", fontWeight: "800", color: "var(--text-primary)" }}>
            Candidate Profile
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
            The autonomous engine strictly relies on verified candidate credentials and your master resume.
          </p>
        </div>
      </div>

      {/* Compact PDF/Resume Upload Bar */}
      <div
        style={{
          border: "1px dashed var(--border-active)",
          background: "var(--bg-card-subtle)",
          borderRadius: "10px",
          padding: "12px 18px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
          flexWrap: "wrap",
          marginBottom: "20px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              background: "var(--primary-subtle)",
              display: "grid",
              placeItems: "center",
              color: "var(--primary)",
              flexShrink: 0,
            }}
          >
            <Upload size={18} />
          </div>
          <div>
            <div style={{ fontSize: "13.5px", fontWeight: "700", color: "var(--text-primary)" }}>
              Upload Resume (.pdf, .md, .txt)
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              Auto-extracts verified candidate facts and updates your Master CV PDF
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {uploadMsg && (
            <span
              style={{
                fontSize: "12px",
                color: uploadMsg.includes("✓") ? "var(--accent-emerald-text)" : "var(--accent-amber-text)",
                fontWeight: "600",
              }}
            >
              {uploadMsg}
            </span>
          )}
          <label className="btn btn-secondary" style={{ cursor: "pointer", display: "inline-flex", padding: "7px 14px", fontSize: "12.5px" }}>
            <Upload size={14} />
            <span>{uploading ? "Parsing..." : "Choose File"}</span>
            <input
              type="file"
              accept=".pdf,.md,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: "none" }}
            />
          </label>
        </div>
      </div>

      {/* PDF CV Vault Section: Master CV & Tailored CVs */}
      <div
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "12px",
          overflow: "hidden",
          marginBottom: "28px",
        }}
      >
        {/* CV Document Selector Bar */}
        <div
          style={{
            padding: "12px 18px",
            background: "var(--bg-card-subtle)",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <span style={{ fontSize: "13px", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Select CV:
            </span>

            {/* Master CV Tab */}
            <button
              type="button"
              onClick={() => setSelectedCvKey("master")}
              style={{
                padding: "6px 12px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: "700",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                border: selectedCvKey === "master" ? "1px solid var(--primary)" : "1px solid var(--border-subtle)",
                background: selectedCvKey === "master" ? "var(--primary-subtle)" : "var(--bg-card)",
                color: selectedCvKey === "master" ? "var(--primary-text)" : "var(--text-secondary)",
                boxShadow: selectedCvKey === "master" ? "0 2px 8px var(--primary-glow)" : "none",
                transition: "all 0.15s ease",
              }}
            >
              <FileText size={14} />
              <span>Master CV</span>
              <span
                style={{
                  fontSize: "10px",
                  background: "rgba(16, 185, 129, 0.15)",
                  color: "var(--accent-emerald-text)",
                  padding: "1px 5px",
                  borderRadius: "4px",
                  fontWeight: "700",
                }}
              >
                Ground Truth
              </span>
            </button>

            {/* Saved Tailored CVs */}
            {savedTailoredCvs.map((cv) => {
              const isSelected = selectedCvKey === cv.id || selectedCvKey === cv.filename;
              return (
                <button
                  key={cv.id || cv.filename}
                  type="button"
                  onClick={() => setSelectedCvKey(cv.id || cv.filename)}
                  style={{
                    padding: "6px 12px",
                    borderRadius: "8px",
                    fontSize: "12px",
                    fontWeight: "600",
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    border: isSelected ? "1px solid var(--accent-indigo-border)" : "1px solid var(--border-subtle)",
                    background: isSelected ? "var(--accent-indigo-subtle)" : "var(--bg-card)",
                    color: isSelected ? "var(--accent-indigo-text)" : "var(--text-secondary)",
                    boxShadow: isSelected ? "0 2px 8px rgba(99, 102, 241, 0.15)" : "none",
                    transition: "all 0.15s ease",
                  }}
                  title={`${cv.company} - ${cv.role}`}
                >
                  <Sparkles size={13} color="var(--primary)" />
                  <span style={{ maxWidth: "240px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {cv.filename}
                  </span>
                </button>
              );
            })}

            {savedTailoredCvs.length === 0 && (
              <span style={{ fontSize: "11.5px", color: "var(--text-muted)", fontStyle: "italic" }}>
                (Save tailored resumes during review to access them here)
              </span>
            )}
          </div>

          {/* Action buttons: Download & Fullscreen */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {selectedCvKey === "master" && (
              <div style={{ display: "flex", background: "var(--bg-card)", borderRadius: "6px", padding: "2px", border: "1px solid var(--border-subtle)", marginRight: "4px" }}>
                <button
                  type="button"
                  onClick={() => setViewFormat("pdf")}
                  style={{
                    padding: "4px 9px",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontWeight: "700",
                    border: "none",
                    cursor: "pointer",
                    background: viewFormat === "pdf" ? "var(--primary)" : "transparent",
                    color: viewFormat === "pdf" ? "#fff" : "var(--text-secondary)",
                  }}
                >
                  PDF
                </button>
                <button
                  type="button"
                  onClick={() => setViewFormat("text")}
                  style={{
                    padding: "4px 9px",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontWeight: "700",
                    border: "none",
                    cursor: "pointer",
                    background: viewFormat === "text" ? "var(--primary)" : "transparent",
                    color: viewFormat === "text" ? "#fff" : "var(--text-secondary)",
                  }}
                >
                  Text
                </button>
              </div>
            )}

            <a
              href={activePdfUrl}
              download={activeFilename}
              className="btn btn-primary"
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
              title={`Download ${activeFilename}`}
            >
              <Download size={13} />
              <span>Download PDF</span>
            </a>

            <a
              href={activePdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
              title="Open PDF in a new browser tab"
            >
              <ExternalLink size={13} />
              <span>Fullscreen</span>
            </a>

            {isTailored && activeTailoredCv && (
              <button
                type="button"
                onClick={() => handleDeleteTailoredCV(activeTailoredCv.id)}
                className="btn btn-secondary"
                style={{
                  padding: "6px 10px",
                  fontSize: "12px",
                  color: "var(--accent-rose-text)",
                  borderColor: "var(--accent-rose-border)",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                }}
                title="Remove this tailored CV"
              >
                <Trash2 size={13} />
                <span>Remove</span>
              </button>
            )}
          </div>
        </div>

        {/* Document Info Sub-bar */}
        <div
          style={{
            padding: "8px 18px",
            background: "var(--bg-card)",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontWeight: "700", color: "var(--text-primary)" }}>
              {activeTitle}
            </span>
            <span style={{ color: "var(--text-muted)" }}>•</span>
            <span style={{ color: "var(--text-secondary)" }}>
              {activeSubtitle}
            </span>
            {isTailored && (
              <span
                style={{
                  background: "var(--primary-subtle)",
                  color: "var(--primary-text)",
                  padding: "1px 6px",
                  borderRadius: "4px",
                  fontSize: "11px",
                  fontWeight: "700",
                }}
              >
                Tailored 1-Page ATS
              </span>
            )}
          </div>
        </div>

        {/* Viewer Content Area */}
        <div style={{ padding: "16px 18px", background: "var(--bg-well)" }}>
          {viewFormat === "pdf" ? (
            <div
              style={{
                width: "100%",
                height: "640px",
                borderRadius: "8px",
                overflow: "hidden",
                border: "1px solid var(--border-subtle)",
                background: "#525659",
                boxShadow: "var(--card-shadow)",
              }}
            >
              <iframe
                key={activePdfUrl}
                src={`${activePdfUrl}#toolbar=1&navpanes=0`}
                title={activeFilename}
                style={{
                  width: "100%",
                  height: "100%",
                  border: "none",
                  background: "#ffffff",
                }}
              />
            </div>
          ) : (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: "600" }}>
                  Raw Ground Truth Resume Content (Editable)
                </span>
                <button
                  type="button"
                  onClick={handleCopyResume}
                  className="btn btn-secondary"
                  style={{ padding: "4px 10px", fontSize: "11.5px" }}
                >
                  {copiedResume ? <Check size={12} color="var(--accent-emerald-text)" /> : <Copy size={12} />}
                  <span>{copiedResume ? "Copied!" : "Copy Text"}</span>
                </button>
              </div>
              <textarea
                className="input"
                rows={14}
                value={formData.resume_text || formData.master_cv_markdown || ""}
                placeholder="Paste or edit your Master Resume content here..."
                onChange={(e) => {
                  const val = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    resume_text: val,
                    master_cv_markdown: val,
                  }));
                }}
                style={{
                  width: "100%",
                  fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
                  fontSize: "12px",
                  lineHeight: "1.6",
                  resize: "vertical",
                }}
              />
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "8px" }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  {(formData.resume_text || formData.master_cv_markdown || "").length} characters • {(formData.resume_text || formData.master_cv_markdown || "").split("\n").length} lines
                </span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => onSaveProfile(formData)}
                  style={{ fontSize: "12px", padding: "6px 12px" }}
                >
                  <CheckCircle2 size={13} /> Save Master Resume Text
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Verified Candidate Facts Form */}
      <div style={{ marginBottom: "16px" }}>
        <h4 style={{ fontSize: "15px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "4px" }}>
          Verified Candidate Facts & Preferences
        </h4>
        <p style={{ fontSize: "12.5px", color: "var(--text-secondary)" }}>
          Parsed facts used by the matching engine and application generator.
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {/* Personal Details */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Full Name
            </label>
            <input
              type="text"
              className="input"
              value={formData.name || ""}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Email Address
            </label>
            <input
              type="email"
              className="input"
              value={formData.email || ""}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Contact Phone
            </label>
            <input
              type="text"
              className="input"
              value={formData.phone || ""}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Graduation Year
            </label>
            <input
              type="number"
              className="input"
              value={formData.graduation_year || 2027}
              onChange={(e) => setFormData({ ...formData, graduation_year: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Degree & Major
            </label>
            <input
              type="text"
              className="input"
              value={formData.degree || ""}
              onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              College / University
            </label>
            <input
              type="text"
              className="input"
              value={formData.college || ""}
              onChange={(e) => setFormData({ ...formData, college: e.target.value })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              CGPA / Score
            </label>
            <input
              type="number"
              step="0.01"
              className="input"
              value={formData.cgpa || 8.9}
              onChange={(e) => setFormData({ ...formData, cgpa: parseFloat(e.target.value) })}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Minimum Stipend / Salary (₹/month)
            </label>
            <input
              type="number"
              className="input"
              value={formData.minimum_salary || 40000}
              onChange={(e) => setFormData({ ...formData, minimum_salary: parseFloat(e.target.value) })}
            />
          </div>
        </div>

        {/* Work Authorization */}
        <div>
          <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
            Work Authorization Status
          </label>
          <input
            type="text"
            className="input"
            value={formData.work_authorization || "Eligible to work in India"}
            onChange={(e) => setFormData({ ...formData, work_authorization: e.target.value })}
          />
        </div>

        {/* Skills Tag Management */}
        <div>
          <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
            Verified Technical Skills ({formData.skills?.length || 0})
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "10px" }}>
            {(formData.skills || []).map((skill, idx) => (
              <span
                key={idx}
                style={{
                  background: "var(--bg-card-hover)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border-subtle)",
                  padding: "4px 10px",
                  borderRadius: "6px",
                  fontSize: "12.5px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <span>{skill}</span>
                <X size={12} style={{ cursor: "pointer", color: "var(--text-muted)" }} onClick={() => removeSkill(skill)} />
              </span>
            ))}
          </div>
          <div style={{ display: "flex", gap: "8px", maxWidth: "400px" }}>
            <input
              type="text"
              placeholder="Add skill (e.g. Navigation2)..."
              className="input"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addSkill(); } }}
            />
            <button type="button" className="btn btn-secondary" onClick={addSkill}>
              <Plus size={14} /> Add
            </button>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" style={{ alignSelf: "flex-start", marginTop: "10px" }}>
          <CheckCircle2 size={16} /> Save Profile
        </button>
      </form>
    </div>
  );
}
