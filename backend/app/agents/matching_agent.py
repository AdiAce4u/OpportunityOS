from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.matching_tools import calculate_job_match as tool_calculate_match
from app.core.config import settings

def calculate_match(state: JobState) -> JobState:
    """
    Matching & Ranking Agent Node:
    Computes fit breakdown and ranks opportunities.
    """
    profile = state["user_profile"]
    eligible = state.get("eligible_jobs", [])
    threshold = settings.match_threshold
    
    ranked = []
    for job in eligible:
        match_data = tool_calculate_match(job, profile)
        score = match_data["overall_score"]
        if score >= threshold:
            ranked.append({
                "job": job,
                "score": score,
                "breakdown": match_data["breakdown"],
                "reason": match_data["reason"],
                "why_this_job": match_data["why_this_job"]
            })
            
    ranked.sort(key=lambda x: x["score"], reverse=True)
    state["shortlisted_jobs"] = ranked
    
    if ranked:
        best = ranked[0]
        state["selected_job"] = best["job"]
        state["match_score"] = best["score"]
        state["match_breakdown"] = best["breakdown"]
        state["match_reason"] = best["reason"]
        state["why_this_job"] = best["why_this_job"]
        
        log_event(
            state,
            "MatchingAgent",
            f"Ranked {len(ranked)} qualifying roles. Selected top match: {best['job']['title']} at {best['job']['company']} ({best['score']}% match).",
            metadata={"top_candidate": best["job"]["title"], "score": best["score"]}
        )
    else:
        state["selected_job"] = {}
        log_event(
            state,
            "MatchingAgent",
            "No opportunities cleared the match threshold.",
            level="WARNING"
        )
        
    return state
