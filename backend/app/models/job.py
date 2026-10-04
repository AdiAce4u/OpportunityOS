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
    
    salary_text: Mapped[str] = mapped_column(String(255), default="")
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
    source: Mapped[str] = mapped_column(String(100), default="career_page")
    
    company_research: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
