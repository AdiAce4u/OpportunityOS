from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.research_tools import research_company as tool_research

def company_research(state: JobState) -> JobState:
    """
    Company Research Agent Node:
    Conducts in-depth research on the shortlisted target company:
    - Company domain and size
    - Technological stack
    - Recent milestone news
    - Reputation & engineering culture
    """
    selected = state.get("selected_job")
    if not selected:
        return state
        
    company_name = selected.get("company", "")
    insights = tool_research(company_name)
    state["company_research"] = insights
    
    log_event(
        state,
        "CompanyResearchAgent",
        f"Gathered company intelligence on {company_name}: domain '{insights.get('domain')}', {len(insights.get('technology', []))} core technologies identified.",
        metadata={"news": insights.get("recent_news", [])[:1]}
    )
    return state
