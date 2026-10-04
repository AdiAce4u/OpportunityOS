import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from app.models import UserProfile, Job, Application, FollowUpEvent
from app.tools.cv_parser_engine import MasterCVParser
from app.tools.portal_search_engine import ROLE_CATEGORIES, CVProjectMatcher, CompensationParser

def sync_agent_db_jobs(db, projects):
    """Imports all jobs from job-search-agent/jobs_database.db and seeds Consult track."""
    matcher = CVProjectMatcher(projects)
    agent_db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "job-search-agent", "jobs_database.db")
    
    imported_count = 0
    if os.path.exists(agent_db_path):
        try:
            conn = sqlite3.connect(agent_db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM jobs")
            rows = cur.fetchall()
            for r in rows:
                d = dict(r)
                title = d.get("title") or "Software Role"
                company = d.get("company") or "Technology Co"
                cat_raw = d.get("category") or "sde"
                cat = "software" if cat_raw in ["sde", "software"] else cat_raw
                ext_id = d.get("id") or f"{d.get('site', 'portal')}-{uuid.uuid5(uuid.NAMESPACE_DNS, title + company).hex[:10]}"

                existing = db.query(Job).filter((Job.external_id == ext_id) | ((Job.title == title) & (Job.company == company))).first()
                if not existing:
                    match_info = matcher.match_job_description(title, d.get("description") or "")
                    comp_info = CompensationParser.parse_compensation(d)
                    
                    job = Job(
                        external_id=ext_id,
                        title=title,
                        company=company,
                        location=d.get("location") or "India",
                        is_remote=bool(d.get("is_remote")),
                        category=cat,
                        search_term=d.get("search_term") or title,
                        site=d.get("site") or "linkedin",
                        match_score=match_info.get("match_score", 82.0),
                        best_matching_project=match_info.get("best_project", "Featured Project"),
                        best_project_domain=match_info.get("best_project_domain", cat),
                        matched_keywords=match_info.get("matched_keywords", []),
                        salary_text=comp_info.get("display_salary", "Competitive"),
                        display_salary=comp_info.get("display_salary", "Competitive"),
                        normalized_salary=comp_info.get("normalized_yearly_salary", 0.0),
                        description=d.get("description") or f"{title} at {company}",
                        required_skills=match_info.get("matched_keywords") or ["System Design", "Problem Solving"],
                        preferred_skills=["Communication", "Docker"],
                        education_requirements=["B.Tech", "Degree"],
                        url=d.get("job_url") or "",
                        source="job_search_agent_db"
                    )
                    db.add(job)
                    imported_count += 1
            conn.close()
            db.commit()
        except Exception as e:
            pass

    # Ensure rich Consult track openings exist
    consult_openings = [
        ("McKinsey & Company", "Business Analyst / Management Consultant", "₹22.0 - 30.0 LPA", "Gurugram", "https://www.mckinsey.com/careers"),
        ("Boston Consulting Group (BCG)", "Strategy Consulting Analyst - Technology & Ops", "₹24.0 - 32.0 LPA", "Mumbai", "https://careers.bcg.com"),
        ("Bain & Company", "Associate Consultant - Digital Transformation", "₹22.0 - 28.0 LPA", "Bangalore", "https://www.bain.com/careers"),
        ("Dalberg Advisors", "Strategy & Development Consultant", "₹16.0 - 22.0 LPA", "New Delhi", "https://dalberg.com/careers"),
        ("Deloitte Strategy & AI", "Technology Strategy Consulting Analyst", "₹14.0 - 20.0 LPA", "Hyderabad", "https://jobs2.deloitte.com"),
        ("Kearney", "Operations & Supply Chain Consulting Associate", "₹20.0 - 28.0 LPA", "Mumbai", "https://www.kearney.com/careers"),
        ("PwC Advisory", "Business Transformation & Strategy Consultant", "₹15.0 - 22.0 LPA", "Bangalore", "https://pwc.com/careers")
    ]
    for comp, title, sal, loc, url in consult_openings:
        ext_id = f"consult-{uuid.uuid5(uuid.NAMESPACE_DNS, title + comp).hex[:10]}"
        existing = db.query(Job).filter((Job.external_id == ext_id) | ((Job.title == title) & (Job.company == comp))).first()
        if not existing:
            match_info = matcher.match_job_description(title, "Consulting, business intelligence, strategy, operations")
            job = Job(
                external_id=ext_id,
                title=title,
                company=comp,
                location=loc,
                category="consult",
                search_term="Management Consultant",
                site="linkedin",
                match_score=match_info.get("match_score", 85.0),
                best_matching_project=match_info.get("best_project", "Predictive Income Modelling / BI Analysis"),
                best_project_domain="consult",
                matched_keywords=match_info.get("matched_keywords", ["Strategy", "Analytics"]),
                salary_text=sal,
                display_salary=sal,
                description=f"Strategic consulting role at {comp}. Driving digital transformation, market strategy, and operational improvements for enterprise clients.",
                required_skills=["Strategic Thinking", "Data Analysis", "Python", "Presentation"],
                url=url,
                source="portal_linkedin"
            )
            db.add(job)
    db.commit()

def seed_database(db):
    """Initializes OpportunityOS database with Master CV projects, 5 tracks of jobs, and sample application."""
    profile = db.query(UserProfile).first()
    
    master_cv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "job-search-agent", "uploaded_master_cv.md")
    master_text = ""
    if os.path.exists(master_cv_path):
        with open(master_cv_path, "r", encoding="utf-8", errors="ignore") as f:
            master_text = f.read()

    parsed_cv = MasterCVParser.parse_full_master_cv(master_text) if master_text else None

    if not profile:
        profile = UserProfile(
            name=parsed_cv.get("name") if parsed_cv else "Vaibhav Anand",
            email=parsed_cv.get("email") if parsed_cv else "vaibhav.anand@example.com",
            phone=parsed_cv.get("phone") if parsed_cv else "+91 9876543210",
            graduation_year=parsed_cv.get("graduation_year") if parsed_cv else 2028,
            degree=parsed_cv.get("degree") if parsed_cv else "B.Tech in Mechanical Engineering",
            college=parsed_cv.get("college") if parsed_cv else "IIT Kharagpur",
            cgpa=parsed_cv.get("cgpa") if parsed_cv else 8.39,
            skills=parsed_cv.get("skills") if parsed_cv else [
                "Python", "C++", "PyTorch", "ROS2", "Machine Learning", "FastAPI",
                "Deep Learning", "Docker", "Node.js", "SolidWorks", "Computer Vision"
            ],
            projects=parsed_cv.get("projects") if parsed_cv else [],
            categorized_projects=parsed_cv.get("projects") if parsed_cv else [],
            experience=parsed_cv.get("experience") if parsed_cv else [
                {
                    "role": "Research Intern",
                    "company": "Carnegie Mellon University",
                    "duration": "Nov 2025 - Mar 2026",
                    "description": "Developed gradient-derived LLM watermarking and antidistillation framework."
                }
            ],
            preferred_roles=[
                "Software Development Engineer",
                "Machine Learning Engineer",
                "Robotics Software Engineer",
                "Data Scientist",
                "Quantitative Analyst",
                "Management Consultant"
            ],
            preferred_locations=["India", "Bangalore", "Hyderabad", "Remote", "Gurugram", "Mumbai"],
            remote_preference=True,
            minimum_salary=45000.0,
            work_authorization="Eligible to work in India",
            prefer_companies=["NVIDIA", "Uber", "McKinsey", "Razorpay", "XYZ Robotics", "Tower Research"],
            avoid_companies=[],
            resume_filename="Vaibhav_Anand_Master_CV.md",
            master_cv_markdown=master_text or "Master CV loaded."
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    elif parsed_cv and not profile.categorized_projects:
        profile.projects = parsed_cv.get("projects", [])
        profile.categorized_projects = parsed_cv.get("projects", [])
        profile.skills = list(set((profile.skills or []) + (parsed_cv.get("skills") or [])))
        profile.master_cv_markdown = master_text
        db.commit()

    # Sync all jobs from job-search-agent/jobs_database.db
    sync_agent_db_jobs(db, profile.categorized_projects or profile.projects or [])

    # Seed an application ready for review if none exist
    if db.query(Application).count() == 0:
        first_job = db.query(Job).first()
        if first_job and profile:
            from app.tools.resume_tailor_engine import ResumeTailorEngine
            job_dict = {
                "id": first_job.id,
                "title": first_job.title,
                "company": first_job.company,
                "location": first_job.location,
                "description": first_job.description,
                "required_skills": first_job.required_skills or ["Python", "C++", "FastAPI"],
                "preferred_skills": first_job.preferred_skills or []
            }
            prof_dict = {
                "name": profile.name,
                "email": profile.email,
                "phone": profile.phone,
                "college": profile.college,
                "degree": profile.degree,
                "graduation_year": profile.graduation_year,
                "cgpa": profile.cgpa,
                "skills": profile.skills,
                "projects": profile.categorized_projects or profile.projects,
                "experience": profile.experience
            }
            tailored_txt = ResumeTailorEngine.tailor_cv(job_dict, prof_dict)
            os.makedirs("uploads", exist_ok=True)
            pdf_path = os.path.join("uploads", f"Tailored_CV_{first_job.company.replace(' ', '_')}_{first_job.id}.pdf")
            ResumeTailorEngine.generate_pdf(tailored_txt, pdf_path)
            
            app = Application(
                profile_id=profile.id,
                job_id=first_job.id,
                status="AWAITING_APPROVAL",
                match_score=94.5,
                match_breakdown={"skills": 95, "education": 100, "experience": 90, "location": 90, "projects": 95},
                match_reason=f"Direct alignment with {first_job.best_matching_project or 'candidate portfolio'}.",
                why_this_job={"required_present": first_job.required_skills, "best_project": first_job.best_matching_project},
                tailored_resume=tailored_txt,
                tailored_resume_pdf_path=pdf_path,
                cover_letter=ResumeTailorEngine.generate_cover_letter(job_dict, prof_dict, first_job.best_matching_project),
                answers=ResumeTailorEngine.generate_application_answers(job_dict, prof_dict, first_job.best_matching_project),
                missing_information=[]
            )
            db.add(app)
            db.commit()
