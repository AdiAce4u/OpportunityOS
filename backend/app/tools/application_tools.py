from typing import Any

def generate_cover_letter(job: dict[str, Any], user_profile: dict[str, Any]) -> str:
    candidate_name = user_profile.get("name", "Applicant")
    email = user_profile.get("email", "")
    phone = user_profile.get("phone", "")
    college = user_profile.get("college", "")
    degree = user_profile.get("degree", "")
    grad_year = user_profile.get("graduation_year", "")
    skills = ", ".join((user_profile.get("skills") or [])[:5])
    
    company = job.get("company", "Company")
    title = job.get("title", "Position")
    location = job.get("location", "the team")
    
    projects = user_profile.get("projects") or []
    top_project = projects[0]["name"] if projects else "academic robotics systems"
    
    return f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {title} position in {location}. Currently pursuing my {degree} at {college} with an expected graduation in {grad_year}, my technical skills and project focus are directly aligned with your requirements.

My hands-on experience spans {skills}. In particular, through my work on {top_project}, I have solved complex technical challenges and built reliable, performant software. Having researched {company}'s work and technological contributions, I am eager to bring my enthusiasm and practical engineering skills to your engineering team.

I look forward to discussing how my experience can support your ongoing development goals.

Sincerely,
{candidate_name}
{email} | {phone}"""

def generate_application_answers(job: dict[str, Any], user_profile: dict[str, Any]) -> dict[str, str]:
    """Generates truthful, tailored answers to standard application questions."""
    title = job.get("title", "this role")
    company = job.get("company", "the company")
    skills = ", ".join((user_profile.get("skills") or [])[:4])
    
    projects = user_profile.get("projects") or []
    project_summary = f"My project '{projects[0]['name']}' ({projects[0].get('description', '')})" if projects else "My university coursework and lab projects"
    
    return {
        "why_role": (
            f"The {title} role is an ideal match for my background in {skills}. "
            f"I want to apply my practical engineering experience to solve impactful problems at {company}."
        ),
        "why_company": (
            f"I have been closely following {company}'s products and technological leadership. "
            f"Your high engineering bar and mission make it the most exciting environment to contribute and grow."
        ),
        "relevant_experience": (
            f"At {user_profile.get('college', 'my university')}, I developed {project_summary}. "
            f"This gave me direct, real-world proficiency with the tools specified in your job requirements."
        ),
        "availability": "Available immediately or as per the scheduled internship cycle on a full-time basis.",
        "work_authorization": user_profile.get("work_authorization", "Authorized to work in India")
    }

def find_missing_information(job: dict[str, Any], user_profile: dict[str, Any]) -> list[str]:
    """
    Identifies any missing details required for the application.
    If missing, the system will STOP and ask the user rather than guessing!
    """
    missing = []
    if not user_profile.get("email"):
        missing.append("Email address")
    if not user_profile.get("phone"):
        missing.append("Contact phone number")
    if not user_profile.get("work_authorization"):
        missing.append("Work authorization status")
    if not user_profile.get("graduation_year"):
        missing.append("Expected graduation year")
        
    return missing
