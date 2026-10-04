from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    degree: Mapped[str] = mapped_column(String(120), default="")
    college: Mapped[str] = mapped_column(String(255), default="")
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    projects: Mapped[list] = mapped_column(JSON, default=list)
    categorized_projects: Mapped[list] = mapped_column(JSON, default=list)
    experience: Mapped[list] = mapped_column(JSON, default=list)
    
    # Target Search Criteria & Preferences
    preferred_roles: Mapped[list] = mapped_column(JSON, default=list)
    preferred_locations: Mapped[list] = mapped_column(JSON, default=list)
    remote_preference: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_authorization: Mapped[str] = mapped_column(String(120), default="Eligible to work in India")
    prefer_companies: Mapped[list] = mapped_column(JSON, default=list)
    avoid_companies: Mapped[list] = mapped_column(JSON, default=list)
    
    # Resume & Master CV artifacts
    master_cv_markdown: Mapped[str] = mapped_column(Text, default="")
    resume_filename: Mapped[str] = mapped_column(String(255), default="")
    resume_text: Mapped[str] = mapped_column(Text, default="")
    master_cv_pdf_path: Mapped[str] = mapped_column(String(255), default="uploads/mastercv.pdf")
    saved_tailored_cvs: Mapped[list] = mapped_column(JSON, default=list)
    parsed_data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
