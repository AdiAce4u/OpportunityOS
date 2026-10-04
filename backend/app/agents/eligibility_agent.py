from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.matching_tools import check_eligibility as tool_check_eligibility

def check_eligibility(state: JobState) -> JobState:
    """
    Eligibility Agent Node:
    Applies strict deterministic safety filters:
    - Candidate graduation year & degree
    - Work authorization
    - Minimum experience requirements
    - Stipend/salary floor
    Discarding ineligible jobs prevents hallucinations and wasted effort.
    """
    profile = state["user_profile"]
    all_jobs = state.get("discovered_jobs", [])
    
    eligible = []
    discarded = []
    
    for job in all_jobs:
        is_ok, reason = tool_check_eligibility(job, profile)
        if is_ok:
            eligible.append(job)
        else:
            discarded.append({"job": job["title"], "company": job["company"], "reason": reason})
            
    state["eligible_jobs"] = eligible
    
    log_event(
        state,
        "EligibilityAgent",
        f"Verified eligibility: {len(eligible)} opportunities passed criteria ({len(discarded)} discarded).",
        metadata={"discarded_sample": discarded[:3]}
    )
    return state
