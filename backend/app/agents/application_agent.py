from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.application_tools import (
    generate_cover_letter as tool_cover_letter,
    generate_application_answers as tool_answers,
    find_missing_information as tool_find_missing,
)
from app.db.session import SessionLocal
from app.models import Application, Job

def generate_application(state: JobState) -> JobState:
    """
    Application Preparation Agent Node:
    - Prepares tailored cover letter
    - Prepares answers to 'Why this company?', 'Why this role?'
    - Inspects for missing required data
    - Sets human review checkpoint
    """
    selected = state.get("selected_job")
    if not selected:
        return state
        
    profile = state["user_profile"]
    cover_letter = tool_cover_letter(selected, profile)
    answers = tool_answers(selected, profile)
    missing = tool_find_missing(selected, profile)
    
    state["cover_letter"] = cover_letter
    state["application_answers"] = answers
    state["missing_information"] = missing
    
    # Store or update in database as AWAITING_APPROVAL
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.external_id == selected["external_id"]).first()
        if not db_job:
            db_job = Job(**selected)
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            
        app_record = db.query(Application).filter(Application.job_id == db_job.id).first()
        if not app_record:
            app_record = Application(
                profile_id=profile.get("id"),
                job_id=db_job.id,
                status="AWAITING_APPROVAL",
                match_score=state.get("match_score", 0.0),
                match_breakdown=state.get("match_breakdown", {}),
                match_reason=state.get("match_reason", ""),
                why_this_job=state.get("why_this_job", {}),
                company_research=state.get("company_research", {}),
                tailored_resume=state.get("tailored_resume", ""),
                tailored_resume_pdf_path=state.get("tailored_resume_pdf_path", ""),
                cover_letter=cover_letter,
                answers=answers,
                missing_information=missing,
            )
            db.add(app_record)
            db.commit()
            db.refresh(app_record)
        else:
            app_record.status = "AWAITING_APPROVAL"
            app_record.match_score = state.get("match_score", 0.0)
            app_record.match_breakdown = state.get("match_breakdown", {})
            app_record.match_reason = state.get("match_reason", "")
            app_record.why_this_job = state.get("why_this_job", {})
            app_record.company_research = state.get("company_research", {})
            app_record.tailored_resume = state.get("tailored_resume", "")
            app_record.tailored_resume_pdf_path = state.get("tailored_resume_pdf_path", "")
            app_record.cover_letter = cover_letter
            app_record.answers = answers
            app_record.missing_information = missing
            db.commit()
            db.refresh(app_record)
            
        state["application_id"] = app_record.id
        state["application_status"] = "AWAITING_APPROVAL"
    finally:
        db.close()
        
    if missing:
        log_event(
            state,
            "ApplicationAgent",
            f"Missing information flagged ({', '.join(missing)}). Awaiting human clarification before review.",
            level="WARNING",
            metadata={"missing": missing}
        )
    else:
        log_event(
            state,
            "ApplicationAgent",
            f"Application package ready for {selected.get('title')} at {selected.get('company')}! Paused for Human Approval.",
            metadata={"application_id": state["application_id"]}
        )
    return state
