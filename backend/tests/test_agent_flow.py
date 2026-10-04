from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.agents.graph import opportunity_graph
from app.models import UserProfile

def test_opportunity_graph_flow():
    init_db()
    db = SessionLocal()
    seed_database(db)
    profile = db.query(UserProfile).first()
    db.close()
    
    assert profile is not None
    
    initial_state = {
        "profile_id": profile.id,
        "search_goal": {
            "roles": ["Robotics Intern", "ML Intern"],
            "locations": ["Bangalore", "India"],
            "skills": ["Python", "ROS2", "C++"],
            "minimum_salary": 40000.0,
            "target_count": 5
        },
        "logs": [],
        "search_iteration": 1,
        "target_count": 5
    }
    
    final_state = opportunity_graph.invoke(initial_state)
    
    assert final_state["application_status"] == "AWAITING_APPROVAL"
    assert len(final_state["discovered_jobs"]) > 0
    assert len(final_state["eligible_jobs"]) > 0
    assert len(final_state["shortlisted_jobs"]) > 0
    assert final_state["selected_job"] is not None
    assert final_state["match_score"] >= 70.0
    assert "ROS2" in final_state["tailored_resume"]
    assert "Dear" in final_state["cover_letter"]
