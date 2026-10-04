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
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads and parses candidate PDF resume into structured fields."""
    content = await file.read()
    parsed = parse_resume_pdf(content)
    
    # Save file to uploads directory
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
        
    return {
        "filename": file.filename,
        "extracted_email": parsed.get("email"),
        "extracted_phone": parsed.get("phone"),
        "extracted_graduation_year": parsed.get("graduation_year"),
        "extracted_skills": parsed.get("skills", []),
        "resume_text": parsed.get("text", "")[:3000],
    }
