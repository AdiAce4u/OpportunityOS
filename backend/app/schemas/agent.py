from typing import Any
from pydantic import BaseModel, Field

class SearchGoal(BaseModel):
    roles: list[str] = Field(default_factory=lambda: ["Robotics Intern", "Robotics Software Intern", "ML Intern", "AI Intern"])
    locations: list[str] = Field(default_factory=lambda: ["India", "Bangalore", "Hyderabad", "Remote"])
    skills: list[str] = Field(default_factory=lambda: ["Python", "C++", "ROS2", "Machine Learning"])
    minimum_salary: float | None = 40000.0
    target_count: int = 15

class AgentRunRequest(BaseModel):
    profile_id: int
    goal: SearchGoal | None = None
    free_form_goal: str | None = None

class AgentStepLog(BaseModel):
    timestamp: str
    stage: str
    message: str
    level: str = "INFO"
    metadata: dict[str, Any] = Field(default_factory=dict)

class AgentRunResponse(BaseModel):
    status: str
    logs: list[dict[str, Any]] = Field(default_factory=list)
    shortlisted_jobs: list[dict[str, Any]] = Field(default_factory=list)
    selected_job: dict[str, Any] | None = None
    application_id: int | None = None
    match_score: float | None = None
    match_reason: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    iterations_used: int = 1
