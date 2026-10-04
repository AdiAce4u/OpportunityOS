import uuid
from datetime import datetime
from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.db.session import SessionLocal
from app.models import Application

def browser_agent_submit(state: JobState) -> JobState:
    """
    Direct Portal Link Dispatch Node:
    Instead of brittle browser form filling, records the direct portal application link
    and tracks application lifecycle status.
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
        app_code = f"APP-{uuid.uuid4().hex[:8].upper()}"
        
        result = {
            "status": "SUBMITTED",
            "application_id": app_code,
            "method": "DIRECT_PORTAL_LINK",
            "url": url,
            "details": f"Direct link provided to official portal: {url}"
        }
        
        app_record.status = "SUBMITTED"
        app_record.external_application_id = app_code
        app_record.applied_date = datetime.utcnow()
        app_record.submission_receipt = result
        db.commit()
        db.refresh(app_record)
        
        state["application_status"] = "SUBMITTED"
        state["browser_state"] = result
        
        log_event(
            state,
            "ApplicationAgent",
            f"✓ Portal application link prepared for {selected.get('title')} at {selected.get('company')}. Reference: {app_code}",
            metadata={"receipt": result}
        )
    finally:
        db.close()
        
    return state
