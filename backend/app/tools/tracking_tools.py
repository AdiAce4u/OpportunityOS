from datetime import datetime, timedelta
from typing import Any
from app.db.session import SessionLocal
from app.models import Application, Job, FollowUpEvent

def save_application(app_data: dict[str, Any]) -> int:
    db = SessionLocal()
    try:
        app = Application(**app_data)
        db.add(app)
        db.commit()
        db.refresh(app)
        return app.id
    finally:
        db.close()

def get_application_status(application_id: int) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        app = db.get(Application, application_id)
        if not app:
            return None
        return {
            "id": app.id,
            "status": app.status,
            "match_score": app.match_score,
            "applied_date": app.applied_date.isoformat() if app.applied_date else None,
            "external_id": app.external_application_id,
        }
    finally:
        db.close()

def get_all_applications() -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        apps = db.query(Application).order_by(Application.updated_at.desc()).all()
        results = []
        for a in apps:
            job = db.get(Job, a.job_id)
            results.append({
                "id": a.id,
                "job_id": a.job_id,
                "title": job.title if job else "Position",
                "company": job.company if job else "Company",
                "location": job.location if job else "",
                "status": a.status,
                "match_score": a.match_score,
                "match_reason": a.match_reason,
                "match_breakdown": a.match_breakdown,
                "why_this_job": a.why_this_job,
                "applied_date": a.applied_date.strftime("%Y-%m-%d %H:%M") if a.applied_date else None,
                "external_application_id": a.external_application_id,
                "updated_at": a.updated_at.strftime("%Y-%m-%d %H:%M") if a.updated_at else None,
            })
        return results
    finally:
        db.close()

def check_email_for_application_updates() -> list[dict[str, Any]]:
    """
    Checks for incoming status updates, interview invitations, or rejections.
    """
    db = SessionLocal()
    try:
        pending_events = db.query(FollowUpEvent).filter(FollowUpEvent.status == "PENDING").all()
        updates = []
        for event in pending_events:
            app = db.get(Application, event.application_id)
            job = db.get(Job, app.job_id) if app else None
            updates.append({
                "event_id": event.id,
                "application_id": event.application_id,
                "company": job.company if job else "Target Company",
                "role": job.title if job else "Role",
                "type": event.event_type,
                "subject": event.subject,
                "content": event.content,
                "interview_details": event.interview_details,
                "prep_notes": event.prep_notes,
            })
        return updates
    finally:
        db.close()

def create_follow_up(application_id: int, event_type: str, days_later: int = 5) -> int:
    db = SessionLocal()
    try:
        app = db.get(Application, application_id)
        job = db.get(Job, app.job_id) if app else None
        company = job.company if job else "Hiring Team"
        role = job.title if job else "Role"
        
        event = FollowUpEvent(
            application_id=application_id,
            event_type=event_type,
            scheduled_for=datetime.utcnow() + timedelta(days=days_later),
            status="PENDING",
            subject=f"Polite Follow-up: {role} Application Status at {company}",
            content=f"Dear {company} Hiring Team,\n\nI hope this email finds you well. I submitted my application for the {role} position recently and wanted to reaffirm my strong enthusiasm for joining your team. Please let me know if there are any additional materials I can provide.\n\nThank you for your consideration."
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event.id
    finally:
        db.close()

def notify_user(title: str, message: str) -> dict[str, str]:
    return {"title": title, "message": message, "timestamp": datetime.now().strftime("%H:%M:%S")}
