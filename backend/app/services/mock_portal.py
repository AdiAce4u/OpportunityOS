from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
import uuid

portal_router = APIRouter(prefix="/portal", tags=["Career Portal"])

APPLY_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Careers at __COMPANY_NAME__ — Candidate Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root[data-theme="dark"] {
      --bg-page: #070b14;
      --bg-surface: #0e1526;
      --bg-surface-elevated: #141e34;
      --border-subtle: #1e293b;
      --border-focus: #6366f1;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-faint: #64748b;
      --input-bg: #090e1a;
      --input-border: #26334d;
      --accent-primary: #6366f1;
      --accent-gradient: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
      --accent-gradient-hover: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
      --badge-bg: rgba(99, 102, 241, 0.15);
      --badge-border: rgba(99, 102, 241, 0.35);
      --badge-text: #a5b4fc;
      --card-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      --toggle-bg: #1e293b;
      --toggle-border: #334155;
      --toggle-text: #cbd5e1;
    }

    :root[data-theme="light"] {
      --bg-page: #f8fafc;
      --bg-surface: #ffffff;
      --bg-surface-elevated: #f1f5f9;
      --border-subtle: #e2e8f0;
      --border-focus: #4f46e5;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-faint: #94a3b8;
      --input-bg: #ffffff;
      --input-border: #cbd5e1;
      --accent-primary: #4f46e5;
      --accent-gradient: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
      --accent-gradient-hover: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%);
      --badge-bg: #eef2ff;
      --badge-border: #c7d2fe;
      --badge-text: #4338ca;
      --card-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.08);
      --toggle-bg: #ffffff;
      --toggle-border: #cbd5e1;
      --toggle-text: #334155;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.2s ease, border-color 0.2s ease, color 0.15s ease; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 32px 16px;
    }

    /* Top Utility Bar with Dark/Light Toggle in Top Right */
    .top-bar {
      width: min(720px, 100%);
      display: flex;
      justifyContent: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    .brand-pill {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-main);
    }
    .brand-logo {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      background: var(--accent-gradient);
      color: white;
      display: grid;
      place-items: center;
      font-weight: 800;
      font-size: 15px;
      box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
    }

    /* Dark/Light Mode Toggle Button in the Top Right Corner */
    .theme-toggle-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--toggle-bg);
      border: 1px solid var(--toggle-border);
      color: var(--toggle-text);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
      user-select: none;
    }
    .theme-toggle-btn:hover {
      border-color: var(--accent-primary);
      transform: translateY(-1px);
    }

    /* Main Container Card */
    .portal-card {
      width: min(720px, 100%);
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      box-shadow: var(--card-shadow);
      overflow: hidden;
    }

    .portal-header {
      padding: 32px 36px 24px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
    }
    .header-badges {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--badge-text);
    }
    .badge-verified {
      background: rgba(16, 185, 129, 0.15);
      border-color: rgba(16, 185, 129, 0.35);
      color: #10b981;
    }

    h1.role-title {
      font-size: 24px;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 6px;
      line-height: 1.25;
    }
    p.meta-subtitle {
      font-size: 13.5px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 12px;
    }

    /* Form Body */
    .portal-body {
      padding: 32px 36px;
    }

    .form-grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }
    @media (max-width: 600px) {
      .form-grid-2 { grid-template-columns: 1fr; }
      .portal-header, .portal-body { padding: 24px 20px; }
    }

    .form-group {
      margin-bottom: 20px;
    }
    label.field-label {
      display: block;
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 7px;
    }
    label.field-label span.req {
      color: #ef4444;
      margin-left: 2px;
    }
    span.field-hint {
      display: block;
      font-size: 12px;
      color: var(--text-faint);
      margin-top: 5px;
    }

    input.input-field, textarea.input-field {
      width: 100%;
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      border-radius: 9px;
      color: var(--text-main);
      padding: 11px 14px;
      font-size: 14px;
      font-family: inherit;
      outline: none;
    }
    input.input-field:focus, textarea.input-field:focus {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    textarea.input-field {
      resize: vertical;
      min-height: 100px;
      line-height: 1.5;
    }

    /* Resume Drop Zone */
    .resume-drop-box {
      border: 2px dashed var(--input-border);
      background: var(--input-bg);
      border-radius: 10px;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      position: relative;
    }
    .resume-drop-box:hover {
      border-color: var(--accent-primary);
    }
    .drop-icon {
      font-size: 32px;
      margin-bottom: 8px;
    }
    .drop-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 4px;
    }
    .drop-desc {
      font-size: 12px;
      color: var(--text-muted);
    }
    .file-input-hidden {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      opacity: 0;
      cursor: pointer;
    }
    .attached-file-pill {
      display: none;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-top: 12px;
      padding: 6px 14px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #10b981;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Submit Button */
    .submit-button {
      width: 100%;
      background: var(--accent-gradient);
      color: #ffffff;
      border: none;
      padding: 14px;
      border-radius: 10px;
      font-size: 15.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4);
      margin-top: 10px;
    }
    .submit-button:hover {
      background: var(--accent-gradient-hover);
      transform: translateY(-1px);
    }
    .submit-button:active {
      transform: translateY(0);
    }

    .portal-footer {
      padding: 20px 36px;
      border-top: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      display: flex;
      align-items: center;
      justifyContent: space-between;
      font-size: 12px;
      color: var(--text-faint);
    }
  </style>
</head>
<body>

  <!-- Top Utility Bar with Dark/Light Mode Toggle in the Top Right Corner -->
  <div class="top-bar">
    <div class="brand-pill">
      <div class="brand-logo">__COMPANY_INITIAL__</div>
      <span>__COMPANY_NAME__ Recruiting Portal</span>
    </div>

    <button type="button" id="theme-toggle" class="theme-toggle-btn" title="Switch Theme (Dark / Light)">
      <span id="theme-icon">☀️</span>
      <span id="theme-text">Light Mode</span>
    </button>
  </div>

  <!-- Main Application Card -->
  <div class="portal-card">
    <div class="portal-header">
      <div class="header-badges">
        <span class="badge">Official Application Portal</span>
        <span class="badge badge-verified">✓ Verified Opportunity</span>
        <span class="badge" style="font-family: 'JetBrains Mono', monospace;">REF: __EXTERNAL_ID__</span>
      </div>
      <h1 class="role-title">Submit Job Application</h1>
      <p class="meta-subtitle">
        <span>Target: <strong>__COMPANY_NAME__</strong></span>
        <span>•</span>
        <span>Autofilled & verified via OpportunityOS Integration Layer</span>
      </p>
    </div>

    <div class="portal-body">
      <form id="application-form" action="/portal/apply/__EXTERNAL_ID__" method="POST" enctype="multipart/form-data">
        
        <div class="form-grid-2">
          <div class="form-group">
            <label class="field-label" for="name">Full Legal Name <span class="req">*</span></label>
            <input class="input-field" type="text" id="name" name="name" placeholder="e.g. Aarav Sharma" required />
            <span class="field-hint">Matches your verified candidate credentials.</span>
          </div>

          <div class="form-group">
            <label class="field-label" for="email">Email Address <span class="req">*</span></label>
            <input class="input-field" type="email" id="email" name="email" placeholder="e.g. aarav@example.com" required />
            <span class="field-hint">Interview scheduling and confirmation sent here.</span>
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="field-label" for="phone">Phone Number <span class="req">*</span></label>
            <input class="input-field" type="tel" id="phone" name="phone" placeholder="e.g. +91 9876543210" required />
            <span class="field-hint">Include country code for direct contact.</span>
          </div>

          <div class="form-group">
            <label class="field-label" for="college">University / College <span class="req">*</span></label>
            <input class="input-field" type="text" id="college" name="college" placeholder="e.g. IIT Kharagpur" required />
            <span class="field-hint">Current or most recent educational institution.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="field-label" for="why_role">Why are you interested in this role? <span class="req">*</span></label>
          <textarea class="input-field" id="why_role" name="why_role" placeholder="Discuss relevant projects, technical interests, and alignment with company goals..." required></textarea>
          <span class="field-hint">Candidate evidence mapped directly to requirements.</span>
        </div>

        <div class="form-group">
          <label class="field-label" for="resume">Attached Resume (PDF) <span class="req">*</span></label>
          <div class="resume-drop-box" id="drop-box">
            <div class="drop-icon">📄</div>
            <div class="drop-title">Tailored Single-Page ATS Resume</div>
            <div class="drop-desc">PDF format, 0.4-inch margins, verified metrics attached by browser agent</div>
            <input class="file-input-hidden" type="file" id="resume" name="resume" accept=".pdf,.doc,.docx" />
            <div id="file-name-pill" class="attached-file-pill">
              <span>✓ Resume Attached:</span>
              <span id="file-name-text"></span>
            </div>
          </div>
        </div>

        <button type="submit" id="submit-btn" class="submit-button">
          <span>Submit Application to __COMPANY_NAME__</span>
          <span style="font-size: 17px;">→</span>
        </button>
      </form>
    </div>

    <div class="portal-footer">
      <span>🛡️ 256-bit Encrypted ATS Pipeline</span>
      <span>Protected by OpportunityOS Two-Stage Automation Gate</span>
    </div>
  </div>

  <script>
    // Theme Toggle Logic
    const toggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      try { localStorage.setItem('opportunity_portal_theme', theme); } catch(e) {}
      if (theme === 'dark') {
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light Mode';
      } else {
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark Mode';
      }
    }

    const savedTheme = (() => {
      try {
        return localStorage.getItem('opportunity_portal_theme') || 'dark';
      } catch(e) {
        return 'dark';
      }
    })();
    setTheme(savedTheme);

    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });

    // File Input Visual Feedback
    const fileInput = document.getElementById('resume');
    const filePill = document.getElementById('file-name-pill');
    const fileNameText = document.getElementById('file-name-text');

    function updateFileDisplay() {
      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileNameText.textContent = file.name;
        filePill.style.display = 'inline-flex';
      }
    }

    fileInput.addEventListener('change', updateFileDisplay);
    window.addEventListener('DOMContentLoaded', updateFileDisplay);
  </script>
</body>
</html>"""

CONFIRMATION_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Application Received — __COMPANY_NAME__</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root[data-theme="dark"] {
      --bg-page: #070b14;
      --bg-card: #0e1526;
      --border-color: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --id-bg: #141f36;
      --id-border: #3b82f6;
      --id-text: #38bdf8;
      --toggle-bg: #1e293b;
      --toggle-border: #334155;
      --toggle-text: #cbd5e1;
    }
    :root[data-theme="light"] {
      --bg-page: #f8fafc;
      --bg-card: #ffffff;
      --border-color: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #475569;
      --id-bg: #eff6ff;
      --id-border: #93c5fd;
      --id-text: #1d4ed8;
      --toggle-bg: #ffffff;
      --toggle-border: #cbd5e1;
      --toggle-text: #334155;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; transition: background 0.2s, color 0.2s; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justifyContent: center;
      padding: 30px 16px;
    }
    .top-bar {
      width: min(580px, 100%);
      display: flex;
      justifyContent: flex-end;
      margin-bottom: 16px;
    }
    .theme-toggle-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--toggle-bg);
      border: 1px solid var(--toggle-border);
      color: var(--toggle-text);
      padding: 7px 14px;
      border-radius: 20px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }
    .theme-toggle-btn:hover {
      border-color: #3b82f6;
    }
    .card {
      max-width: 580px;
      width: 100%;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 44px 36px;
      border-radius: 20px;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }
    .success-icon {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      background: rgba(16, 185, 129, 0.15);
      border: 2px solid #10b981;
      color: #10b981;
      font-size: 32px;
      display: grid;
      place-items: center;
      margin: 0 auto 20px;
    }
    h1 {
      font-size: 26px;
      font-weight: 800;
      margin-bottom: 10px;
      color: var(--text-main);
    }
    p.lead {
      font-size: 14.5px;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .id-container {
      background: var(--id-bg);
      border: 2px dashed var(--id-border);
      padding: 18px 24px;
      border-radius: 12px;
      margin-bottom: 24px;
    }
    .id-label {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    .id-code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 24px;
      font-weight: 800;
      color: var(--id-text);
      letter-spacing: 1.5px;
    }
    .copy-btn {
      margin-top: 10px;
      background: transparent;
      border: 1px solid var(--id-border);
      color: var(--id-text);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }
    .copy-btn:hover {
      background: rgba(59, 130, 246, 0.1);
    }
    .summary-box {
      text-align: left;
      background: rgba(0,0,0,0.15);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 20px;
      font-size: 13px;
      color: var(--text-muted);
    }
    .summary-row {
      display: flex;
      justifyContent: space-between;
      padding: 4px 0;
    }
    .summary-row strong {
      color: var(--text-main);
    }
  </style>
</head>
<body>

  <div class="top-bar">
    <button type="button" id="theme-toggle" class="theme-toggle-btn">
      <span id="theme-icon">☀️</span>
      <span id="theme-text">Light Mode</span>
    </button>
  </div>

  <div class="card">
    <div class="success-icon">✓</div>
    <h1>Application Submitted Successfully!</h1>
    <p class="lead">
      Thank you, <strong>__CANDIDATE_NAME__</strong>. Your candidate dossier has been received and registered by the <strong>__COMPANY_NAME__</strong> talent acquisition team.
    </p>

    <div class="id-container">
      <div class="id-label">Official ATS Confirmation Receipt</div>
      <div id="confirmation-id" class="id-code" data-app-id="__CONFIRMATION_ID__">__CONFIRMATION_ID__</div>
      <button type="button" class="copy-btn" onclick="navigator.clipboard.writeText('__CONFIRMATION_ID__'); this.textContent='✓ Copied!';">
        Copy Reference Code
      </button>
    </div>

    <div class="summary-box">
      <div class="summary-row"><span>Candidate:</span> <strong>__CANDIDATE_NAME__</strong></div>
      <div class="summary-row"><span>Email:</span> <strong>__CANDIDATE_EMAIL__</strong></div>
      <div class="summary-row"><span>Position Ref:</span> <strong>__EXTERNAL_ID__</strong></div>
      <div class="summary-row"><span>Status:</span> <strong style="color: #10b981;">REGISTERED & VERIFIED</strong></div>
    </div>

    <p style="font-size: 12.5px; color: var(--text-muted);">
      OpportunityOS has logged this submission receipt. You may now return to your OpportunityOS workspace or close this tab.
    </p>
  </div>

  <script>
    const toggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      try { localStorage.setItem('opportunity_portal_theme', theme); } catch(e) {}
      if (theme === 'dark') {
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light Mode';
      } else {
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark Mode';
      }
    }

    const savedTheme = (() => {
      try {
        return localStorage.getItem('opportunity_portal_theme') || 'dark';
      } catch(e) {
        return 'dark';
      }
    })();
    setTheme(savedTheme);

    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  </script>
</body>
</html>"""

@portal_router.get("/apply/{external_id}", response_class=HTMLResponse)
async def get_apply_page(external_id: str):
    company_name = external_id.replace("-", " ").title()
    company_initial = company_name[:1] if company_name else "C"
    html = (
        APPLY_PAGE_TEMPLATE
        .replace("__COMPANY_NAME__", company_name)
        .replace("__COMPANY_INITIAL__", company_initial)
        .replace("__EXTERNAL_ID__", external_id)
    )
    return HTMLResponse(content=html)

@portal_router.post("/apply/{external_id}", response_class=HTMLResponse)
async def post_apply_submission(
    external_id: str,
    name: str = Form("Candidate"),
    email: str = Form(""),
    phone: str = Form(""),
    college: str = Form(""),
    why_role: str = Form(""),
    resume: UploadFile = File(None)
):
    company_name = external_id.replace("-", " ").title()
    confirmation_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    html = (
        CONFIRMATION_PAGE_TEMPLATE
        .replace("__COMPANY_NAME__", company_name)
        .replace("__CANDIDATE_NAME__", name)
        .replace("__CANDIDATE_EMAIL__", email or "candidate@example.com")
        .replace("__EXTERNAL_ID__", external_id)
        .replace("__CONFIRMATION_ID__", confirmation_id)
    )
    return HTMLResponse(content=html)
