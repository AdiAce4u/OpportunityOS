from typing import Any, List, Optional
from pydantic import BaseModel, Field

class ProfileCreate(BaseModel):
    name: str = "Candidate"
    email: str = "candidate@example.com"
    phone: str = "+91 9876543210"
    graduation_year: Optional[int] = 2028
    degree: str = "B.Tech"
    college: str = "IIT Kharagpur"
    cgpa: Optional[float] = 8.39
    skills: List[str] = Field(default_factory=list)
    projects: List[Any] = Field(default_factory=list)
    categorized_projects: List[Any] = Field(default_factory=list)
    experience: List[Any] = Field(default_factory=list)
    
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: bool = True
    minimum_salary: Optional[float] = 40000.0
    work_authorization: str = "Eligible to work in India"
    prefer_companies: List[str] = Field(default_factory=list)
    avoid_companies: List[str] = Field(default_factory=list)
    
    master_cv_markdown: str = ""
    resume_text: str = ""
    resume_filename: str = ""
    master_cv_pdf_path: str = "uploads/mastercv.pdf"
    saved_tailored_cvs: List[Any] = Field(default_factory=list)

class ProfileResponse(ProfileCreate):
    id: int
    parsed_data: dict[str, Any] = Field(default_factory=dict)

class ResumeParseRequest(BaseModel):
    text: str

class SaveTailoredCVRequest(BaseModel):
    company: str
    role: str
    application_id: Optional[int] = None
    resume_text: Optional[str] = None

