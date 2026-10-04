from app.tools.matching_tools import calculate_job_match, check_eligibility

def test_calculate_job_match():
    job = {
        "title": "Robotics Software Intern",
        "company": "XYZ Robotics",
        "location": "Bangalore",
        "is_remote": False,
        "description": "ROS2, Python, C++, navigation and SLAM",
        "required_skills": ["Python", "C++", "ROS2", "Robotics"],
        "preferred_skills": ["Navigation2", "Gazebo"],
        "education_requirements": ["B.Tech"],
    }
    
    profile = {
        "name": "Test Candidate",
        "degree": "B.Tech in CS",
        "college": "IIT",
        "skills": ["Python", "C++", "ROS2", "Robotics", "Linux"],
        "projects": [{"name": "ROS2 Robot", "description": "Quadruped with ROS2"}],
        "preferred_locations": ["Bangalore", "India"],
        "experience": [{"role": "Research Intern", "company": "Lab"}]
    }
    
    match = calculate_job_match(job, profile)
    assert match["overall_score"] >= 80.0
    assert "ROS2" in match["why_this_job"]["required_present"]
    assert match["breakdown"]["skills"] >= 90.0

def test_eligibility_filter():
    ineligible_senior_job = {
        "title": "Staff Robotics Engineer",
        "eligibility": {"graduation_year_max": 2020, "required_min_years_experience": 8}
    }
    
    student_profile = {
        "graduation_year": 2027,
        "experience": []
    }
    
    is_ok, reason = check_eligibility(ineligible_senior_job, student_profile)
    assert is_ok is False
    assert "Graduation year" in reason or "experience" in reason
