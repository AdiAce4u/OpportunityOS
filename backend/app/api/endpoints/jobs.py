from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Job
from app.schemas.job import JobSchema
from app.tools.search_tools import search_job_source

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
