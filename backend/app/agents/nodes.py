from app.models import Application, Job, UserProfile
from app.tools.search import search_many
from app.tools.llm import tailor_resume, generate_cover_letter, generate_answers

def log(state, message):
    state.setdefault("logs", []).append(message)

def load_profile(state, db):
    profile = db.get(UserProfile, state["profile_id"])
    if not profile:
        raise ValueError("Profile not found")
    state["profile"] = profile
    log(state, "✓ Loaded user profile")
    return state

def plan_queries(state):
    goal = state["goal"]
    roles = goal.get("roles") or ["software intern"]
    locations = goal.get("locations") or ["India"]
    skills = goal.get("skills") or []
    queries = []
    for role in roles:
        for location in locations:
            queries.append(f"{role} {location} {' '.join(skills[:3])}".strip())
        queries.append(f"{role} robotics AI")
        queries.append(f"{role} autonomous systems")
    state["search_queries"] = list(dict.fromkeys(queries))[:20]
    log(state, f"✓ Generated {len(state['search_queries'])} search queries")
    return state

def search(state):
    state["search_results"] = search_many(state["search_queries"])
    log(state, f"✓ Found {len(state['search_results'])} unique opportunities")
    return state

def check_eligibility(state):
    profile = state["profile"]
    eligible = []
    for job in state["search_results"]:
        rules = job.get("eligibility", {})
        year = profile.graduation_year
        if year is not None:
            if year < rules.get("graduation_year_min", 0):
                continue
            if year > rules.get("graduation_year_max", 9999):
                continue
        eligible.append(job)
    state["eligible_jobs"] = eligible
    log(state, f"✓ {len(eligible)} opportunities passed eligibility")
    return state

def rank_jobs(state):
    profile = state["profile"]
    goal = state["goal"]
    profile_skills = {x.lower() for x in (profile.skills or [])}
    wanted = {x.lower() for x in (goal.get("skills") or [])}
    locations = [x.lower() for x in (goal.get("locations") or [])]
    ranked = []

    for job in state["eligible_jobs"]:
        required = {x.lower() for x in job["required_skills"]}
        skill = len(profile_skills & required) / max(len(required), 1)
        target = len(wanted & required) / max(len(wanted), 1) if wanted else 1.0
        loc = 1.0 if not locations or any(x in job["location"].lower() for x in locations) else 0.5
        score = round(100 * (0.55*skill + 0.25*target + 0.20*loc), 1)
        reason = f"Skill match {skill:.0%}; target alignment {target:.0%}; location fit {loc:.0%}."
        ranked.append({"job": job, "score": score, "reason": reason})

    ranked.sort(key=lambda x: x["score"], reverse=True)
    state["ranked_jobs"] = ranked[:10]

    if ranked:
        best = ranked[0]
        state["selected_job"] = best["job"]
        state["match_score"] = best["score"]
        state["match_reason"] = best["reason"]

    log(state, f"✓ Ranked {len(ranked)} eligible opportunities")
    return state

def prepare_application(state, db):
    if not state.get("selected_job"):
        state["status"] = "NO_MATCH"
        log(state, "⚠ No suitable opportunity found")
        return state

    profile = state["profile"]
    job = state["selected_job"]

    state["tailored_resume"] = tailor_resume(profile, job)
    state["cover_letter"] = generate_cover_letter(profile, job)
    state["answers"] = generate_answers(profile, job)

    db_job = db.query(Job).filter(Job.external_id == job["external_id"]).first()
    if not db_job:
        db_job = Job(**job)
        db.add(db_job)
        db.commit()
        db.refresh(db_job)

    application = Application(
        job_id=db_job.id,
        status="AWAITING_APPROVAL",
        match_score=state["match_score"],
        match_reason=state["match_reason"],
        tailored_resume=state["tailored_resume"],
        cover_letter=state["cover_letter"],
        answers=state["answers"],
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    state["application_id"] = application.id
    state["status"] = "AWAITING_APPROVAL"
    log(state, "✓ Application package ready — waiting for human approval")
    return state
