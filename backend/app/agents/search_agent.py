from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.search_tools import generate_search_queries as tool_generate_queries, search_job_source

def generate_search_queries(state: JobState) -> JobState:
    """
    Search Agent Node: Generates initial targeted search queries.
    """
    plan = state["search_goal"]
    iteration = state.get("search_iteration", 1)
    queries = tool_generate_queries(plan, iteration=iteration)
    
    state["search_queries"] = queries
    log_event(
        state,
        "JobSearchAgent",
        f"Generated {len(queries)} dynamic search queries (Iteration {iteration}).",
        metadata={"queries": queries[:4]}
    )
    return state

def search_jobs(state: JobState) -> JobState:
    """
    Search Agent Node: Executes multi-query search across sources.
    """
    queries = state.get("search_queries", [])
    collected = list(state.get("discovered_jobs", []))
    
    new_found = 0
    for q in queries:
        results = search_job_source(q)
        for r in results:
            if not any(x.get("external_id") == r.get("external_id") for x in collected):
                collected.append(r)
                new_found += 1
                
    state["discovered_jobs"] = collected
    log_event(
        state,
        "JobSearchAgent",
        f"Searched across job sources: {len(collected)} unique opportunities collected (+{new_found} new)."
    )
    return state

def evaluate_search_results(state: JobState) -> JobState:
    """
    Evaluates whether enough opportunities have been gathered.
    """
    count = len(state.get("discovered_jobs", []))
    target = state.get("target_count", 10)
    iteration = state.get("search_iteration", 1)
    
    log_event(
        state,
        "JobSearchAgent",
        f"Opportunity check: {count}/{target} target opportunities in pool (Iteration {iteration})."
    )
    return state

def should_search_again(state: JobState) -> str:
    """
    Conditional edge:
    If discovered jobs < target_count AND iteration < 3: loop back!
    Else: continue to deduplication and extraction.
    """
    count = len(state.get("discovered_jobs", []))
    target = state.get("target_count", 10)
    iteration = state.get("search_iteration", 1)
    
    if count < target and iteration < 2:
        return "generate_new_queries"
    return "deduplicate_jobs"

def generate_new_queries(state: JobState) -> JobState:
    """
    Refines queries when target count not met.
    """
    state["search_iteration"] = state.get("search_iteration", 1) + 1
    plan = state["search_goal"]
    new_queries = tool_generate_queries(plan, iteration=state["search_iteration"])
    state["search_queries"] = new_queries
    
    log_event(
        state,
        "JobSearchAgent",
        f"Expanding search scope with {len(new_queries)} specialized queries (Iteration {state['search_iteration']}).",
        metadata={"queries": new_queries[:3]}
    )
    return state

def deduplicate_jobs(state: JobState) -> JobState:
    """
    Deduplicates gathered jobs across sources.
    """
    raw_list = state.get("discovered_jobs", [])
    seen = set()
    deduped = []
    for item in raw_list:
        eid = item.get("external_id") or item.get("url")
        if eid and eid not in seen:
            seen.add(eid)
            deduped.append(item)
            
    state["discovered_jobs"] = deduped
    log_event(
        state,
        "JobSearchAgent",
        f"Deduplicated pool: {len(deduped)} distinct job opportunities ready for analysis."
    )
    return state
