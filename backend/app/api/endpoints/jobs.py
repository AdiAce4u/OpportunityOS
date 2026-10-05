import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Job, UserProfile, Application
from app.schemas.job import JobSchema, CustomJDAnalysisRequest
from app.tools.portal_search_engine import search_live_portals, ROLE_CATEGORIES, CVProjectMatcher, CompensationParser
from app.tools.extraction_tools import parse_custom_jd
from app.tools.matching_tools import calculate_job_match, check_eligibility

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class PortalSearchRequest(BaseModel):
    category: Optional[str] = "software"
    query: Optional[str] = None
    location: Optional[str] = "India"
    results_wanted: Optional[int] = 15
    sites: Optional[List[str]] = ["linkedin", "indeed", "glassdoor", "wellfound"]
    is_remote: Optional[bool] = False
    profile_id: Optional[int] = None

@router.get("", response_model=list[JobSchema])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.match_score.desc(), Job.created_at.desc()).all()

@router.post("/{job_id}/wishlist")
def toggle_wishlist(job_id: int, db: Session = Depends(get_db)):
    """
    Toggles the wishlist state (heart icon) for a job opportunity.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.is_wishlisted = not bool(job.is_wishlisted)

    # Sync to application if existing
    app_rec = db.query(Application).filter(Application.job_id == job.id).first()
    if app_rec:
        app_rec.is_wishlisted = job.is_wishlisted

    db.commit()
    return {"job_id": job.id, "is_wishlisted": job.is_wishlisted, "message": "Wishlist updated"}

@router.post("/{job_id}/browse")
def mark_job_browsed(job_id: int, db: Session = Depends(get_db)):
    """
    Marks an opportunity as recently browsed when the candidate inspects or opens it.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.recently_browsed = True
    job.last_browsed_at = datetime.utcnow()

    app_rec = db.query(Application).filter(Application.job_id == job.id).first()
    if app_rec:
        app_rec.recently_browsed = True
        app_rec.last_browsed_at = job.last_browsed_at

    db.commit()
    return {"job_id": job.id, "recently_browsed": True}


@router.get("/categories")
def get_job_categories():
    return {
        "categories": {
            "software": ["Software Development Engineer", "Backend Engineer", "Frontend Engineer", "Full Stack Developer", "DevOps Engineer"],
            "data": ["Data Scientist", "Machine Learning Engineer", "AI Engineer", "Data Engineer", "Data Analyst"],
            "consult": ["Management Consultant", "Strategy Analyst", "Business Analyst", "Technology Consulting Analyst"],
            "finance": ["Quantitative Analyst", "Quantitative Researcher", "Financial Analyst", "Risk Analyst"],
            "core": ["Robotics Software Engineer", "Embedded Software Engineer", "Hardware Engineer", "Mechanical Design Engineer"]
        }
    }

@router.get("/{job_id}", response_model=JobSchema)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@router.post("/portal-search")
def search_job_portals(request: PortalSearchRequest, db: Session = Depends(get_db)):
    """
    Executes multi-platform job discovery for the 5 requested tracks:
    Software, Data, Consult, Finance, and Core.
    """
    profile = db.get(UserProfile, request.profile_id) if request.profile_id else db.query(UserProfile).first()
    candidate_projects = (profile.categorized_projects or profile.projects or []) if profile else []

    category = (request.category or "software").lower()
    if category == "sde":
        category = "software"

    search_term = request.query
    if not search_term or search_term.startswith("ALL_"):
        cat_roles = ROLE_CATEGORIES.get(category, ["Software Development Engineer"])
        search_term = cat_roles[0]

    discovered_jobs = search_live_portals(
        search_term=search_term,
        location=request.location or "India",
        category=category,
        results_wanted=request.results_wanted or 15,
        sites=request.sites,
        is_remote=request.is_remote or False,
        candidate_projects=candidate_projects
    )

    saved_jobs = []
    for item in discovered_jobs:
        ext_id = f"{item.get('site', 'web')}-{uuid.uuid5(uuid.NAMESPACE_DNS, item.get('title', '') + item.get('company', '') + item.get('location', '')).hex[:12]}"
        
        existing = db.query(Job).filter(Job.external_id == ext_id).first()
        if not existing:
            existing = db.query(Job).filter(Job.title == item.get("title"), Job.company == item.get("company")).first()

        if existing:
            existing.url = item.get("job_url") or existing.url
            existing.match_score = item.get("match_score", existing.match_score)
            existing.best_matching_project = item.get("best_matching_project", existing.best_matching_project)
            existing.best_project_domain = item.get("best_project_domain", existing.best_project_domain)
            existing.matched_keywords = item.get("matched_keywords", existing.matched_keywords)
            existing.display_salary = item.get("display_salary", existing.display_salary)
            existing.category = category
            saved_jobs.append(existing)
        else:
            new_job = Job(
                external_id=ext_id,
                title=item.get("title", search_term),
                company=item.get("company", "Tech Company"),
                location=item.get("location", request.location or "India"),
                is_remote=item.get("is_remote", False),
                category=category,
                search_term=search_term,
                site=item.get("site", "linkedin"),
                match_score=item.get("match_score", 75.0),
                best_matching_project=item.get("best_matching_project", "Featured Project"),
                best_project_domain=item.get("best_project_domain", category),
                matched_keywords=item.get("matched_keywords", []),
                salary_text=item.get("display_salary", "Competitive"),
                display_salary=item.get("display_salary", "Competitive"),
                normalized_salary=item.get("normalized_salary", 0.0),
                salary_min=item.get("min_amount"),
                salary_max=item.get("max_amount"),
                description=item.get("description", ""),
                required_skills=item.get("matched_keywords") or ["Problem Solving", "System Design"],
                preferred_skills=["Communication", "Leadership"],
                education_requirements=["B.Tech", "Degree"],
                eligibility={"graduation_year_min": 2026, "graduation_year_max": 2028},
                url=item.get("job_url", ""),
                application_method="portal",
                source=f"portal_{item.get('site', 'linkedin')}",
            )
            db.add(new_job)
            saved_jobs.append(new_job)

    db.commit()

    # Query all jobs matching this category
    cat_condition = (Job.category == category) | (Job.category == ("sde" if category == "software" else category))
    all_cat_jobs = db.query(Job).filter(cat_condition).order_by(Job.match_score.desc()).all()
    candidate_jobs = all_cat_jobs if all_cat_jobs else saved_jobs

    def matches_site(j_site: str, allowed: Optional[List[str]]) -> bool:
        if not allowed or len(allowed) == 4:
            return True
        js = (j_site or "").lower()
        for s in allowed:
            sl = s.lower()
            if sl == "linkedin" and ("linkedin" in js or "company_careers" in js):
                return True
            if sl == "wellfound" and ("wellfound" in js or "angel" in js):
                return True
            if sl == "indeed" and ("indeed" in js or "job_board" in js):
                return True
            if sl == "glassdoor" and "glassdoor" in js:
                return True
            if sl in js:
                return True
        return False

    filtered_jobs = []
    for j in candidate_jobs:
        # 1. Filter by Portal Sites
        if request.sites and not matches_site(j.site, request.sites):
            continue

        # 2. Filter by Remote preference
        if request.is_remote:
            loc_lower = (j.location or "").lower()
            if not (j.is_remote or "remote" in loc_lower):
                continue

        # 3. Filter by Location
        if request.location and request.location.strip().lower() not in ["india", "all", "any", ""]:
            target_loc = request.location.strip().lower()
            loc_lower = (j.location or "").lower()
            if not (target_loc in loc_lower or j.is_remote or "remote" in loc_lower):
                continue

        filtered_jobs.append(j)

    # Sort by match score
    filtered_jobs.sort(key=lambda x: x.match_score or 0.0, reverse=True)

    # Slicing by results_wanted (Max Results to Display)
    max_count = request.results_wanted if (request.results_wanted and request.results_wanted > 0) else 15
    final_display = filtered_jobs[:max_count]

    return {
        "status": "SUCCESS",
        "search_term": search_term,
        "category": category,
        "location": request.location,
        "total_discovered": len(filtered_jobs),
        "jobs": [
            {
                "id": j.id,
                "external_id": j.external_id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "is_remote": j.is_remote,
                "site": j.site,
                "category": j.category,
                "match_score": j.match_score,
                "best_matching_project": j.best_matching_project,
                "best_project_domain": j.best_project_domain,
                "matched_keywords": j.matched_keywords,
                "salary_text": j.salary_text,
                "display_salary": j.display_salary,
                "normalized_salary": j.normalized_salary or (CompensationParser._parse_from_text(j.salary_text or j.display_salary or '') or {}).get('normalized_yearly_salary', 0.0),
                "description": j.description,
                "url": j.url,
            }
            for j in final_display
        ]
    }

@router.post("/rescore")
def rescore_database(profile_id: Optional[int] = None, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id) if profile_id else db.query(UserProfile).first()
    if not profile:
        raise HTTPException(404, "No profile found")
    
    projects = profile.categorized_projects or profile.projects or []
    matcher = CVProjectMatcher(projects)
    
    all_jobs = db.query(Job).all()
    count = 0
    for j in all_jobs:
        match_info = matcher.match_job_description(j.title or "", j.description or "")
        j.match_score = match_info.get("match_score", 0.0)
        j.best_matching_project = match_info.get("best_project", "Featured Project")
        j.best_project_domain = match_info.get("best_project_domain", "general")
        j.matched_keywords = match_info.get("matched_keywords", [])
        count += 1
        
    db.commit()
    return {"status": "SUCCESS", "rescored_jobs_count": count}

@router.post("/analyze-custom-jd")
def analyze_custom_jd(request: CustomJDAnalysisRequest, db: Session = Depends(get_db)):
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
        "projects": profile.categorized_projects or profile.projects or [],
        "experience": profile.experience or [],
        "preferred_locations": profile.preferred_locations or [],
        "minimum_salary": profile.minimum_salary,
        "work_authorization": profile.work_authorization,
    }

    parsed_job = parse_custom_jd(request.jd_text, request.title, request.company)
    is_eligible, eligibility_reason = check_eligibility(parsed_job, profile_dict)
    match_result = calculate_job_match(parsed_job, profile_dict)
    
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
            match_score=match_result["overall_score"]
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
