"""
Configuration for Multi-Platform Autonomous Job Search Agent
Pre-configured categories for SDE, Data, Core Engineering, Finance, etc.
"""

ROLE_CATEGORIES = {
    "sde": [
        "Software Development Engineer",
        "Backend Engineer",
        "Frontend Engineer",
        "Full Stack Developer",
        "DevOps Engineer"
    ],
    "data": [
        "Data Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Analyst",
        "AI Engineer"
    ],
    "core": [
        "Embedded Software Engineer",
        "Hardware Engineer",
        "Robotics Engineer",
        "VLSI Design Engineer",
        "Mechanical Engineer"
    ],
    "finance": [
        "Quantitative Analyst",
        "Financial Analyst",
        "Risk Analyst",
        "Fintech Software Engineer",
        "Investment Banking Analyst"
    ]
}

DEFAULT_SETTINGS = {
    "sites": ["linkedin", "indeed", "glassdoor"],  # Multi-platform discovery
    "default_location": "India",
    "results_per_role": 5,
    "hours_old": 72,
    "db_path": "jobs_database.db",
    "output_dir": "results",
    "default_cv_path": "master_cv.md",
    "default_sort": "match"  # 'match' (CV similarity), 'salary' (decreasing stipend), 'recent'
}
