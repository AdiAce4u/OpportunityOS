import re
import hashlib
from typing import Any
from app.db.session import SessionLocal
from app.models import Job

def compute_job_hash(company: str, title: str, url: str = "") -> str:
    """Computes deterministic SHA-256 fingerprint for cross-platform duplicate prevention."""
    norm_comp = re.sub(r"[^a-z0-9]", "", (company or "").lower())
    norm_title = re.sub(r"[^a-z0-9]", "", (title or "").lower())
    base_url = (url or "").split("?")[0].rstrip("/")
    raw_sig = f"{norm_comp}|{norm_title}|{base_url}"
    return hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()

def read_job_page(url: str) -> dict[str, Any]:
    """Reads raw page content from URL."""
    # Find in DB or generate structured mockup
    db = SessionLocal()
    try:
        external_id = url.split("/")[-1] if "/" in url else url
        job = db.query(Job).filter(Job.external_id == external_id).first()
        if job:
            return {
                "title": job.title,
                "company": job.company,
                "raw_text": f"{job.title} at {job.company} - {job.location}\nSalary: {job.salary_text}\n{job.description}",
                "url": url,
            }
        return {"raw_text": f"Career opportunity at {url}", "url": url}
    finally:
        db.close()

def extract_job_information(job_dict_or_url: str | dict[str, Any]) -> dict[str, Any]:
    """
    Extracts normalized structured job information:
    title, company, location, salary, description, required_skills, preferred_skills, eligibility, deadline, url, application method.
    """
    if isinstance(job_dict_or_url, dict):
        return job_dict_or_url
    
    url = str(job_dict_or_url)
    db = SessionLocal()
    try:
        external_id = url.split("/")[-1] if "/" in url else url
        job = db.query(Job).filter(Job.external_id == external_id).first()
        if job:
            return {
                "external_id": job.external_id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "is_remote": job.is_remote,
                "salary_text": job.salary_text,
                "salary_min": job.salary_min,
                "description": job.description,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "eligibility": job.eligibility or {},
                "deadline": job.deadline,
                "url": job.url,
                "application_method": job.application_method,
                "required_documents": job.required_documents or ["resume"],
                "source": job.source,
                "company_research": job.company_research or {}
            }
        return {}
    finally:
        db.close()

def parse_custom_jd(jd_text: str, custom_title: str = "", custom_company: str = "") -> dict[str, Any]:
    """
    Parses unformatted, raw custom Job Description text into structured specifications:
    title, company, required_skills, preferred_skills, location, salary, eligibility.
    """
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
    
    # 1. Title inference
    title = custom_title.strip()
    if not title:
        for line in lines[:5]:
            match = re.search(r"(?:role|title|position):\s*(.+)", line, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                break
            if any(k in line.lower() for k in ["intern", "engineer", "developer", "scientist", "analyst", "architect"]):
                title = line.strip("#-* ")
                break
        if not title:
            title = lines[0][:60] if lines else "Custom Technical Opportunity"

    # 2. Company inference
    company = custom_company.strip()
    if not company:
        for line in lines[:8]:
            match = re.search(r"(?:company|organization|at)\s*[:\-]?\s*([A-Za-z0-9\s&]+)", line, re.IGNORECASE)
            if match and len(match.group(1).strip()) > 2:
                company = match.group(1).strip()
                break
        if not company:
            company = "Custom Employer"

    # 3. Location inference
    location = "Bangalore"
    loc_keywords = ["remote", "bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "delhi", "gurgaon", "noida", "india"]
    for loc in loc_keywords:
        if re.search(rf"\b{loc}\b", jd_text, re.IGNORECASE):
            location = loc.capitalize() if loc != "remote" else "Remote"
            break

    # 4. Salary/stipend inference
    salary_text = "Competitive / Market Standard"
    salary_min = None
    sal_match = re.search(r"(?:₹|rs\.?|inr)\s*([\d,]+)", jd_text, re.IGNORECASE)
    if sal_match:
        val = float(sal_match.group(1).replace(",", ""))
        salary_min = val
        salary_text = f"₹{val:,.0f}/month"

    # 5. Technical Skill Extraction
    KNOWN_TECH = [
        "Python", "C++", "C", "ROS2", "ROS", "Linux", "Git", "Docker", "Kubernetes",
        "PyTorch", "TensorFlow", "OpenCV", "Gazebo", "SLAM", "Navigation2", "Controls",
        "Machine Learning", "Deep Learning", "Computer Vision", "SQL", "FastAPI",
        "React", "TypeScript", "JavaScript", "Embedded Systems", "STM32", "FreeRTOS",
        "AWS", "GCP", "Azure", "TensorRT", "CUDA", "Robotics"
    ]
    
    found_skills = [s for s in KNOWN_TECH if re.search(rf"\b{re.escape(s)}\b", jd_text, re.IGNORECASE)]
    
    # Split into required vs preferred based on sections if present
    req_skills = []
    pref_skills = []
    
    is_preferred_section = False
    for line in lines:
        if any(h in line.lower() for h in ["preferred", "nice to have", "plus", "good to have"]):
            is_preferred_section = True
        elif any(h in line.lower() for h in ["requirement", "must have", "qualifications", "what you need"]):
            is_preferred_section = False
            
        line_skills = [s for s in found_skills if re.search(rf"\b{re.escape(s)}\b", line, re.IGNORECASE)]
        if is_preferred_section:
            pref_skills.extend(line_skills)
        else:
            req_skills.extend(line_skills)
            
    req_skills = list(dict.fromkeys(req_skills)) or found_skills[:4]
    pref_skills = [s for s in dict.fromkeys(pref_skills) if s not in req_skills]

    # 6. Eligibility (Graduation Year & Degree)
    grad_min = 2026
    grad_max = 2028
    grad_match = re.search(r"(202[4-9]|203[0-5])", jd_text)
    if grad_match:
        found_year = int(grad_match.group(1))
        grad_min = found_year - 1
        grad_max = found_year + 1

    import hashlib
    raw_sig = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}"
    hash_id = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()[:10]
    external_id = f"custom-jd-{hash_id}"

    return {
        "external_id": external_id,
        "title": title,
        "company": company,
        "location": location,
        "is_remote": "remote" in location.lower(),
        "salary_text": salary_text,
        "salary_min": salary_min,
        "description": jd_text[:2000],
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "education_requirements": ["B.Tech", "M.Tech", "Degree in CS / Robotics / Engineering"],
        "eligibility": {"graduation_year_min": grad_min, "graduation_year_max": grad_max},
        "url": f"http://localhost:8000/portal/apply/{external_id}",
        "application_method": "form",
        "source": "custom_jd_input"
    }

