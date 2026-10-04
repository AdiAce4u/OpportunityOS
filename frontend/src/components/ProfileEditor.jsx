import React, { useState, useEffect } from "react";
import { Upload, CheckCircle2, User, BookOpen, MapPin, DollarSign, ShieldCheck, Plus, X } from "lucide-react";
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
  });

  useEffect(() => {
    if (profile) {
      setFormData(profile);
    }
  }, [profile]);

  const [newSkill, setNewSkill] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg("Parsing PDF resume with AI extractor...");
    try {
      const res = await api.uploadResume(file, formData?.id);
      if (res.profile) {
        setFormData(res.profile);
        if (onSaveProfile) {
          onSaveProfile(res.profile);
        }
      } else {
        setFormData((prev) => ({
          ...prev,
          name: res.extracted_name || prev.name,
          email: res.extracted_email || prev.email,
          phone: res.extracted_phone || prev.phone,
          college: res.extracted_college || prev.college,
          degree: res.extracted_degree || prev.degree,
          graduation_year: res.extracted_graduation_year || prev.graduation_year,
          cgpa: res.extracted_cgpa !== undefined && res.extracted_cgpa !== null ? res.extracted_cgpa : prev.cgpa,
          skills: Array.from(new Set([...(prev.skills || []), ...(res.extracted_skills || [])])),
          projects: res.extracted_projects?.length ? res.extracted_projects : prev.projects,
          experience: res.extracted_experience?.length ? res.extracted_experience : prev.experience,
        }));
      }
      setUploadMsg(`✓ Successfully parsed ${file.name}! Profile details and database updated.`);
    } catch (err) {
      setUploadMsg(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
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

  return (
    <div className="card" style={{ padding: "28px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
        <div>
          <h3 style={{ fontSize: "18px", fontWeight: "800", color: "var(--text-primary)" }}>
            Candidate Profile & Ground Truth
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
            The autonomous agent only relies on verified facts entered here. Zero synthetic claims will be generated.
          </p>
        </div>
      </div>

      {/* PDF Upload Box */}
      <div
        style={{
          border: "2px dashed var(--border-hover)",
          background: "var(--bg-card-subtle)",
          borderRadius: "12px",
          padding: "24px",
          textAlign: "center",
          marginBottom: "28px",
        }}
      >
        <Upload size={32} color="var(--primary)" style={{ margin: "0 auto 10px" }} />
        <h4 style={{ fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>Upload Resume PDF</h4>
        <p style={{ fontSize: "12.5px", color: "var(--text-muted)", margin: "4px 0 14px" }}>
          PDF will be parsed into structured skills, coursework, and verified dates.
        </p>
        <label className="btn btn-secondary" style={{ cursor: "pointer", display: "inline-flex" }}>
          <span>Choose PDF File</span>
          <input type="file" accept=".pdf" onChange={handleFileUpload} style={{ display: "none" }} />
        </label>
        {uploadMsg && (
          <div style={{ fontSize: "12px", color: uploadMsg.includes("✓") ? "var(--accent-emerald-text)" : "var(--accent-amber-text)", marginTop: "10px" }}>
            {uploadMsg}
          </div>
        )}
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
          <CheckCircle2 size={16} /> Save Profile & Ground Truth
        </button>
      </form>
    </div>
  );
}
