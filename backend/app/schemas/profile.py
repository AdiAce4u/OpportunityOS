from typing import Any
from pydantic import BaseModel, Field

class ProjectItem(BaseModel):
    name: str
    description: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    link: str = ""

class ExperienceItem(BaseModel):
    role: str
    company: str
    duration: str = ""
    description: str = ""

class ProfileCreate(BaseModel):
    name: str = "Candidate"
    email: str = "candidate@example.com"
    phone: str = "+91 9876543210"
    graduation_year: int | None = 2027
    degree: str = "B.Tech"
    college: str = "IIT Kharagpur"
    cgpa: float | None = 8.9
    skills: list[str] = Field(default_factory=lambda: ["Python", "C++", "ROS2", "Machine Learning", "Robotics", "Controls"])
    projects: list[ProjectItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    
    preferred_roles: list[str] = Field(default_factory=lambda: ["Robotics Intern", "Robotics Software Intern", "ML Intern", "AI Intern"])
    preferred_locations: list[str] = Field(default_factory=lambda: ["India", "Bangalore", "Hyderabad", "Remote"])
    remote_preference: bool = True
    minimum_salary: float | None = 40000.0
    work_authorization: str = "Eligible to work in India"
    prefer_companies: list[str] = Field(default_factory=list)
    avoid_companies: list[str] = Field(default_factory=list)
    
    resume_text: str = ""
    resume_filename: str = ""

class ProfileResponse(ProfileCreate):
    id: int
    parsed_data: dict[str, Any] = Field(default_factory=dict)

class ResumeParseRequest(BaseModel):
    text: str
