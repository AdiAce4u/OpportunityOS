from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str] = mapped_column(String(255), default="")
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Portal search attributes
    category: Mapped[str] = mapped_column(String(100), default="custom")
    search_term: Mapped[str] = mapped_column(String(255), default="")
    site: Mapped[str] = mapped_column(String(100), default="linkedin")
    
    # Match & Compensation
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    best_matching_project: Mapped[str] = mapped_column(String(255), default="")
    best_project_domain: Mapped[str] = mapped_column(String(100), default="general")
    matched_keywords: Mapped[list] = mapped_column(JSON, default=list)
    
    salary_text: Mapped[str] = mapped_column(String(255), default="")
    display_salary: Mapped[str] = mapped_column(String(255), default="Competitive")
    normalized_salary: Mapped[float] = mapped_column(Float, default=0.0)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    description: Mapped[str] = mapped_column(Text, default="")
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list)
    
    education_requirements: Mapped[list] = mapped_column(JSON, default=list)
    graduation_requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    experience_requirements: Mapped[str] = mapped_column(String(255), default="0-1 years")
    
    eligibility: Mapped[dict] = mapped_column(JSON, default=dict)
    deadline: Mapped[str] = mapped_column(String(100), default="Rolling basis")
    
    url: Mapped[str] = mapped_column(String(1000), default="")
    application_method: Mapped[str] = mapped_column(String(100), default="form")
    required_documents: Mapped[list] = mapped_column(JSON, default=lambda: ["resume"])
    source: Mapped[str] = mapped_column(String(100), default="portal")
    
    company_research: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Candidate interaction & wishlist state
    is_wishlisted: Mapped[bool] = mapped_column(Boolean, default=False)
    recently_browsed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_browsed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
