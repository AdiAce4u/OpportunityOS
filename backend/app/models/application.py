from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Application(Base):
    __tablename__ = "applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    
    # Status lifecycle:
    # DISCOVERED, ELIGIBLE, SHORTLISTED, PREPARING, AWAITING_APPROVAL,
    # SUBMITTED, UNDER_REVIEW, INTERVIEW, REJECTED, OFFER, WITHDRAWN
    status: Mapped[str] = mapped_column(String(50), default="DISCOVERED")
    
    # Matching details
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    match_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    match_reason: Mapped[str] = mapped_column(Text, default="")
    why_this_job: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Company research insights
    company_research: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Tailored artifacts
    tailored_resume: Mapped[str] = mapped_column(Text, default="")
    tailored_resume_pdf_path: Mapped[str] = mapped_column(String(500), default="")
    cover_letter: Mapped[str] = mapped_column(Text, default="")
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Human-in-the-loop and missing information
    missing_information: Mapped[list] = mapped_column(JSON, default=list)
    user_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    user_feedback: Mapped[str] = mapped_column(Text, default="")
    
    # Submission details
    external_application_id: Mapped[str] = mapped_column(String(255), default="")
    submission_receipt: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Tracking & Follow-up
    applied_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    interview_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    
    # Candidate interaction & wishlist state
    is_wishlisted: Mapped[bool] = mapped_column(Boolean, default=False)
    recently_browsed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_browsed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
