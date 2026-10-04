import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import UserProfile
from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.agents.graph import opportunity_graph

logger = logging.getLogger("OpportunityOS.API.Agent")
router = APIRouter(prefix="/agent", tags=["Agent"])

# Global flag for kill-switch
AGENT_KILL_SWITCH = False

@router.post("/run", response_model=AgentRunResponse)
def run_agent_workflow(request: AgentRunRequest, db: Session = Depends(get_db)):
    """
    Triggers the autonomous OpportunityOS multi-agent workflow:
    Supervisor -> Search loop -> Extraction -> Eligibility -> Matching & Ranking ->
    Company Research -> Resume Tailoring -> Application Prep -> Human Approval Pause
    """
    global AGENT_KILL_SWITCH
    AGENT_KILL_SWITCH = False
    
    profile = db.get(UserProfile, request.profile_id)
    if not profile:
        profile = db.query(UserProfile).first()
        if not profile:
            raise HTTPException(404, "No candidate profile found. Please create one or upload a resume first.")

    goal_dict = request.goal.model_dump() if request.goal else {
        "roles": profile.preferred_roles or ["Robotics Intern", "Robotics Software Intern", "ML Intern"],
        "locations": profile.preferred_locations or ["India", "Bangalore", "Hyderabad", "Remote"],
        "skills": profile.skills or ["Python", "C++", "ROS2", "Machine Learning"],
        "minimum_salary": profile.minimum_salary or 40000.0,
        "target_count": 12
    }

    if request.free_form_goal:
        goal_text = request.free_form_goal.strip()
        goal_dict["free_form_goal"] = goal_text
        
        # Infer target roles from free-form goal keywords
        inferred_roles = []
        low = goal_text.lower()
        if "robot" in low or "ros" in low:
            inferred_roles.extend(["Robotics Intern", "Robotics Software Intern"])
        if any(k in low for k in ["ai", "ml", "machine learning", "deep learning", "vision"]):
            inferred_roles.extend(["ML Intern", "AI Engineer Intern"])
        if any(k in low for k in ["embedded", "firmware", "hardware"]):
            inferred_roles.extend(["Embedded Systems Intern", "Firmware Engineer"])
        if any(k in low for k in ["full-stack", "fullstack", "software", "backend", "frontend", "sde"]):
            inferred_roles.extend(["Software Engineering Intern", "Full-Stack Engineer"])
            
        if inferred_roles:
            goal_dict["roles"] = list(dict.fromkeys(inferred_roles + goal_dict.get("roles", [])))
            
        # Parse salary threshold if present in text
        import re
        sal_match = re.search(r"(?:₹|rs\.?|inr)\s*([\d,]+)", goal_text, re.IGNORECASE)
        if sal_match:
            try:
                goal_dict["minimum_salary"] = float(sal_match.group(1).replace(",", ""))
            except ValueError:
                pass

    initial_state = {
        "profile_id": profile.id,
        "search_goal": goal_dict,
        "logs": [],
        "search_iteration": 1,
        "target_count": goal_dict.get("target_count", 12)
    }

    try:
        final_state = opportunity_graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"Error in multi-agent workflow execution: {e}", exc_info=True)
        raise HTTPException(500, f"Agent execution error: {str(e)}")

    return AgentRunResponse(
        status=final_state.get("application_status", "AWAITING_APPROVAL"),
        logs=final_state.get("logs", []),
        shortlisted_jobs=final_state.get("shortlisted_jobs", []),
        selected_job=final_state.get("selected_job"),
        application_id=final_state.get("application_id"),
        match_score=final_state.get("match_score"),
        match_reason=final_state.get("match_reason"),
        missing_information=final_state.get("missing_information", []),
        iterations_used=final_state.get("search_iteration", 1)
    )

@router.post("/stop")
def trigger_kill_switch():
    """Emergency kill switch allowing user to halt any active agent operations."""
    global AGENT_KILL_SWITCH
    AGENT_KILL_SWITCH = True
    return {"status": "STOPPED", "message": "Kill switch triggered. Agent loop halted safely."}
