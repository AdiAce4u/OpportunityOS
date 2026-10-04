from typing import Any
from pydantic import BaseModel, Field
from app.schemas.job import JobSchema

class ApprovalRequest(BaseModel):
    approve: bool
    edited_answers: dict[str, Any] | None = None
    edited_cover_letter: str | None = None
    edited_resume: str | None = None
    user_feedback: str | None = None

class ApplicationResponse(BaseModel):
    id: int
    profile_id: int | None = None
    job_id: int
    status: str
    match_score: float
    match_breakdown: dict[str, Any] = Field(default_factory=dict)
    match_reason: str = ""
    why_this_job: dict[str, Any] = Field(default_factory=dict)
    company_research: dict[str, Any] = Field(default_factory=dict)
    tailored_resume: str = ""
    tailored_resume_pdf_path: str = ""
    cover_letter: str = ""
    answers: dict[str, Any] = Field(default_factory=dict)
    missing_information: list[str] = Field(default_factory=list)
    user_edited: bool = False
    external_application_id: str = ""
    submission_receipt: dict[str, Any] = Field(default_factory=dict)
    job: JobSchema | None = None

class ProvideMissingInfoRequest(BaseModel):
    answers: dict[str, Any]
