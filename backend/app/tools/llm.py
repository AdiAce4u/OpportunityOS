# Deterministic MVP provider. Replace these functions with an LLM adapter.

def tailor_resume(profile, job: dict) -> str:
    skills = profile.skills or []
    relevant = [
        s for s in skills
        if s.lower() in job["description"].lower()
        or any(s.lower() == r.lower() for r in job["required_skills"])
    ]
    relevant = relevant or skills[:6]
    return (
        "JOB-SPECIFIC RESUME\n\n"
        f"Candidate: {profile.name}\n"
        f"Target: {job['title']} — {job['company']}\n\n"
        f"Relevant skills: {', '.join(relevant)}\n\n"
        "Only user-supplied facts are used."
    )

def generate_cover_letter(profile, job: dict) -> str:
    skills = ", ".join((profile.skills or [])[:5])
    return (
        f"Dear {job['company']} Hiring Team,\n\n"
        f"I am interested in the {job['title']} position. "
        f"My background includes {skills}, which aligns with the role.\n\n"
        "I would welcome the opportunity to contribute to the team.\n\n"
        f"Regards,\n{profile.name}"
    )

def generate_answers(profile, job: dict) -> dict:
    return {
        "why_role": (
            f"I am interested in {job['title']} because it aligns with "
            f"my background in {', '.join((profile.skills or [])[:4])}."
        ),
        "relevant_experience": "Generated only from supplied profile information."
    }
