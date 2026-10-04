"""
LangGraph Multi-Agent Orchestrator for OpportunityOS.
Implements the autonomous supervisor & agentic looping workflow:
- Supervisor goal parsing
- Search loop with dynamic query refinement
- Information extraction & normalization
- Deterministic eligibility gating
- Multi-dimensional ranking & match reasoning
- In-depth company research
- Truth-preserving resume tailoring & PDF rendering
- Application packaging (cover letter, answers, missing info detection)
- Human Review checkpoint
- Browser automation & tracking post-approval
"""

from langgraph.graph import StateGraph, START, END
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

def build_opportunity_graph():
    """
    Builds the autonomous discovery, research, and application preparation graph.
    Loops until enough jobs are found or max iterations reached, then prepares the application package.
    Pauses before browser submission for Human-in-the-Loop review.
    """
    builder = StateGraph(JobState)
    
    # 1. Supervisor
    builder.add_node("understand_goal", understand_goal)
    
    # 2. Search Agent (Looping)
    builder.add_node("generate_search_queries", generate_search_queries)
    builder.add_node("search_jobs", search_jobs)
    builder.add_node("evaluate_search_results", evaluate_search_results)
    builder.add_node("generate_new_queries", generate_new_queries)
    builder.add_node("deduplicate_jobs", deduplicate_jobs)
    
    # 3. Extraction Agent
    builder.add_node("extract_job_information", extract_job_information)
    
    # 4. Eligibility Agent
    builder.add_node("check_eligibility", check_eligibility)
    
    # 5. Matching Agent
    builder.add_node("calculate_match", calculate_match)
    
    # 6. Company Research Agent
    builder.add_node("company_research", company_research)
    
    # 7. Resume Agent
    builder.add_node("tailor_resume", tailor_resume)
    
    # 8. Application Prep Agent
    builder.add_node("generate_application", generate_application)
    
    # Graph Edges & Flow
    builder.add_edge(START, "understand_goal")
    builder.add_edge("understand_goal", "generate_search_queries")
    builder.add_edge("generate_search_queries", "search_jobs")
    builder.add_edge("search_jobs", "evaluate_search_results")
    
    # Conditional loop: if not enough opportunities -> generate_new_queries -> search_jobs
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

def build_submission_graph():
    """
    Builds the post-approval execution graph:
    browser_agent -> validate_submission -> submit_application -> save_application -> schedule_follow_up
    """
    builder = StateGraph(JobState)
    builder.add_node("browser_agent_submit", browser_agent_submit)
    builder.add_node("schedule_follow_up", schedule_follow_up)
    
    builder.add_edge(START, "browser_agent_submit")
    builder.add_edge("browser_agent_submit", "schedule_follow_up")
    builder.add_edge("schedule_follow_up", END)
    
    return builder.compile()

# Compile singletons
opportunity_graph = build_opportunity_graph()
submission_graph = build_submission_graph()
