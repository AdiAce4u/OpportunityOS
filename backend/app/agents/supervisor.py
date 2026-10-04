from typing import Any
from app.agents.state import JobState
from app.core.logging import AgentActivityLogger
from app.tools.search_tools import get_user_profile, get_resume

def log_event(state: JobState, stage: str, message: str, level: str = "INFO", metadata: dict | None = None) -> None:
    event = AgentActivityLogger.format_log(stage, message, level, metadata)
    state.setdefault("logs", []).append(event)

def understand_goal(state: JobState) -> JobState:
    """
    Supervisor Agent Node:
    - Parses user goal and constraints
    - Loads candidate verified profile
    - Constructs structured search plan
    """
    profile_id = state.get("profile_id")
    profile = get_user_profile(profile_id)
    if not profile:
        raise ValueError(f"Profile {profile_id} not found in database.")
    
    state["user_profile"] = profile
    state["original_resume"] = get_resume(profile_id)
    
    goal = state.get("search_goal") or {}
    roles = goal.get("roles") or profile.get("preferred_roles") or ["Robotics Intern", "ML Intern"]
    locations = goal.get("locations") or profile.get("preferred_locations") or ["India", "Bangalore", "Remote"]
    skills = goal.get("skills") or profile.get("skills") or ["Python", "C++", "ROS2"]
    min_stipend = goal.get("minimum_salary") or profile.get("minimum_salary") or 40000.0
    target_count = goal.get("target_count") or 15
    
    structured_plan = {
        "roles": roles,
        "locations": locations,
        "minimum_stipend": min_stipend,
        "skills": skills,
        "target_count": target_count
    }
    
    state["search_goal"] = structured_plan
    state["target_count"] = target_count
    state["search_iteration"] = 1
    state["discovered_jobs"] = []
    
    log_event(
        state,
        "Supervisor",
        f"Structured search plan formulated: target {target_count} opportunities across {len(roles)} roles in {', '.join(locations[:2])}.",
        metadata=structured_plan
    )
    return state
