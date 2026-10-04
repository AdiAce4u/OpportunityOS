from datetime import datetime
from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.browser_tools import submit_application_sync
from app.db.session import SessionLocal
from app.models import Application

def browser_agent_submit(state: JobState) -> JobState:
    """
    Browser Automation Agent Node:
    CRITICAL SAFETY CHECK: Only invoked AFTER Human Review & Approval!
    Executes Playwright browser automation against application portal.
    """
    app_id = state.get("application_id")
    if not app_id:
        return state
        
    db = SessionLocal()
    try:
        app_record = db.get(Application, app_id)
        if not app_record:
            return state
            
        selected = state.get("selected_job") or {}
        url = selected.get("url") or f"http://localhost:8000/portal/apply/{selected.get('external_id')}"
        profile = state.get("user_profile") or {}
        
        form_data = {
            "name": profile.get("name"),
            "email": profile.get("email"),
            "phone": profile.get("phone"),
            "college": profile.get("college"),
            "degree": profile.get("degree"),
            "cover_letter": state.get("cover_letter"),
            "answers": state.get("application_answers", {})
        }
        
        log_event(
            state,
            "BrowserAgent",
            f"Launching Playwright automation: opening {url}..."
        )
        
        result = submit_application_sync(url, form_data, state.get("tailored_resume_pdf_path", ""))
        
        app_record.status = "SUBMITTED"
        app_record.external_application_id = result.get("application_id", "")
        app_record.applied_date = datetime.utcnow()
        app_record.submission_receipt = result
        db.commit()
        db.refresh(app_record)
        
        state["application_status"] = "SUBMITTED"
        state["browser_state"] = result
        
        log_event(
            state,
            "BrowserAgent",
            f"✓ Application successfully submitted! Confirmation ID: {result.get('application_id')}",
            metadata={"receipt": result}
        )
    finally:
        db.close()
        
    return state
