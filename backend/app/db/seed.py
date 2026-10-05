import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from app.models import UserProfile, Job, Application, FollowUpEvent
from app.tools.cv_parser_engine import MasterCVParser
from app.tools.portal_search_engine import ROLE_CATEGORIES, CVProjectMatcher, CompensationParser

APP_HOST = os.getenv("APP_HOST", "https://opportunityos1.onrender.com").rstrip("/")

SAMPLE_JOBS = [
    {
        "external_id": "xyz-robotics-001",
        "title": "Robotics Software Intern",
        "company": "XYZ Robotics",
        "location": "Bangalore",
        "is_remote": False,
        "salary_text": "₹50,000/month",
        "salary_min": 50000.0,
        "salary_max": 50000.0,
        "category": "robotics",
        "search_term": "Robotics Intern",
        "site": "company_careers",
        "match_score": 94.2,
        "description": "Develop autonomous mobile robot navigation, ROS2 sensor drivers, state estimation, and path planning in Python and C++.",
        "required_skills": ["Python", "C++", "ROS2", "Robotics", "Linux"],
        "preferred_skills": ["Navigation2", "Gazebo", "SLAM", "Docker"],
        "education_requirements": ["B.Tech", "M.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-1 years / Student",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028, "degree": ["B.Tech", "M.Tech", "Dual Degree"]},
        "deadline": "2026-11-15",
        "url": f"{APP_HOST}/portal/apply/xyz-robotics-001",
        "application_method": "form",
        "required_documents": ["resume", "cover_letter"],
        "source": "company_careers",
        "company_research": {
            "summary": "XYZ Robotics builds next-gen autonomous warehouse robots and industrial AMRs with cutting-edge LiDAR SLAM.",
            "domain": "Robotics & Autonomous Logistics",
            "size": "50-150 employees",
            "technology": ["ROS2", "C++20", "Python", "NVIDIA Isaac Sim", "TensorRT"],
            "recent_news": ["Secured $12M Series A funding for warehouse fleet expansion across Southeast Asia."],
            "reputation_notes": ["Known for high engineering bar and rapid robotics prototyping culture."]
        }
    },
    {
        "external_id": "abc-ai-002",
        "title": "Machine Learning Intern",
        "company": "ABC AI",
        "location": "Remote",
        "is_remote": True,
        "salary_text": "₹45,000/month",
        "salary_min": 45000.0,
        "salary_max": 45000.0,
        "category": "data",
        "search_term": "ML Intern",
        "site": "job_board",
        "match_score": 91.0,
        "description": "Train and evaluate deep learning vision models, build feature extraction pipelines with PyTorch, and deploy real-time inference services.",
        "required_skills": ["Python", "Machine Learning", "PyTorch", "Data Science"],
        "preferred_skills": ["Computer Vision", "FastAPI", "ONNX", "Docker"],
        "education_requirements": ["B.Tech", "M.Tech", "MS"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-1 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-10-31",
        "url": f"{APP_HOST}/portal/apply/abc-ai-002",
        "application_method": "form",
        "required_documents": ["resume"],
        "source": "job_board",
        "company_research": {
            "summary": "ABC AI is an applied machine intelligence research lab developing vision and multimodal agents.",
            "domain": "Applied Artificial Intelligence",
            "size": "100-250 employees",
            "technology": ["PyTorch", "Python", "Transformers", "Kubernetes"],
            "recent_news": ["Published state-of-the-art vision benchmark at CVPR."],
            "reputation_notes": ["Strong remote-first research culture with mentorship from FAANG alumni."]
        }
    },
    {
        "external_id": "def-auto-003",
        "title": "Autonomous Systems Intern",
        "company": "DEF Autonomy",
        "location": "Hyderabad",
        "is_remote": False,
        "salary_text": "₹55,000/month",
        "salary_min": 55000.0,
        "salary_max": 60000.0,
        "category": "robotics",
        "search_term": "Autonomous Systems",
        "site": "company_careers",
        "match_score": 91.0,
        "description": "Perception, sensor fusion (camera, LiDAR, radar), Kalman filters, and controls for autonomous navigation systems.",
        "required_skills": ["ROS2", "C++", "Python", "Controls", "Robotics"],
        "preferred_skills": ["EKF", "C++17", "Point Cloud Library", "CAN Bus"],
        "education_requirements": ["B.Tech", "M.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-2 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-11-20",
        "url": f"{APP_HOST}/portal/apply/def-auto-003",
        "application_method": "form",
        "required_documents": ["resume", "cover_letter"],
        "source": "company_careers",
        "company_research": {
            "summary": "DEF Autonomy designs self-driving mining haulers and autonomous off-road heavy machinery.",
            "domain": "Autonomous Vehicles & Industrial Automation",
            "size": "200-500 employees",
            "technology": ["ROS2", "Modern C++", "Simulink", "Linux Real-Time"],
            "recent_news": ["Deployed first fully driverless fleet at a major open-pit site."],
            "reputation_notes": ["High safety rigor, exceptional hardware-in-the-loop facilities."]
        }
    },
    {
        "external_id": "neural-drive-004",
        "title": "Robot Perception Intern",
        "company": "NeuralDrive Labs",
        "location": "Bangalore",
        "is_remote": False,
        "salary_text": "₹60,000/month",
        "salary_min": 60000.0,
        "salary_max": 65000.0,
        "category": "data",
        "search_term": "Robot Perception",
        "site": "github_careers",
        "match_score": 91.0,
        "description": "Build real-time 3D object detection, semantic segmentation, and tracking pipelines for humanoid robotic arms and quadrupeds.",
        "required_skills": ["Python", "C++", "Computer Vision", "Machine Learning", "ROS2"],
        "preferred_skills": ["CUDA", "TensorRT", "RealSense", "Isaac Gym"],
        "education_requirements": ["B.Tech", "M.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "Student / 0-1 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-12-01",
        "url": f"{APP_HOST}/portal/apply/neural-drive-004",
        "application_method": "form",
        "required_documents": ["resume", "cover_letter"],
        "source": "github_careers",
        "company_research": {
            "summary": "NeuralDrive Labs builds generalist robotic dexterity algorithms and bipedal humanoid platforms.",
            "domain": "Embodied AI & Humanoid Robotics",
            "size": "30-80 employees",
            "technology": ["PyTorch", "ROS2 Humble", "NVIDIA Jetson", "C++20"],
            "recent_news": ["Demonstrated whole-body teleoperation via VR headset."],
            "reputation_notes": ["Fast-paced venture-backed startup with generous equity and compute."]
        }
    },
    {
        "external_id": "apex-robotics-005",
        "title": "Embedded Robotics Firmware Intern",
        "company": "Apex Robotics",
        "location": "Pune",
        "is_remote": False,
        "salary_text": "₹42,000/month",
        "salary_min": 42000.0,
        "salary_max": 45000.0,
        "category": "robotics",
        "search_term": "Embedded Firmware",
        "site": "company_careers",
        "match_score": 85.0,
        "description": "Microcontroller programming, motor control (BLDC/FOC), CAN/UART interfaces, and FreeRTOS integration with ROS2 micro-XRCE.",
        "required_skills": ["C++", "Python", "Embedded Systems", "Robotics"],
        "preferred_skills": ["STM32", "FreeRTOS", "micro-ROS", "Altium"],
        "education_requirements": ["B.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-1 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-11-10",
        "url": f"{APP_HOST}/portal/apply/apex-robotics-005",
        "application_method": "form",
        "required_documents": ["resume"],
        "source": "company_careers",
        "company_research": {
            "summary": "Apex Robotics manufactures drone avionics and precision agricultural spraying rovers.",
            "domain": "AgriTech & Drones",
            "size": "80-150 employees",
            "technology": ["STM32", "C++", "Python", "ROS2", "KiCad"],
            "recent_news": ["Granted DGCA type certification for high-payload commercial drone."],
            "reputation_notes": ["Hands-on hardware lab with rigorous testing fields."]
        }
    },
    {
        "external_id": "ineligible-senior-006",
        "title": "Principal Robotics Architect",
        "company": "Titan Robotics",
        "location": "Bangalore",
        "is_remote": False,
        "salary_text": "₹2,50,000/month",
        "salary_min": 250000.0,
        "salary_max": 300000.0,
        "category": "robotics",
        "search_term": "Robotics Architect",
        "site": "job_board",
        "match_score": 45.0,
        "description": "10+ years leading production robotics architecture, ROS safety certifications, and commercial fleet deployments.",
        "required_skills": ["ROS2", "C++", "System Architecture", "Safety Critical Systems"],
        "preferred_skills": ["ISO 26262", "Autosar"],
        "education_requirements": ["M.Tech", "Ph.D"],
        "graduation_requirements": {"min_year": 2010, "max_year": 2018},
        "experience_requirements": "8+ years",
        "eligibility": {"graduation_year_min": 2010, "graduation_year_max": 2018, "required_min_years_experience": 8},
        "deadline": "2026-10-15",
        "url": f"{APP_HOST}/portal/apply/ineligible-senior-006",
        "application_method": "form",
        "required_documents": ["resume"],
        "source": "job_board",
        "company_research": {"summary": "Titan Robotics is a defense industrial contractor.", "domain": "Defense Robotics"}
    }
]

def sync_agent_db_jobs(db, projects):
    """Imports all jobs from job-search-agent/jobs_database.db or jobs_latest.json and seeds Consult track."""
    matcher = CVProjectMatcher(projects)
    agent_db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "job-search-agent", "jobs_database.db")
    json_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "job-search-agent", "results", "jobs_latest.json")
    
    imported_count = 0
    if os.path.exists(agent_db_path):
        try:
            conn = sqlite3.connect(agent_db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM jobs")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
        except Exception:
            rows = []
    elif os.path.exists(json_path):
        try:
            import json
            with open(json_path, "r", encoding="utf-8") as f:
                rows = json.load(f)
        except Exception:
            rows = []
    else:
        rows = []

    for d in rows[:250]:
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
                match_score=float(d.get("match_score") or match_info.get("match_score", 82.0)),
                best_matching_project=d.get("best_matching_project") or match_info.get("best_project", "Featured Project"),
                best_project_domain=match_info.get("best_project_domain", cat),
                matched_keywords=d.get("matched_keywords") or match_info.get("matched_keywords", []),
                salary_text=d.get("display_salary") or comp_info.get("display_salary", "Competitive"),
                display_salary=d.get("display_salary") or comp_info.get("display_salary", "Competitive"),
                normalized_salary=float(d.get("normalized_salary") or comp_info.get("normalized_yearly_salary", 0.0)),
                description=d.get("description") or f"{title} at {company}",
                required_skills=d.get("matched_keywords") or match_info.get("matched_keywords") or ["System Design", "Problem Solving"],
                preferred_skills=["Communication", "Docker"],
                education_requirements=["B.Tech", "Degree"],
                url=d.get("job_url") or "",
                source=f"portal_{d.get('site', 'database')}"
            )
            db.add(job)
            imported_count += 1
    db.commit()

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
            skills=list(dict.fromkeys((parsed_cv.get("skills") or []) + [
                "Python", "C++", "PyTorch", "ROS2", "Machine Learning", "FastAPI",
                "Deep Learning", "Docker", "Node.js", "SolidWorks", "Computer Vision"
            ])) if parsed_cv else [
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
                "Robotics Software Engineer",
                "Machine Learning Engineer",
                "Software Development Engineer",
                "Data Scientist",
                "Quantitative Analyst",
                "Management Consultant"
            ],
            preferred_locations=["India", "Bangalore", "Hyderabad", "Remote", "Gurugram", "Mumbai"],
            remote_preference=True,
            minimum_salary=40000.0,
            work_authorization="Eligible to work in India",
            prefer_companies=["XYZ Robotics", "NeuralDrive Labs", "ABC AI", "NVIDIA", "Uber"],
            avoid_companies=[],
            resume_filename="Master_CV.md",
            master_cv_markdown=master_text or "Master CV loaded."
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    elif parsed_cv:
        profile.projects = parsed_cv.get("projects", [])
        profile.categorized_projects = parsed_cv.get("projects", [])
        profile.skills = list(dict.fromkeys((profile.skills or []) + (parsed_cv.get("skills") or []) + [
            "ROS2", "C++", "Python", "PyTorch", "Machine Learning"
        ]))
        profile.master_cv_markdown = master_text
        db.commit()

    # Seed benchmark opportunities
    for job_data in SAMPLE_JOBS:
        existing = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
        if not existing:
            job = Job(**job_data)
            db.add(job)
    db.commit()

    # Sync all jobs from job-search-agent/jobs_database.db
    sync_agent_db_jobs(db, profile.categorized_projects or profile.projects or [])

    # Seed an application ready for review if none exist
    if db.query(Application).count() == 0:
        first_job = db.query(Job).filter(Job.external_id == "xyz-robotics-001").first() or db.query(Job).first()
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

            # Seed an interview follow-up event
            if db.query(FollowUpEvent).count() == 0:
                follow_up = FollowUpEvent(
                    application_id=app.id,
                    event_type="INTERVIEW_INVITATION",
                    scheduled_for=datetime.utcnow() + timedelta(days=3),
                    status="PENDING",
                    subject=f"Interview Invitation: {first_job.title} at {first_job.company}",
                    content=f"{first_job.company} would like to invite you for a 45-minute Technical Discussion on ROS2 architecture and path planning.",
                    interview_details={
                        "date": (datetime.utcnow() + timedelta(days=3)).strftime("%B %d, %Y at 3:00 PM IST"),
                        "round": "Technical Round 1 (Autonomy & System Architecture)",
                        "interviewers": "Lead Autonomy Engineer",
                        "meeting_link": "https://meet.google.com/xyz-robt-demo"
                    },
                    prep_notes="Review Cartographer SLAM parameter tuning, Nav2 BT navigator concepts, and C++ memory management (smart pointers)."
                )
                db.add(follow_up)
                db.commit()
