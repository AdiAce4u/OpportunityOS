from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.extraction_tools import extract_job_information as tool_extract

def extract_job_information(state: JobState) -> JobState:
    """
    Job Information Extraction Agent Node:
    Normalizes each job record into structured format.
    """
    raw_jobs = state.get("discovered_jobs", [])
    extracted_jobs = []
    
    for j in raw_jobs:
        norm = tool_extract(j)
        if norm:
            extracted_jobs.append(norm)
            
    state["discovered_jobs"] = extracted_jobs
    log_event(
        state,
        "JobInfoAgent",
        f"Extracted detailed job specs, requirements, and deadlines for {len(extracted_jobs)} listings."
    )
    return state
