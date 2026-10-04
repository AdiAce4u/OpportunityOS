import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Application, Job, UserProfile
from app.schemas.application import ApprovalRequest, ApplicationResponse, ProvideMissingInfoRequest
from app.agents.graph import submission_graph

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("", response_model=list[dict])
def list_applications(db: Session = Depends(get_db)):
    rows = db.query(Application).order_by(Application.updated_at.desc()).all()
    results = []
    for row in rows:
        job = db.get(Job, row.job_id)
        results.append({
            "id": row.id,
            "job_id": row.job_id,
            "title": job.title if job else "Role",
            "company": job.company if job else "Company",
            "location": job.location if job else "",
            "salary_text": job.salary_text if job else "",
            "status": row.status,
            "match_score": row.match_score,
            "match_reason": row.match_reason,
            "match_breakdown": row.match_breakdown or {},
            "why_this_job": row.why_this_job or {},
            "external_application_id": row.external_application_id,
            "updated_at": row.updated_at.strftime("%Y-%m-%d %H:%M") if row.updated_at else None,
            "applied_date": row.applied_date.strftime("%Y-%m-%d %H:%M") if row.applied_date else None,
        })
    return results

@router.get("/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db)):
    row = db.get(Application, application_id)
    if not row:
        raise HTTPException(404, "Application not found")
    job = db.get(Job, row.job_id)
    return {
        "id": row.id,
        "profile_id": row.profile_id,
        "job_id": row.job_id,
        "status": row.status,
        "match_score": row.match_score,
        "match_breakdown": row.match_breakdown or {},
        "match_reason": row.match_reason,
        "why_this_job": row.why_this_job or {},
        "evidence_table": (row.why_this_job or {}).get("evidence_table", []),
        "company_research": row.company_research or (job.company_research if job else {}),
        "tailored_resume": row.tailored_resume,
        "tailored_resume_pdf_path": row.tailored_resume_pdf_path,
        "cover_letter": row.cover_letter,
        "answers": row.answers or {},
        "missing_information": row.missing_information or [],
        "user_edited": row.user_edited,
        "external_application_id": row.external_application_id,
        "submission_receipt": row.submission_receipt or {},
        "job": {
            "title": job.title if job else "",
            "company": job.company if job else "",
            "location": job.location if job else "",
            "salary_text": job.salary_text if job else "",
            "description": job.description if job else "",
            "url": job.url if job else "",
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
        } if job else None
    }

@router.post("/{application_id}/approval")
def handle_approval(application_id: int, request: ApprovalRequest, db: Session = Depends(get_db)):
    """
    HUMAN-IN-THE-LOOP CHECKPOINT:
    Before submitting ANY application, user explicitly approves, edits, or rejects.
    Only after user approval does browser automation proceed!
    """
    row = db.get(Application, application_id)
    if not row:
        raise HTTPException(404, "Application not found")
        
    if not request.approve:
        row.status = "REJECTED_BY_USER"
        row.user_feedback = request.user_feedback or "Rejected by candidate during review."
        db.commit()
        return {"status": row.status, "message": "Application discarded by user."}

    # Apply any edits from candidate
    if request.edited_cover_letter:
        row.cover_letter = request.edited_cover_letter
        row.user_edited = True
    if request.edited_answers:
        row.answers = request.edited_answers
        row.user_edited = True
    if request.edited_resume:
        row.tailored_resume = request.edited_resume
        row.user_edited = True
    db.commit()
    
    # Execute Browser Automation Agent
    job = db.get(Job, row.job_id)
    profile = db.get(UserProfile, row.profile_id) if row.profile_id else db.query(UserProfile).first()
    
    state_input = {
        "application_id": row.id,
        "selected_job": {
            "external_id": job.external_id if job else "job-001",
            "title": job.title if job else "Position",
            "company": job.company if job else "Company",
            "url": job.url if job else "",
        },
        "user_profile": {
            "name": profile.name if profile else "Candidate",
            "email": profile.email if profile else "demo@example.com",
            "phone": profile.phone if profile else "+91 9876543210",
            "college": profile.college if profile else "IIT",
            "degree": profile.degree if profile else "B.Tech",
        },
        "cover_letter": row.cover_letter,
        "application_answers": row.answers,
        "tailored_resume_pdf_path": row.tailored_resume_pdf_path,
        "logs": []
    }
    
    result = submission_graph.invoke(state_input)
    db.refresh(row)
    
    return {
        "status": row.status,
        "external_application_id": row.external_application_id,
        "submission_receipt": row.submission_receipt,
        "logs": result.get("logs", [])
    }

@router.post("/{application_id}/provide-missing-info")
def provide_missing_info(application_id: int, request: ProvideMissingInfoRequest, db: Session = Depends(get_db)):
    row = db.get(Application, application_id)
    if not row:
        raise HTTPException(404, "Application not found")
        
    answers = row.answers or {}
    answers.update(request.answers)
    row.answers = answers
    row.missing_information = []
    db.commit()
    return {"status": "UPDATED", "answers": row.answers}

@router.post("/{application_id}/prepare-portal")
def prepare_portal(application_id: int, db: Session = Depends(get_db)):
    """
    Phase 3: Two-stage browser automation - Step 1: Pre-fill & Snapshot
    Loads the job application portal, fills form fields and attaches tailored resume,
    captures a visual snapshot (screenshot) for human review before final submission.
    """
    from app.tools.browser_tools import prepare_portal_prefill_sync
    
    row = db.get(Application, application_id)
    if not row:
        raise HTTPException(404, "Application not found")
        
    job = db.get(Job, row.job_id)
    profile = db.get(UserProfile, row.profile_id) if row.profile_id else db.query(UserProfile).first()
    
    job_url = (job.url if (job and job.url) else "http://localhost:8000/portal/apply/job-001")
    
    form_data = {
        "name": profile.name if profile else "Candidate",
        "email": profile.email if profile else "demo@example.com",
        "phone": profile.phone if profile else "+91 9876543210",
        "college": profile.college if profile else "Engineering College",
        "degree": profile.degree if profile else "B.Tech",
        "cover_letter": row.cover_letter or "",
        "answers": row.answers or {},
    }
    
    result = prepare_portal_prefill_sync(
        url=job_url,
        form_data=form_data,
        resume_path=row.tailored_resume_pdf_path or "",
        app_id=row.id
    )
    
    # Update application record with prefill snapshot
    receipt = dict(row.submission_receipt or {})
    if result.get("snapshot_url"):
        receipt["prefill_snapshot_url"] = result.get("snapshot_url")
    row.submission_receipt = receipt
    db.commit()
    
    return {
        "status": result.get("status", "PORTAL_PREFILLED"),
        "snapshot_url": result.get("snapshot_url", ""),
        "details": result.get("details", "")
    }

@router.get("/{application_id}/resume-pdf")
def download_resume_pdf(application_id: int, db: Session = Depends(get_db)):
    """
    Returns the tailored ATS PDF resume for this application.
    If the PDF file has not yet been generated on disk, dynamically compiles it on demand
    using the tailored_resume text so it is always viewable and downloadable.
    """
    row = db.get(Application, application_id)
    if not row:
        raise HTTPException(404, "Application not found")
        
    os.makedirs("uploads", exist_ok=True)
    pdf_path = row.tailored_resume_pdf_path
    
    if not pdf_path or not os.path.exists(pdf_path):
        from app.tools.resume_tools import generate_resume_pdf
        pdf_filename = f"Tailored_Resume_App_{row.id}.pdf"
        pdf_path = os.path.join("uploads", pdf_filename)
        resume_content = row.tailored_resume or "Candidate Tailored Resume"
        generate_resume_pdf(resume_content, pdf_path)
        row.tailored_resume_pdf_path = pdf_path
        db.commit()
        
    filename = os.path.basename(pdf_path)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )
