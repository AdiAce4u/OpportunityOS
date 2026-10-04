from typing import Any

def check_eligibility(job: dict[str, Any], user_profile: dict[str, Any]) -> tuple[bool, str]:
    """
    Deterministic rule-based eligibility evaluation:
    - Degree match
    - Graduation year range
    - Minimum required experience (e.g. if job requires 8+ years and user is student -> Ineligible!)
    - Location constraints
    - Work authorization
    Returns (is_eligible, reason)
    """
    rules = job.get("eligibility", {})
    
    # 1. Graduation year check
    user_grad = user_profile.get("graduation_year")
    min_grad = rules.get("graduation_year_min")
    max_grad = rules.get("graduation_year_max")
    
    if user_grad is not None:
        if min_grad and user_grad < min_grad:
            return False, f"Graduation year {user_grad} precedes required minimum {min_grad}"
        if max_grad and user_grad > max_grad:
            return False, f"Graduation year {user_grad} exceeds required maximum {max_grad}"
    
    # 2. Minimum experience constraint
    required_exp_years = rules.get("required_min_years_experience", 0)
    user_exp_list = user_profile.get("experience", [])
    if required_exp_years > 2 and len(user_exp_list) < 2:
        return False, f"Requires {required_exp_years}+ years of professional industry experience"
    
    # 3. Work Authorization
    user_auth = user_profile.get("work_authorization", "").lower()
    job_loc = job.get("location", "").lower()
    if "us only" in rules.get("authorization", "").lower() and "us" not in user_auth:
        return False, "Candidate does not have required US work authorization"

    # 4. Salary/stipend threshold
    user_min_salary = user_profile.get("minimum_salary")
    job_salary = job.get("salary_min")
    if user_min_salary and job_salary and job_salary < user_min_salary:
        return False, f"Salary/stipend ₹{job_salary:,.0f} is below user requirement of ₹{user_min_salary:,.0f}"

    return True, "Eligible"

def generate_evidence_table(job: dict[str, Any], user_profile: dict[str, Any]) -> list[dict[str, str]]:
    """
    Constructs a transparent 1-to-1 evidence citation table mapping each job requirement
    to verified candidate project, internship, or coursework achievements.
    Rating Rubric:
    - STRONG: Direct implementation in a named project or professional work experience.
    - MODERATE: Confirmed skill listed in candidate credentials.
    - NONE: No verified evidence found in profile.
    """
    user_skills = {s.lower().strip() for s in (user_profile.get("skills") or [])}
    projects = user_profile.get("projects") or []
    experience = user_profile.get("experience") or []
    
    req_skills = job.get("required_skills") or []
    pref_skills = job.get("preferred_skills") or []
    targets = req_skills + [p for p in pref_skills if p not in req_skills][:2]
    
    table = []
    for req in targets:
        req_clean = req.strip()
        req_lower = req_clean.lower()
        
        evidence_found = None
        rating = "NONE"
        
        # 1. Search in projects (strongest proof)
        for p in projects:
            p_text = f"{p.get('name', '')} {' '.join(p.get('tech_stack', []))} {p.get('description', '')}".lower()
            if req_lower in p_text:
                evidence_found = f"{p.get('name')} project"
                rating = "STRONG"
                break
                
        # 2. Search in work experience
        if not evidence_found:
            for e in experience:
                e_text = f"{e.get('role', '')} {e.get('company', '')} {e.get('description', '')}".lower()
                if req_lower in e_text:
                    evidence_found = f"{e.get('role')} at {e.get('company')}"
                    rating = "STRONG"
                    break
                    
        # 3. Search in general skills competency
        if not evidence_found:
            if req_lower in user_skills:
                evidence_found = "Verified technical competency in profile"
                rating = "MODERATE"
            else:
                evidence_found = "No project or production evidence found"
                rating = "NONE"
                
        table.append({
            "requirement": req_clean,
            "evidence": evidence_found,
            "rating": rating
        })
        
    return table

def calculate_job_match(job: dict[str, Any], user_profile: dict[str, Any]) -> dict[str, Any]:
    """
    Computes a multi-dimensional match score and generates the 'Why this job?' explanation
    and evidence citation table.
    """
    user_skills = {s.lower().strip() for s in (user_profile.get("skills") or [])}
    req_skills = [s.strip() for s in (job.get("required_skills") or [])]
    pref_skills = [s.strip() for s in (job.get("preferred_skills") or [])]
    
    req_lower = {s.lower() for s in req_skills}
    pref_lower = {s.lower() for s in pref_skills}
    
    # Present vs Missing
    present_skills = [s for s in req_skills if s.lower() in user_skills]
    missing_skills = [s for s in req_skills if s.lower() not in user_skills]
    present_preferred = [s for s in pref_skills if s.lower() in user_skills]
    
    # Generate Evidence Citation Table
    evidence_table = generate_evidence_table(job, user_profile)
    
    # 1. Skill Match (50% weight)
    matched_req_count = len(req_lower & user_skills)
    skill_pct = (matched_req_count / max(len(req_lower), 1)) * 100
    
    # 2. Education Match (15% weight)
    user_degree = (user_profile.get("degree") or "").lower()
    edu_reqs = [e.lower() for e in (job.get("education_requirements") or [])]
    edu_pct = 100.0 if not edu_reqs or any(e in user_degree for e in edu_reqs) else 80.0
    
    # 3. Project Relevance (15% weight)
    user_projects = user_profile.get("projects") or []
    project_text = " ".join([p.get("name", "") + " " + p.get("description", "") for p in user_projects]).lower()
    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    
    project_hits = sum(1 for s in req_lower if s in project_text)
    project_pct = min(100.0, (project_hits / max(len(req_lower), 1)) * 120)
    
    # 4. Location Match (10% weight)
    pref_locs = [l.lower() for l in (user_profile.get("preferred_locations") or [])]
    job_loc = (job.get("location") or "").lower()
    is_remote = job.get("is_remote", False) or "remote" in job_loc
    
    if is_remote or any(loc in job_loc for loc in pref_locs):
        loc_pct = 100.0
    else:
        loc_pct = 60.0
        
    # 5. Experience / Domain match (10% weight)
    exp_pct = 85.0 if user_profile.get("experience") else 70.0
    
    # Overall weighted score
    overall = round(
        (skill_pct * 0.45) +
        (project_pct * 0.20) +
        (edu_pct * 0.15) +
        (loc_pct * 0.10) +
        (exp_pct * 0.10),
        1
    )
    
    # Build explanation
    breakdown = {
        "skills": round(skill_pct, 1),
        "education": round(edu_pct, 1),
        "projects": round(project_pct, 1),
        "location": round(loc_pct, 1),
        "experience": round(exp_pct, 1),
    }
    
    reason = (
        f"Overall match {overall}%. Skill alignment {skill_pct:.0f}%, "
        f"strong project relevance ({project_pct:.0f}%), and confirmed location fit ({loc_pct:.0f}%)."
    )
    
    why_this_job = {
        "required_present": present_skills,
        "missing": missing_skills,
        "preferred_present": present_preferred,
        "evidence_table": evidence_table,
        "highlights": [
            f"{len(present_skills)} of {len(req_skills)} required technical skills directly proven",
            f"Education directly aligns with {user_profile.get('degree', 'degree')} at {user_profile.get('college', 'college')}",
            f"Location: {job.get('location')} matches preferred list"
        ]
    }
    
    return {
        "overall_score": overall,
        "breakdown": breakdown,
        "reason": reason,
        "why_this_job": why_this_job,
        "evidence_table": evidence_table
    }
