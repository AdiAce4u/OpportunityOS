import os

APP_HOST = os.getenv("APP_HOST", "https://opportunityos1.onrender.com").rstrip("/")

MOCK_JOBS = [
    {
        "external_id": "xyz-robotics-001",
        "title": "Robotics Software Intern",
        "company": "XYZ Robotics",
        "location": "Bangalore",
        "salary_text": "₹50,000/month",
        "description": "Robot autonomy, ROS2, Python, C++ and simulation.",
        "url": f"{APP_HOST}/api/mock-apply/xyz-robotics-001",
        "required_skills": ["Python","C++","ROS2","Robotics"],
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028}
    },
    {
        "external_id": "abc-ai-002",
        "title": "Machine Learning Intern",
        "company": "ABC AI",
        "location": "Remote",
        "salary_text": "₹45,000/month",
        "description": "ML pipelines, Python services and model evaluation.",
        "url": f"{APP_HOST}/api/mock-apply/abc-ai-002",
        "required_skills": ["Python","Machine Learning","SQL"],
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028}
    },
    {
        "external_id": "def-auto-003",
        "title": "Autonomous Systems Intern",
        "company": "DEF Autonomy",
        "location": "Hyderabad",
        "salary_text": "₹55,000/month",
        "description": "Perception, controls, ROS2 and autonomous navigation.",
        "url": f"{APP_HOST}/api/mock-apply/def-auto-003",
        "required_skills": ["ROS2","C++","Python","Controls","Robotics"],
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028}
    },
    {
        "external_id": "ghi-data-004",
        "title": "Data Science Intern",
        "company": "GHI Analytics",
        "location": "Pune",
        "salary_text": "₹35,000/month",
        "description": "Data analysis, Python, SQL and machine learning.",
        "url": f"{APP_HOST}/api/mock-apply/ghi-data-004",
        "required_skills": ["Python","SQL","Machine Learning"],
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2029}
    }
]

def search_jobs(query: str) -> list[dict]:
    tokens = {x for x in query.lower().replace(","," ").split() if len(x) > 2}
    scored = []
    for job in MOCK_JOBS:
        text = " ".join([
            job["title"], job["company"], job["location"],
            job["description"], " ".join(job["required_skills"])
        ]).lower()
        score = sum(token in text for token in tokens)
        if score:
            scored.append((score, job))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [job for _, job in scored]
