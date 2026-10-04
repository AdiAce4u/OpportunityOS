from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
import uuid

portal_router = APIRouter(prefix="/portal", tags=["Career Portal"])

@portal_router.get("/apply/{external_id}", response_class=HTMLResponse)
async def get_apply_page(external_id: str):
    """
    Realistic Company Career Application Portal for Playwright Browser Automation.
    Contains standard ATS inputs (Name, Email, Phone, College, Why Role, Resume File).
    """
    company_name = external_id.replace("-", " ").title()
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Careers at {company_name} — Job Application</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 40px; margin: 0; }}
    .container {{ max-width: 650px; margin: auto; background: #131b2e; padding: 32px; border-radius: 12px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
    .badge {{ display: inline-block; background: #3b82f6; color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 12px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; color: #ffffff; }}
    p.subtitle {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; }}
    .form-group {{ margin-bottom: 18px; }}
    label {{ display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #cbd5e1; }}
    input[type="text"], input[type="email"], input[type="tel"], textarea {{
      width: 100%; box-sizing: border-box; background: #0a0f1d; border: 1px solid #334155; border-radius: 8px; color: #f8fafc; padding: 10px 14px; font-size: 14px;
    }}
    input:focus, textarea:focus {{ outline: none; border-color: #6366f1; }}
    textarea {{ resize: vertical; min-height: 80px; }}
    .file-drop {{ border: 2px dashed #334155; padding: 20px; border-radius: 8px; text-align: center; background: #0a0f1d; }}
    button[type="submit"] {{
      width: 100%; background: #4f46e5; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.2s;
    }}
    button[type="submit"]:hover {{ background: #4338ca; }}
    .footer {{ margin-top: 24px; font-size: 12px; color: #64748b; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">Official Application Portal</div>
    <h1>Apply for Position</h1>
    <p class="subtitle">Reference ID: <b>{external_id}</b> · Careers Portal</p>
    
    <form id="application-form" action="/portal/apply/{external_id}" method="POST" enctype="multipart/form-data">
      <div class="form-group">
        <label for="name">Full Legal Name *</label>
        <input type="text" id="name" name="name" placeholder="e.g. Aarav Sharma" required />
      </div>

      <div class="form-group">
        <label for="email">Email Address *</label>
        <input type="email" id="email" name="email" placeholder="e.g. aarav@example.com" required />
      </div>

      <div class="form-group">
        <label for="phone">Phone Number *</label>
        <input type="tel" id="phone" name="phone" placeholder="e.g. +91 9876543210" required />
      </div>

      <div class="form-group">
        <label for="college">University / College *</label>
        <input type="text" id="college" name="college" placeholder="e.g. IIT Kharagpur" required />
      </div>

      <div class="form-group">
        <label for="why_role">Why are you interested in this role? *</label>
        <textarea id="why_role" name="why_role" placeholder="Discuss relevant projects and motivations..." required></textarea>
      </div>

      <div class="form-group">
        <label for="resume">Upload Resume (PDF)</label>
        <div class="file-drop">
          <input type="file" id="resume" name="resume" accept=".pdf,.doc,.docx" />
        </div>
      </div>

      <button type="submit" id="submit-btn">Submit Application</button>
    </form>
    <div class="footer">Secure Portal · Protected by OpportunityOS Integration Layer</div>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)

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
    """
    Receives submitted form and returns an ATS confirmation page with confirmation ID.
    """
    confirmation_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Application Received — Success</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080c14; color: #f1f5f9; padding: 60px 20px; text-align: center; }}
    .card {{ max-width: 550px; margin: auto; background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1e293b; }}
    .icon {{ font-size: 48px; color: #10b981; margin-bottom: 16px; }}
    h1 {{ color: #ffffff; font-size: 26px; margin: 0 0 10px; }}
    p {{ color: #94a3b8; font-size: 15px; line-height: 1.5; }}
    .id-box {{ background: #1e293b; padding: 14px 20px; border-radius: 8px; font-family: monospace; font-size: 18px; color: #38bdf8; font-weight: 700; margin: 20px 0; border: 1px dashed #38bdf8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✓</div>
    <h1>Application Successfully Submitted!</h1>
    <p>Thank you, <b>{name}</b>. Your application for position <b>{external_id}</b> has been registered in our recruiting system.</p>
    <div id="confirmation-id" class="id-box" data-app-id="{confirmation_id}">{confirmation_id}</div>
    <p>A confirmation email has been dispatched to <b>{email}</b>. Our team will review your qualifications and reach out with updates.</p>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)
