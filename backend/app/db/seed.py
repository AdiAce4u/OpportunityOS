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

    # Seed rich Wellfound startup openings across all 5 tracks
    wellfound_startups = [
        ("software", "Cursor (Anysphere)", "Full Stack / AI Infrastructure Engineer", "₹32.0 - 45.0 LPA", "Remote", "https://wellfound.com/jobs?role=software"),
        ("software", "Together AI", "Backend & Cloud Systems Engineer", "₹30.0 - 42.0 LPA", "Remote", "https://wellfound.com/jobs?role=software"),
        ("software", "Supabase", "Distributed Systems / Postgres Engineer", "₹28.0 - 38.0 LPA", "Remote", "https://wellfound.com/jobs?role=software"),
        ("software", "LangChain", "Software Engineer - Developer Frameworks & APIs", "₹26.0 - 35.0 LPA", "Remote", "https://wellfound.com/jobs?role=software"),
        ("software", "Postman", "Founding Platform Engineer (APIs & Systems)", "₹22.0 - 30.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=software"),
        ("software", "Vercel", "Frontend & Full Stack Systems Engineer", "₹28.0 - 36.0 LPA", "Remote", "https://wellfound.com/jobs?role=software"),
        ("data", "Perplexity AI", "AI / Retrieval & Search Systems Engineer", "₹35.0 - 50.0 LPA", "Remote", "https://wellfound.com/jobs?role=data"),
        ("data", "Mistral AI", "Machine Learning & Model Optimization Engineer", "₹38.0 - 55.0 LPA", "Remote", "https://wellfound.com/jobs?role=data"),
        ("data", "Glean", "Machine Learning Engineer - Enterprise Knowledge Graph", "₹30.0 - 45.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=data"),
        ("data", "Pinecone", "Vector Database & Indexing Systems Engineer", "₹28.0 - 40.0 LPA", "Remote", "https://wellfound.com/jobs?role=data"),
        ("data", "Scale AI", "Data & Computer Vision Research Engineer", "₹26.0 - 38.0 LPA", "Remote", "https://wellfound.com/jobs?role=data"),
        ("data", "Weights & Biases", "MLOps & Deep Learning Infrastructure Engineer", "₹25.0 - 35.0 LPA", "Remote", "https://wellfound.com/jobs?role=data"),
        ("data", "Arize AI", "Machine Learning Observability & Evaluation Intern", "₹65,000/month", "Remote", "https://wellfound.com/jobs?role=data"),
        ("core", "Figure AI", "Humanoid Robotics Software Engineer (Controls & ROS2)", "₹35.0 - 50.0 LPA", "Remote", "https://wellfound.com/jobs?role=robotics"),
        ("core", "Skydio", "Autonomous Drone Navigation & SLAM Engineer", "₹28.0 - 42.0 LPA", "Remote", "https://wellfound.com/jobs?role=robotics"),
        ("core", "Covariant", "Robotics Perception & Manipulation Engineer", "₹30.0 - 44.0 LPA", "Remote", "https://wellfound.com/jobs?role=robotics"),
        ("core", "Monarch Tractor", "Autonomous Vehicle & Embedded Systems Engineer", "₹24.0 - 34.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=robotics"),
        ("core", "Dexterity", "Robotics Motion Planning & Firmware Engineer", "₹26.0 - 36.0 LPA", "Remote", "https://wellfound.com/jobs?role=robotics"),
        ("finance", "Wintermute", "Quantitative Trader & Algorithmic Researcher", "₹40.0 - 65.0 LPA", "Remote", "https://wellfound.com/jobs?role=finance"),
        ("finance", "FalconX", "Crypto Quant Researcher & Liquidity Engineer", "₹35.0 - 55.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=finance"),
        ("finance", "Ramp", "Fintech Backend & Risk Intelligence Engineer", "₹32.0 - 46.0 LPA", "Remote", "https://wellfound.com/jobs?role=finance"),
        ("finance", "Plaid", "Financial Data Infrastructure Engineer", "₹30.0 - 44.0 LPA", "Remote", "https://wellfound.com/jobs?role=finance"),
        ("finance", "Brex", "Fintech Risk Analytics & Quantitative Engineer", "₹28.0 - 40.0 LPA", "Remote", "https://wellfound.com/jobs?role=finance"),
        ("consult", "Antler India", "Venture Partner & Startup Strategy Analyst", "₹18.0 - 25.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=consulting"),
        ("consult", "Entrepreneur First", "Founders Associate - Strategy & Operations", "₹16.0 - 24.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=consulting"),
        ("consult", "Carta", "Corporate Strategy & Private Market Valuation Analyst", "₹20.0 - 28.0 LPA", "Bangalore", "https://wellfound.com/jobs?role=consulting"),
        ("consult", "Techstars", "Startup Acceleration & Strategy Associate", "₹15.0 - 22.0 LPA", "Remote", "https://wellfound.com/jobs?role=consulting"),
    ]
    for cat, comp, title, sal, loc, url in wellfound_startups:
        ext_id = f"wf-{uuid.uuid5(uuid.NAMESPACE_DNS, title + comp).hex[:10]}"
        existing = db.query(Job).filter((Job.external_id == ext_id) | ((Job.title == title) & (Job.company == comp))).first()
        if not existing:
            match_info = matcher.match_job_description(title, f"{title} at {comp}. Cutting-edge startup technology.")
            job = Job(
                external_id=ext_id,
                title=title,
                company=comp,
                location=loc,
                is_remote="remote" in loc.lower(),
                category=cat,
                search_term=title,
                site="wellfound",
                match_score=match_info.get("match_score", 86.0),
                best_matching_project=match_info.get("best_project", "Featured Project"),
                best_project_domain=cat,
                matched_keywords=match_info.get("matched_keywords", ["Python", "Systems"]),
                salary_text=sal,
                display_salary=sal,
                description=f"Frontier startup opening for {title} at {comp} on Wellfound. Equity, high ownership, and rapid engineering iteration.",
                required_skills=match_info.get("matched_keywords", ["System Design", "Problem Solving"]),
                url=url,
                source="portal_wellfound"
            )
            db.add(job)
    db.commit()

def seed_database(db):
    """Initializes OpportunityOS database with benchmark and portal opportunities (Profile and Applications remain blank until user uploads Master CV)."""
    # Seed benchmark opportunities
    for job_data in SAMPLE_JOBS:
        existing = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
        if not existing:
            job = Job(**job_data)
            db.add(job)
    db.commit()

    # Sync all jobs from job-search-agent/jobs_database.db
    sync_agent_db_jobs(db, [])

