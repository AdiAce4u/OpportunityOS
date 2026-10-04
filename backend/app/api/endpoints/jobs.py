from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Job, UserProfile
from app.schemas.job import JobSchema, CustomJDAnalysisRequest
from app.tools.search_tools import search_job_source
from app.tools.extraction_tools import parse_custom_jd
from app.tools.matching_tools import calculate_job_match, check_eligibility

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=list[JobSchema])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@router.get("/{job_id}", response_model=JobSchema)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@router.get("/search/preview")
def preview_search(q: str = Query("robotics intern", description="Search query")):
    return search_job_source(q)

@router.post("/analyze-custom-jd")
def analyze_custom_jd(request: CustomJDAnalysisRequest, db: Session = Depends(get_db)):
    """
    On-Demand Custom JD Analyzer:
    Parses arbitrary JD text, checks eligibility, and computes 1-to-1 evidence citations
    against the candidate profile without running a web search.
    """
    if not request.jd_text.strip():
        raise HTTPException(400, "Job description text cannot be empty.")
        
    profile = db.get(UserProfile, request.profile_id) if request.profile_id else db.query(UserProfile).first()
    if not profile:
        raise HTTPException(404, "No candidate profile found. Please create a profile first.")

    profile_dict = {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "graduation_year": profile.graduation_year,
        "degree": profile.degree,
        "college": profile.college,
        "skills": profile.skills or [],
        "projects": profile.projects or [],
        "experience": profile.experience or [],
        "preferred_locations": profile.preferred_locations or [],
        "minimum_salary": profile.minimum_salary,
        "work_authorization": profile.work_authorization,
    }

    parsed_job = parse_custom_jd(request.jd_text, request.title, request.company)
    
    # Run eligibility check
    is_eligible, eligibility_reason = check_eligibility(parsed_job, profile_dict)
    
    # Run matching & evidence-based citation table
    match_result = calculate_job_match(parsed_job, profile_dict)
    
    # Save or update parsed job with duplicate prevention
    existing_job = db.query(Job).filter(Job.external_id == parsed_job["external_id"]).first()
    if existing_job:
        new_job = existing_job
    else:
        new_job = Job(
            external_id=parsed_job["external_id"],
            title=parsed_job["title"],
            company=parsed_job["company"],
            location=parsed_job["location"],
            is_remote=parsed_job["is_remote"],
            salary_text=parsed_job["salary_text"],
            salary_min=parsed_job["salary_min"],
            description=parsed_job["description"],
            required_skills=parsed_job["required_skills"],
            preferred_skills=parsed_job["preferred_skills"],
            education_requirements=parsed_job["education_requirements"],
            eligibility=parsed_job["eligibility"],
            url=parsed_job["url"],
            application_method=parsed_job["application_method"],
            source="custom_jd_input",
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
    
    return {
        "job_id": new_job.id,
        "job": parsed_job,
        "is_eligible": is_eligible,
        "eligibility_reason": eligibility_reason,
        "match_score": match_result["overall_score"],
        "breakdown": match_result["breakdown"],
        "reason": match_result["reason"],
        "why_this_job": match_result["why_this_job"],
        "evidence_table": match_result["evidence_table"]
    }

