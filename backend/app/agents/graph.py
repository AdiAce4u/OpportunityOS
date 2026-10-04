"""
Multi-Agent Orchestrator for OpportunityOS.
Implements autonomous supervisor & agentic looping workflow with fallback to pure Python graph execution.
"""

import logging
from typing import Dict, Any, Callable

from app.agents.state import JobState
from app.agents.supervisor import understand_goal
from app.agents.search_agent import (
    generate_search_queries,
    search_jobs,
    evaluate_search_results,
    should_search_again,
    generate_new_queries,
    deduplicate_jobs,
)
from app.agents.extraction_agent import extract_job_information
from app.agents.eligibility_agent import check_eligibility
from app.agents.matching_agent import calculate_match
from app.agents.research_agent import company_research
from app.agents.resume_agent import tailor_resume
from app.agents.application_agent import generate_application
from app.agents.browser_agent import browser_agent_submit
from app.agents.tracker_agent import schedule_follow_up

logger = logging.getLogger("OpportunityOS.Agents.Graph")

class SimpleGraph:
    """Lightweight pure-Python fallback graph orchestrator."""
    def __init__(self, mode="discovery"):
        self.mode = mode

    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        curr = dict(state)
        curr["logs"] = curr.get("logs", [])

        if self.mode == "discovery":
            # 1. Supervisor
            curr = understand_goal(curr)
            # 2. Search loop
            curr = generate_search_queries(curr)
            curr = search_jobs(curr)
            curr = evaluate_search_results(curr)
            
            # Condition check
            decision = should_search_again(curr)
            if decision == "generate_new_queries":
                curr = generate_new_queries(curr)
                curr = search_jobs(curr)
                
            curr = deduplicate_jobs(curr)
            # 3. Extraction
            curr = extract_job_information(curr)
            # 4. Eligibility
            curr = check_eligibility(curr)
            # 5. Matching & Ranking
            curr = calculate_match(curr)
            # 6. Company Research
            curr = company_research(curr)
            # 7. Resume Agent
            curr = tailor_resume(curr)
            # 8. Application Agent
            curr = generate_application(curr)
            return curr

        elif self.mode == "submission":
            curr = browser_agent_submit(curr)
            curr = schedule_follow_up(curr)
            return curr

        return curr

def build_opportunity_graph():
    try:
        from langgraph.graph import StateGraph, START, END
        builder = StateGraph(JobState)
        builder.add_node("understand_goal", understand_goal)
        builder.add_node("generate_search_queries", generate_search_queries)
        builder.add_node("search_jobs", search_jobs)
        builder.add_node("evaluate_search_results", evaluate_search_results)
        builder.add_node("generate_new_queries", generate_new_queries)
        builder.add_node("deduplicate_jobs", deduplicate_jobs)
        builder.add_node("extract_job_information", extract_job_information)
        builder.add_node("check_eligibility", check_eligibility)
        builder.add_node("calculate_match", calculate_match)
        builder.add_node("company_research", company_research)
        builder.add_node("tailor_resume", tailor_resume)
        builder.add_node("generate_application", generate_application)

        builder.add_edge(START, "understand_goal")
        builder.add_edge("understand_goal", "generate_search_queries")
        builder.add_edge("generate_search_queries", "search_jobs")
        builder.add_edge("search_jobs", "evaluate_search_results")
        builder.add_conditional_edges(
            "evaluate_search_results",
            should_search_again,
            {
                "generate_new_queries": "generate_new_queries",
                "deduplicate_jobs": "deduplicate_jobs"
            }
        )
        builder.add_edge("generate_new_queries", "search_jobs")
        builder.add_edge("deduplicate_jobs", "extract_job_information")
        builder.add_edge("extract_job_information", "check_eligibility")
        builder.add_edge("check_eligibility", "calculate_match")
        builder.add_edge("calculate_match", "company_research")
        builder.add_edge("company_research", "tailor_resume")
        builder.add_edge("tailor_resume", "generate_application")
        builder.add_edge("generate_application", END)
        return builder.compile()
    except Exception as e:
        logger.debug(f"Using pure-Python workflow graph: {e}")
        return SimpleGraph(mode="discovery")

def build_submission_graph():
    try:
        from langgraph.graph import StateGraph, START, END
        builder = StateGraph(JobState)
        builder.add_node("browser_agent_submit", browser_agent_submit)
        builder.add_node("schedule_follow_up", schedule_follow_up)
        builder.add_edge(START, "browser_agent_submit")
        builder.add_edge("browser_agent_submit", "schedule_follow_up")
        builder.add_edge("schedule_follow_up", END)
        return builder.compile()
    except Exception as e:
        logger.debug(f"Using pure-Python submission graph: {e}")
        return SimpleGraph(mode="submission")

# Compile singletons
opportunity_graph = build_opportunity_graph()
submission_graph = build_submission_graph()
