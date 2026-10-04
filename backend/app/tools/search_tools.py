import json
import logging
from typing import Any
from app.db.session import SessionLocal
from app.models import Job, UserProfile
from app.tools.llm_adapter import llm_client

logger = logging.getLogger("OpportunityOS.Tools.Search")

def get_user_profile(profile_id: int) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        profile = db.get(UserProfile, profile_id)
        if not profile:
            return None
        return {
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "graduation_year": profile.graduation_year,
            "degree": profile.degree,
            "college": profile.college,
            "cgpa": profile.cgpa,
            "skills": profile.skills or [],
            "projects": profile.projects or [],
            "experience": profile.experience or [],
            "preferred_roles": profile.preferred_roles or [],
            "preferred_locations": profile.preferred_locations or [],
            "remote_preference": profile.remote_preference,
            "minimum_salary": profile.minimum_salary,
            "work_authorization": profile.work_authorization,
            "prefer_companies": profile.prefer_companies or [],
            "avoid_companies": profile.avoid_companies or [],
            "resume_text": profile.resume_text,
        }
    finally:
        db.close()

def get_resume(profile_id: int) -> str:
    db = SessionLocal()
    try:
        profile = db.get(UserProfile, profile_id)
        return profile.resume_text if profile else ""
    finally:
        db.close()

def generate_search_queries(user_goal: dict[str, Any], iteration: int = 1) -> list[str]:
    """
    Dynamically generates multiple targeted search queries for the autonomous search loop.
    Iteratively branches into specialized terminology and keywords.
    """
    roles = user_goal.get("roles") or ["Robotics Intern", "ML Intern"]
    locations = user_goal.get("locations") or ["India", "Bangalore", "Hyderabad", "Remote"]
    skills = user_goal.get("skills") or ["Python", "C++", "ROS2"]
    
    queries = []
    
    if iteration == 1:
        # Base direct queries
        for role in roles:
            for loc in locations[:3]:
                queries.append(f"{role} {loc}")
            queries.append(f"{role} {' '.join(skills[:2])}")
    elif iteration == 2:
        # Specialized technical sub-field queries
        for role in roles:
            queries.append(f"{role} autonomous systems")
            queries.append(f"{role} perception controls")
            queries.append(f"ROS2 robotics software intern")
            queries.append(f"computer vision ML intern India")
    else:
        # Advanced and company-targeted queries
        queries.extend([
            "robot autonomy intern India",
            "robot perception intern Bangalore",
            "SLAM autonomous mobile robot intern",
            "embedded robotics firmware intern",
            "embodied AI research intern Remote",
            "machine learning engineering intern stipend 40000"
        ])
    
    # Deduplicate while preserving order
    return list(dict.fromkeys(queries))

def search_job_source(query: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """
    Searches jobs from database & internal repositories matching tokens in query.
    """
    filters = filters or {}
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        tokens = {x.lower() for x in query.replace(",", " ").split() if len(x) > 2}
        results = []
        for job in jobs:
            text = f"{job.title} {job.company} {job.location} {job.description} {' '.join(job.required_skills)}".lower()
            relevance = sum(token in text for token in tokens)
            
            # Check remote filter if requested
            if filters.get("remote_only") and not job.is_remote and "remote" not in job.location.lower():
                continue
            
            if relevance > 0:
                results.append({
                    "id": job.id,
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
                    "education_requirements": job.education_requirements or [],
                    "eligibility": job.eligibility or {},
                    "deadline": job.deadline,
                    "url": job.url,
                    "application_method": job.application_method,
                    "required_documents": job.required_documents or ["resume"],
                    "source": job.source,
                    "company_research": job.company_research or {},
                    "relevance_score": relevance
                })
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results
    finally:
        db.close()

def search_company_careers(company: str, query: str = "") -> list[dict[str, Any]]:
    """Searches open positions directly on target company careers page."""
    return search_job_source(f"{company} {query}")

def search_web(query: str) -> list[dict[str, Any]]:
    """Simulates real-time web discovery across job listings and university postings."""
    return search_job_source(query)
