from typing import Any, TypedDict

class JobState(TypedDict, total=False):
    profile_id: int
    user_profile: dict[str, Any]
    search_goal: dict[str, Any]
    search_queries: list[str]
    search_results: list[dict[str, Any]]
    discovered_jobs: list[dict[str, Any]]
    eligible_jobs: list[dict[str, Any]]
    shortlisted_jobs: list[dict[str, Any]]
    selected_job: dict[str, Any]
    company_research: dict[str, Any]
    original_resume: str
    tailored_resume: str
    tailored_resume_pdf_path: str
    cover_letter: str
    application_answers: dict[str, Any]
    missing_information: list[str]
    approval_status: str  # "PENDING" | "APPROVED" | "REJECTED"
    application_status: str  # "DISCOVERED" | "ELIGIBLE" | "SHORTLISTED" | "PREPARING" | "AWAITING_APPROVAL" | "SUBMITTED"
    browser_state: dict[str, Any]
    application_id: int | None
    search_iteration: int
    target_count: int
    match_score: float
    match_breakdown: dict[str, Any]
    match_reason: str
    why_this_job: dict[str, Any]
    logs: list[dict[str, Any]]
