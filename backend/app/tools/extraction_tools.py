import re
from typing import Any
from app.db.session import SessionLocal
from app.models import Job

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
