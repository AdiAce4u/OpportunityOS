from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Application, Job, FollowUpEvent, UserProfile
from app.tools.research_tools import research_company

router = APIRouter(prefix="/tracker", tags=["Tracker & Follow-ups"])

@router.get("/dashboard")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    has_cv = bool(
        profile and (
            profile.master_cv_markdown
            or (profile.projects and len(profile.projects) > 0)
            or profile.resume_text
        )
    )

    if not has_cv:
        return {
            "total_opportunities_found": 0,
            "eligible_opportunities": 0,
            "shortlisted": 0,
            "applications_prepared": 0,
            "applications_submitted": 0,
            "interviews": 0,
            "offers": 0,
            "rejections": 0,
            "estimated_time_saved_hours": 0.0,
        }

    total_jobs = db.query(Job).count()
    apps = db.query(Application).all()
    
    total_apps = len(apps)
    prepared = len([a for a in apps if a.status in ["PREPARING", "AWAITING_APPROVAL"]])
    submitted = len([a for a in apps if "SUBMIT" in (a.status or "") or a.status == "UNDER_REVIEW"])
    interviews = len([a for a in apps if a.status == "INTERVIEW"])
    
    # Also check follow-up events for detected interviews
    interview_events = db.query(FollowUpEvent).filter(FollowUpEvent.event_type == "INTERVIEW_INVITATION").count()
    interviews = max(interviews, interview_events)
    
    offers = len([a for a in apps if a.status == "OFFER"])
    rejections = len([a for a in apps if "REJECT" in (a.status or "")])
    shortlisted = len([a for a in apps if a.match_score and a.match_score >= 70.0])
    
    # Time saved: ~1.75 hrs per prepared application
    hours_saved = round((total_apps * 1.75) + (total_jobs * 0.05 if total_apps > 0 else 0), 1)

    return {
        "total_opportunities_found": total_jobs,
        "eligible_opportunities": total_jobs,
        "shortlisted": shortlisted,
        "applications_prepared": total_apps,
        "applications_submitted": submitted,
        "interviews": interviews,
        "offers": offers,
        "rejections": rejections,
        "estimated_time_saved_hours": hours_saved,
    }

@router.get("/events")
def get_tracker_events(db: Session = Depends(get_db)):
    events = db.query(FollowUpEvent).order_by(FollowUpEvent.scheduled_for.desc()).all()
    results = []
    for e in events:
        app = db.get(Application, e.application_id)
        job = db.get(Job, app.job_id) if app else None
        results.append({
            "id": e.id,
            "application_id": e.application_id,
            "company": job.company if job else "Company",
            "role": job.title if job else "Role",
            "event_type": e.event_type,
            "scheduled_for": e.scheduled_for.strftime("%Y-%m-%d %H:%M"),
            "status": e.status,
            "subject": e.subject,
            "content": e.content,
            "interview_details": e.interview_details or {},
            "prep_notes": e.prep_notes,
        })
    return results

@router.get("/interview-prep/{application_id}")
def generate_interview_prep(application_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if not app:
        raise HTTPException(404, "Application not found")
        
    job = db.get(Job, app.job_id)
    company_info = app.company_research or (research_company(job.company) if job else {})
    
    return {
        "company": job.company if job else "Target Company",
        "role": job.title if job else "Role",
        "domain": company_info.get("domain", "Technology"),
        "key_technologies": company_info.get("technology", ["Python", "ROS2", "C++"]),
        "recent_news": company_info.get("recent_news", []),
        "company_briefing": company_info.get("company_summary", ""),
        "recommended_talking_points": [
            f"Highlight your experience with {', '.join(job.required_skills[:3]) if job else 'core skills'}.",
            f"Relate your university projects directly to {company_info.get('domain', 'the company field')}.",
            "Emphasize autonomous debugging, modular system design, and performance optimization."
        ],
        "probable_technical_questions": [
            "Explain the difference between topics, services, and actions in ROS2 and when to use each.",
            "How do you handle sensor uncertainty and Kalman filter drift in real-time robotics perception?",
            "Describe a challenging bug you encountered in a recent project and how you resolved it."
        ],
        "suggested_questions_for_interviewer": [
            f"What does the day-to-day deployment pipeline look like for robots at {job.company if job else 'the company'}?",
            "What simulation environments and hardware-in-the-loop tests does the team rely on?",
            "What are the most exciting autonomy milestones planned for the next six months?"
        ]
    }
