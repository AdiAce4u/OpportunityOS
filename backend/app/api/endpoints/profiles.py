import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import UserProfile
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.tools.resume_tools import parse_resume_pdf

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

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    profile_id: int | None = None,
    db: Session = Depends(get_db)
):
    """
    Uploads candidate CV / resume, parses structured metadata with AI extractor,
    and automatically updates the UserProfile record in the database.
    """
    content = await file.read()
    parsed = parse_resume_pdf(content)
    
    # Save file to uploads directory
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Find or create UserProfile
    profile = None
    if profile_id:
        profile = db.get(UserProfile, profile_id)
    if not profile:
        profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(name="Candidate")
        db.add(profile)
        db.flush()

    # Update profile fields from CV
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

    # Update projects if extracted
    if parsed.get("projects"):
        profile.projects = parsed["projects"]

    # Update experience if extracted
    if parsed.get("experience"):
        profile.experience = parsed["experience"]

    profile.resume_filename = file.filename
    profile.resume_text = parsed.get("text", "")
    profile.parsed_data = parsed
    
    db.commit()
    db.refresh(profile)

    return {
        "status": "SUCCESS",
        "message": f"Resume parsed and profile updated for {profile.name or 'candidate'}.",
        "filename": file.filename,
        "extracted_name": parsed.get("name"),
        "extracted_email": parsed.get("email"),
        "extracted_phone": parsed.get("phone"),
        "extracted_college": parsed.get("college"),
        "extracted_degree": parsed.get("degree"),
        "extracted_graduation_year": parsed.get("graduation_year"),
        "extracted_cgpa": parsed.get("cgpa"),
        "extracted_skills": parsed.get("skills", []),
        "extracted_projects": parsed.get("projects", []),
        "extracted_experience": parsed.get("experience", []),
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
            "experience": profile.experience or [],
            "preferred_roles": profile.preferred_roles or [],
            "preferred_locations": profile.preferred_locations or [],
            "minimum_salary": profile.minimum_salary,
            "work_authorization": profile.work_authorization,
            "prefer_companies": profile.prefer_companies or [],
            "avoid_companies": profile.avoid_companies or [],
        }
    }
