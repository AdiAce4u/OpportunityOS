import os
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import UserProfile
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.tools.cv_parser_engine import MasterCVParser
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
        profile = UserProfile(name=parsed["name"] or "Candidate")
        db.add(profile)
        db.flush()

    # Update profile fields
    if parsed.get("name"):
        profile.name = parsed["name"]
    if parsed.get("email"):
        profile.email = parsed["email"]
    if parsed.get("phone"):
        profile.phone = parsed["phone"]
    if parsed.get("college"):
        profile.college = parsed["college"]
    if parsed.get("degree"):
        profile.degree = parsed["degree"]
    if parsed.get("graduation_year"):
        profile.graduation_year = parsed["graduation_year"]
    if parsed.get("cgpa") is not None:
        profile.cgpa = parsed["cgpa"]

    # Merge skills
    existing_skills = list(profile.skills or [])
    for s in (parsed.get("skills") or []):
        if s not in existing_skills:
            existing_skills.append(s)
    profile.skills = existing_skills

    # Save categorized projects
    profile.projects = parsed.get("projects", [])
    profile.categorized_projects = parsed.get("projects", [])
    if parsed.get("experience"):
        profile.experience = parsed["experience"]

    profile.master_cv_markdown = text
    profile.resume_filename = filename
    profile.resume_text = text
    profile.parsed_data = parsed

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
