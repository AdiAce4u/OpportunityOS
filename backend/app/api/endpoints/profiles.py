import os
import io
import re
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import UserProfile, Application
from app.schemas.profile import ProfileCreate, ProfileResponse, SaveTailoredCVRequest
from app.tools.cv_parser_engine import MasterCVParser
from app.tools.resume_tailor_engine import ResumeTailorEngine
from app.core.config import settings
from pypdf import PdfReader

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("", response_model=list[ProfileResponse])
def get_all_profiles(db: Session = Depends(get_db)):
    profiles = db.query(UserProfile).all()
    return profiles

@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile

@router.post("", response_model=ProfileResponse)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    profile = UserProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: int, data: ProfileCreate, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    for key, value in data.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile

@router.post("/upload-master-cv")
async def upload_master_cv(
    file: UploadFile = File(...),
    profile_id: int | None = None,
    db: Session = Depends(get_db)
):
    """
    Uploads candidate Master CV (.md, .txt, .pdf) containing all projects across all domains
    (SDE, Data, Product, Consult, Core, Finance). Automatically parses and structures the projects vault.
    """
    content_bytes = await file.read()
    filename = file.filename or "master_cv.md"
    
    # Extract text content depending on file type
    if filename.lower().endswith(".pdf"):
        text = ""
        try:
            reader = PdfReader(io.BytesIO(content_bytes))
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception as e:
            text = content_bytes.decode("utf-8", errors="ignore")
    else:
        text = content_bytes.decode("utf-8", errors="ignore")

    # Parse with MasterCVParser
    parsed = MasterCVParser.parse_full_master_cv(text, filename=filename)

    # Enhance project classification via Gemini LLM
    try:
        from app.tools.gemini_tailor_agent import GeminiTailorAgent
        if parsed.get("projects"):
            parsed["projects"] = GeminiTailorAgent.classify_projects_with_llm(parsed["projects"])
    except Exception as ce:
        pass

    # Save raw file to uploads directory
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", filename)
    with open(file_path, "wb") as f:
        f.write(content_bytes)

    # Find or create UserProfile
    profile = None
    if profile_id:
        profile = db.get(UserProfile, profile_id)
    if not profile:
        profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(name=parsed.get("name") or "")
        db.add(profile)
        db.flush()

    # Update profile fields
    profile.name = parsed.get("name") or profile.name or ""
    profile.email = parsed.get("email") or profile.email or ""
    profile.phone = parsed.get("phone") or profile.phone or ""
    profile.college = parsed.get("college") or profile.college or ""
    profile.degree = parsed.get("degree") or profile.degree or ""
    profile.graduation_year = parsed.get("graduation_year")
    profile.cgpa = parsed.get("cgpa")

    # Set skills, projects, and experience directly from parsed Master CV
    profile.skills = parsed.get("skills") or []
    profile.projects = parsed.get("projects") or []
    profile.categorized_projects = parsed.get("projects") or []
    profile.experience = parsed.get("experience") or []

    profile.master_cv_markdown = text
    profile.resume_filename = filename
    profile.resume_text = text
    profile.parsed_data = parsed

    if filename.lower().endswith(".pdf"):
        profile.master_cv_pdf_path = file_path
    else:
        try:
            pdf_path = os.path.join("uploads", "mastercv.pdf")
            ResumeTailorEngine.generate_pdf(text, pdf_path)
            profile.master_cv_pdf_path = pdf_path
        except Exception:
            profile.master_cv_pdf_path = "uploads/mastercv.pdf"

    db.commit()
    db.refresh(profile)

    # Group projects by domain for response
    by_domain = {}
    for p in profile.projects:
        dom = p.get("domain", "general")
        by_domain.setdefault(dom, []).append(p)

    return {
        "status": "SUCCESS",
        "message": f"Master CV parsed successfully! {len(profile.projects)} projects categorized across domains.",
        "filename": filename,
        "extracted_name": profile.name,
        "extracted_college": profile.college,
        "extracted_degree": profile.degree,
        "extracted_graduation_year": profile.graduation_year,
        "extracted_cgpa": profile.cgpa,
        "total_projects": len(profile.projects),
        "domain_breakdown": {k: len(v) for k, v in by_domain.items()},
        "projects": profile.projects,
        "skills": profile.skills,
        "resume_filename": profile.resume_filename,
        "resume_text": profile.resume_text,
        "master_cv_markdown": profile.master_cv_markdown,
        "master_cv_pdf_path": profile.master_cv_pdf_path,
        "saved_tailored_cvs": profile.saved_tailored_cvs or [],
        "profile": {
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "college": profile.college,
            "degree": profile.degree,
            "graduation_year": profile.graduation_year,
            "cgpa": profile.cgpa,
            "skills": profile.skills or [],
            "projects": profile.projects or [],
            "categorized_projects": profile.categorized_projects or [],
            "experience": profile.experience or [],
            "preferred_roles": profile.preferred_roles or [],
            "preferred_locations": profile.preferred_locations or [],
            "minimum_salary": profile.minimum_salary,
            "work_authorization": profile.work_authorization,
            "resume_filename": profile.resume_filename,
            "resume_text": profile.resume_text,
            "master_cv_markdown": profile.master_cv_markdown,
            "master_cv_pdf_path": profile.master_cv_pdf_path,
            "saved_tailored_cvs": profile.saved_tailored_cvs or [],
        }
    }

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    profile_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Backwards compatible endpoint delegating to upload_master_cv."""
    return await upload_master_cv(file=file, profile_id=profile_id, db=db)

@router.get("/{profile_id}/master-cv-pdf")
def get_master_cv_pdf(profile_id: int, db: Session = Depends(get_db)):
    """
    Serves the candidate's Master CV as a PDF file with inline disposition for browser viewing.
    If the file does not exist, automatically generates it using candidate data.
    """
    profile = db.get(UserProfile, profile_id)
    if not profile:
        profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(404, "Candidate profile not found")

    os.makedirs("uploads", exist_ok=True)
    pdf_path = profile.master_cv_pdf_path

    if not pdf_path or not os.path.exists(pdf_path):
        if os.path.exists("uploads/mastercv.pdf"):
            pdf_path = "uploads/mastercv.pdf"
        elif profile.master_cv_markdown or profile.resume_text:
            pdf_path = "uploads/mastercv.pdf"
            ResumeTailorEngine.generate_pdf(profile.master_cv_markdown or profile.resume_text, pdf_path)
            profile.master_cv_pdf_path = pdf_path
            db.commit()

    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(404, "Master CV PDF file not found on server")

    filename = os.path.basename(pdf_path)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

@router.post("/{profile_id}/save-tailored-cv")
def save_tailored_cv(
    profile_id: int,
    req: SaveTailoredCVRequest,
    db: Session = Depends(get_db)
):
    """
    Saves a tailored CV to the candidate's profile.
    Naming follows the format: CV_{company}_{role}.pdf
    """
    profile = db.get(UserProfile, profile_id)
    if not profile:
        profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(404, "Candidate profile not found")

    os.makedirs("uploads", exist_ok=True)
    clean_company = re.sub(r'[^a-zA-Z0-9]+', '_', req.company.strip()).strip('_')
    clean_role = re.sub(r'[^a-zA-Z0-9]+', '_', req.role.strip()).strip('_')
    cv_filename = f"CV_{clean_company}_{clean_role}.pdf"
    target_path = os.path.join("uploads", cv_filename)

    # 1. Compile or copy PDF
    if req.resume_text and req.resume_text.strip():
        ResumeTailorEngine.generate_pdf(req.resume_text, target_path)
    elif req.application_id:
        app_rec = db.get(Application, req.application_id)
        if app_rec and app_rec.tailored_resume_pdf_path and os.path.exists(app_rec.tailored_resume_pdf_path):
            import shutil
            shutil.copy2(app_rec.tailored_resume_pdf_path, target_path)
        elif app_rec and app_rec.tailored_resume:
            ResumeTailorEngine.generate_pdf(app_rec.tailored_resume, target_path)
        else:
            ResumeTailorEngine.generate_pdf(profile.master_cv_markdown or "Tailored Resume", target_path)
    else:
        ResumeTailorEngine.generate_pdf(profile.master_cv_markdown or "Tailored Resume", target_path)

    # 2. Add or update entry in saved_tailored_cvs
    cvs = list(profile.saved_tailored_cvs or [])
    # Remove existing entry with same filename if present
    cvs = [c for c in cvs if c.get("filename") != cv_filename]

    cv_entry = {
        "id": str(uuid.uuid4())[:8],
        "company": req.company,
        "role": req.role,
        "filename": cv_filename,
        "pdf_url": f"{settings.app_host}/uploads/{cv_filename}",
        "created_at": datetime.utcnow().strftime("%b %d, %Y • %I:%M %p"),
        "application_id": req.application_id
    }
    cvs.insert(0, cv_entry)
    profile.saved_tailored_cvs = cvs
    db.commit()
    db.refresh(profile)

    return {
        "status": "SUCCESS",
        "message": f"Successfully saved {cv_filename} to Profile!",
        "filename": cv_filename,
        "cv": cv_entry,
        "saved_tailored_cvs": profile.saved_tailored_cvs
    }

@router.get("/{profile_id}/tailored-cvs")
def get_saved_tailored_cvs(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile.saved_tailored_cvs or []

@router.delete("/{profile_id}/tailored-cvs/{cv_id}")
def delete_saved_tailored_cv(profile_id: int, cv_id: str, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    cvs = list(profile.saved_tailored_cvs or [])
    cvs = [c for c in cvs if c.get("id") != cv_id and c.get("filename") != cv_id]
    profile.saved_tailored_cvs = cvs
    db.commit()
    db.refresh(profile)
    return {"status": "SUCCESS", "saved_tailored_cvs": profile.saved_tailored_cvs}

@router.get("/{profile_id}/projects")
def get_profile_projects(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    
    projects = profile.categorized_projects or profile.projects or []
    by_domain = {}
    for p in projects:
        dom = p.get("domain", "general")
        by_domain.setdefault(dom, []).append(p)

    return {
        "profile_id": profile.id,
        "candidate_name": profile.name,
        "total_projects": len(projects),
        "domains": by_domain,
        "all_projects": projects
    }

@router.post("/reset-all")
def reset_all_profiles(db: Session = Depends(get_db)):
    """
    Resets candidate profile and applications back to completely blank initial state
    before any master CV is uploaded.
    """
    db.query(Application).delete()
    profiles = db.query(UserProfile).all()
    for p in profiles:
        p.name = ""
        p.email = ""
        p.phone = ""
        p.graduation_year = None
        p.degree = ""
        p.college = ""
        p.cgpa = None
        p.skills = []
        p.projects = []
        p.categorized_projects = []
        p.experience = []
        p.master_cv_markdown = ""
        p.resume_filename = ""
        p.resume_text = ""
        p.master_cv_pdf_path = ""
        p.saved_tailored_cvs = []
        p.parsed_data = {}
    db.commit()
    return {"status": "SUCCESS", "message": "Profile and applications reset to blank initial state."}

@router.post("/reclassify-projects")
def reclassify_profile_projects(
    payload: dict = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    Re-runs LLM domain classification on candidate's master CV projects across domains:
    'sde', 'data', 'core', 'finance', 'consult'.
    """
    profile_id = payload.get("profile_id")
    profile = db.get(UserProfile, profile_id) if profile_id else db.query(UserProfile).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    projects = profile.categorized_projects or profile.projects or []
    if not projects and profile.master_cv_markdown:
        parsed = MasterCVParser.parse_full_master_cv(profile.master_cv_markdown)
        projects = parsed.get("projects") or []

    if not projects:
        return {"status": "SUCCESS", "message": "No projects found to classify.", "total_projects": 0, "projects": []}

    # 1. First run updated deterministic taxonomy
    for p in projects:
        full_text = f"{p.get('name', '')} {p.get('dates', '')}\n{p.get('description', '')}\n" + "\n".join(p.get('bullets', []))
        p['domain'] = MasterCVParser.infer_domain(full_text)

    # 2. Invoke Gemini LLM for AI project classification
    try:
        from app.tools.gemini_tailor_agent import GeminiTailorAgent
        projects = GeminiTailorAgent.classify_projects_with_llm(projects)
    except Exception as e:
        pass

    profile.projects = projects
    profile.categorized_projects = projects
    db.commit()
    db.refresh(profile)

    by_domain = {}
    for p in projects:
        dom = p.get("domain", "general")
        by_domain.setdefault(dom, []).append(p)

    return {
        "status": "SUCCESS",
        "message": f"Successfully classified {len(projects)} projects across domains with AI!",
        "total_projects": len(projects),
        "domain_breakdown": {k: len(v) for k, v in by_domain.items()},
        "projects": projects,
        "profile": {
            "id": profile.id,
            "name": profile.name,
            "skills": profile.skills,
            "projects": profile.projects,
            "categorized_projects": profile.categorized_projects,
            "experience": profile.experience,
        }
    }


