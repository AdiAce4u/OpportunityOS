from typing import Any
from pydantic import BaseModel, Field

class JobSchema(BaseModel):
    id: int | None = None
    external_id: str
    title: str
    company: str
    location: str = ""
    is_remote: bool = False
    salary_text: str = ""
    salary_min: float | None = None
    salary_max: float | None = None
    description: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    eligibility: dict[str, Any] = Field(default_factory=dict)
    deadline: str = ""
    url: str = ""
    application_method: str = "form"
    required_documents: list[str] = Field(default_factory=list)
    source: str = "career_page"
    company_research: dict[str, Any] = Field(default_factory=dict)

class JobSearchQuery(BaseModel):
    query: str
    location: str | None = None
    roles: list[str] = Field(default_factory=list)
    min_salary: float | None = None
