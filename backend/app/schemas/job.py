from typing import Any, List, Optional
from pydantic import BaseModel, Field

class JobSchema(BaseModel):
    id: Optional[int] = None
    external_id: str
    title: str
    company: str
    location: str = ""
    is_remote: bool = False
    category: str = "custom"
    search_term: str = ""
    site: str = "linkedin"
    match_score: float = 0.0
    best_matching_project: str = ""
    best_project_domain: str = "general"
    matched_keywords: List[str] = Field(default_factory=list)
    salary_text: str = ""
    display_salary: str = ""
    normalized_salary: float = 0.0
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    eligibility: dict[str, Any] = Field(default_factory=dict)
    deadline: str = ""
    url: str = ""
    application_method: str = "portal"
    required_documents: List[str] = Field(default_factory=list)
    source: str = "portal"
    company_research: dict[str, Any] = Field(default_factory=dict)

class JobSearchQuery(BaseModel):
    query: str
    location: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    min_salary: Optional[float] = None

class CustomJDAnalysisRequest(BaseModel):
    jd_text: str
    title: str = ""
    company: str = ""
    profile_id: Optional[int] = None
