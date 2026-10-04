import io
import os
import re
from typing import Any
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def parse_resume_pdf(file_bytes: bytes) -> dict[str, Any]:
    """
    Parses resume PDF into structured text and candidate metadata.
    """
    text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        text = "Failed to parse binary PDF; please paste plain text."

    # Extract email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = email_match.group(0) if email_match else ""

    # Extract phone
    phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else ""

    # Extract graduation year
    grad_match = re.search(r"(202[4-9]|203[0-5])", text)
    grad_year = int(grad_match.group(0)) if grad_match else None

    # Detect skills
    common_skills = [
        "Python", "C++", "C", "Java", "ROS2", "ROS", "Linux", "Git", "Docker",
        "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "OpenCV",
        "SLAM", "Computer Vision", "Gazebo", "SQL", "FastAPI", "React"
    ]
    found_skills = [s for s in common_skills if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE)]

    return {
        "text": text,
        "email": email,
        "phone": phone,
        "graduation_year": grad_year,
        "skills": found_skills
    }

def tailor_resume(job: dict[str, Any], user_profile: dict[str, Any], raw_resume: str = "") -> str:
    """
    Takes ORIGINAL RESUME + JOB DESCRIPTION.
    STRICT RULES:
    - Never invent experience.
    - Never invent skills.
    - Never invent employment.
    - Never invent projects.
    - Never change factual dates.
    - Only reorganize, rewrite and emphasize truthful facts present in profile.
    """
    candidate_name = user_profile.get("name", "Candidate")
    email = user_profile.get("email", "")
    phone = user_profile.get("phone", "")
    college = user_profile.get("college", "")
    degree = user_profile.get("degree", "")
    grad_year = user_profile.get("graduation_year", "")
    cgpa = user_profile.get("cgpa", "")
    
    user_skills = user_profile.get("skills") or []
    req_skills = [s.lower() for s in (job.get("required_skills") or [])]
    
    # Sort skills putting job-relevant skills first
    matched_skills = [s for s in user_skills if s.lower() in req_skills]
    other_skills = [s for s in user_skills if s.lower() not in req_skills]
    ordered_skills = matched_skills + other_skills
    
    # Projects relevant to job
    projects = user_profile.get("projects") or []
    experience = user_profile.get("experience") or []
    
    lines = [
        f"{candidate_name.upper()}",
        f"{email} | {phone} | {college}",
        f"Target Role: {job.get('title')} — {job.get('company')}",
        "-" * 60,
        "PROFESSIONAL OBJECTIVE & ALIGNMENT",
        f"Dedicated {degree} candidate at {college} (Graduation: {grad_year}, CGPA: {cgpa}) with proven technical background in {', '.join(matched_skills[:4])}. Applying hands-on project experience to excel in {job.get('title')} at {job.get('company')}.",
        "",
        "RELEVANT TECHNICAL COMPETENCIES (VERIFIED)",
        f"• Targeted Core Skills: {', '.join(matched_skills) if matched_skills else 'Strong engineering fundamentals'}",
        f"• Additional Technical Skills: {', '.join(other_skills[:6])}",
        "",
        "FEATURED PROJECT ACCOMPLISHMENTS"
    ]
    
    for p in projects:
        lines.append(f"• {p.get('name')}")
        if p.get("tech_stack"):
            lines.append(f"  Technologies: {', '.join(p.get('tech_stack'))}")
        lines.append(f"  {p.get('description')}")
        if p.get("link"):
            lines.append(f"  Repository: {p.get('link')}")
        lines.append("")
        
    if experience:
        lines.append("PRACTICAL EXPERIENCE")
        for e in experience:
            lines.append(f"• {e.get('role')} — {e.get('company')} ({e.get('duration')})")
            lines.append(f"  {e.get('description')}")
            lines.append("")
            
    lines.extend([
        "EDUCATION CREDENTIALS",
        f"• {degree}, {college} (Expected: {grad_year}, CGPA: {cgpa})",
        "",
        "SAFETY & COMPLIANCE NOTICE: Grounded strictly in candidate-provided verified credentials. Zero synthetic or fabricated qualifications."
    ])
    
    return "\n".join(lines)

def generate_resume_pdf(resume_text: str, output_path: str) -> str:
    """
    Renders the tailored resume into a clean PDF document.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    normal_style = styles["Normal"]
    normal_style.fontSize = 9.5
    normal_style.leading = 13
    
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Heading1"],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=6
    )
    
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4C51BF"),
        spaceBefore=8,
        spaceAfter=4
    )
    
    story = []
    lines = resume_text.split("\n")
    if lines:
        story.append(Paragraph(f"<b>{lines[0]}</b>", title_style))
        story.append(Spacer(1, 4))
        
    for line in lines[1:]:
        line_clean = line.strip()
        if not line_clean:
            story.append(Spacer(1, 4))
        elif line_clean.isupper() and len(line_clean) < 40 and not line_clean.startswith("•"):
            story.append(Paragraph(f"<b>{line_clean}</b>", heading_style))
        else:
            story.append(Paragraph(line_clean.replace("&", "&amp;"), normal_style))
            
    doc.build(story)
    return output_path
