import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.models import UserProfile, Job, Application
from app.tools.extraction_tools import parse_custom_jd, compute_job_hash
from app.tools.matching_tools import generate_evidence_table, calculate_job_match
from app.tools.resume_tools import select_relevant_projects, format_action_result_bullet

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_evidence_citation_table():
    job = {
        "required_skills": ["ROS2", "Python", "Docker"],
        "preferred_skills": ["AWS"]
    }
    profile = {
        "skills": ["Python", "ROS2", "C++"],
        "projects": [
            {
                "name": "Autonomous Rover",
                "tech_stack": ["ROS2", "Python", "Linux"],
                "description": "Built 4-wheel robot using ROS2 Navigation2"
            }
        ],
        "experience": [
            {
                "role": "Robotics Intern",
                "company": "Agility Systems",
                "description": "Dockerized robotics simulations"
            }
        ]
    }
    
    table = generate_evidence_table(job, profile)
    assert len(table) >= 3
    
    # ROS2 should have STRONG evidence in Rover project
    ros_entry = next((e for e in table if e["requirement"] == "ROS2"), None)
    assert ros_entry is not None
    assert ros_entry["rating"] == "STRONG"
    assert "Autonomous Rover" in ros_entry["evidence"]
    
    # Docker should have STRONG evidence in Agility Systems experience
    docker_entry = next((e for e in table if e["requirement"] == "Docker"), None)
    assert docker_entry is not None
    assert docker_entry["rating"] == "STRONG"
    assert "Agility Systems" in docker_entry["evidence"]
    
    # AWS has no project/skill evidence -> NONE
    aws_entry = next((e for e in table if e["requirement"] == "AWS"), None)
    assert aws_entry is not None
    assert aws_entry["rating"] == "NONE"

def test_parse_custom_jd_and_sha256_deduplication():
    raw_jd = """
    Job Title: Robotics Software Intern
    Company: HyperScale Robotics
    Location: Bengaluru / Remote
    Salary: ₹45,000 / month
    Requirements:
    - Hands-on experience with ROS2 and C++
    - Familiarity with Navigation2 and SLAM algorithms
    - Minimum graduation year 2026 or 2027
    """
    
    parsed = parse_custom_jd(raw_jd)
    assert "Robotics" in parsed["title"]
    assert "HyperScale" in parsed["company"]
    assert parsed["is_remote"] is True or "Bengaluru" in parsed["location"]
    assert parsed["salary_min"] == 45000.0
    assert "ROS2" in parsed["required_skills"]
    assert parsed["external_id"].startswith("custom-jd-")
    
    # Verify deterministic SHA-256 deduplication
    hash1 = compute_job_hash("HyperScale Robotics", "Robotics Software Intern", "http://example.com/apply")
    hash2 = compute_job_hash("hyperscale robotics", "robotics software intern", "http://example.com/apply?utm_source=ad")
    assert hash1 == hash2

def test_action_result_bullet_optimizer():
    raw_desc = "Made a robot arm controller in C++ and python that was faster"
    tech = ["C++", "Python", "ROS2"]
    bullet = format_action_result_bullet(raw_desc, tech)
    
    # Starts with a strong action verb
    first_word = bullet.split()[0].rstrip(":")
    assert first_word in ["Engineered", "Architected", "Spearheaded", "Implemented", "Developed", "Optimized", "Designed", "Formulated"]
    # Technical scope included
    assert any(t in bullet for t in ["C++", "Python", "ROS2"])
    # Outcome / metric included
    assert "%" in bullet or "latency" in bullet or "efficiency" in bullet or "throughput" in bullet or "accuracy" in bullet

def test_project_domain_pruning():
    projects = [
        {"name": "E-Commerce App", "tech_stack": ["React", "CSS"], "description": "Web shop"},
        {"name": "Quadruped ROS2 Robot", "tech_stack": ["ROS2", "C++", "Navigation2"], "description": "Autonomous navigation"},
        {"name": "SLAM Drone", "tech_stack": ["ROS2", "Python", "OpenCV"], "description": "Vision SLAM mapping"},
        {"name": "Simple Calculator", "tech_stack": ["HTML"], "description": "Calculator"}
    ]
    job = {
        "required_skills": ["ROS2", "C++", "SLAM"],
        "preferred_skills": ["Python"]
    }
    
    pruned = select_relevant_projects(projects, job, max_projects=2)
    assert len(pruned) == 2
    names = [p["name"] for p in pruned]
    assert "Quadruped ROS2 Robot" in names
    assert "SLAM Drone" in names
    assert "E-Commerce App" not in names

def test_custom_jd_api_endpoint():
    payload = {
        "jd_text": "We are seeking a Robotics Systems Intern proficient in ROS2, Python, and Linux at AeroBotix in Bangalore. Stipend: ₹50,000/month.",
        "title": "Robotics Systems Intern",
        "company": "AeroBotix"
    }
    response = client.post("/api/jobs/analyze-custom-jd", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["title"] == "Robotics Systems Intern"
    assert data["job"]["company"] == "AeroBotix"
    assert "match_score" in data
    assert len(data["evidence_table"]) > 0

def test_portal_prefill_endpoint():
    db = SessionLocal()
    app_record = db.query(Application).first()
    db.close()
    
    if app_record:
        response = client.post(f"/api/applications/{app_record.id}/prepare-portal")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PORTAL_PREFILLED"

def test_resume_parser_and_profile_update():
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    import io
    
    # Generate test PDF in memory
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Rohan Varma", styles["Normal"]),
        Paragraph("rohan.varma@example.com | +91 9876543210", styles["Normal"]),
        Paragraph("Education:", styles["Normal"]),
        Paragraph("Indian Institute of Technology Delhi", styles["Normal"]),
        Paragraph("B.Tech in Computer Science & Engineering, Batch of 2026", styles["Normal"]),
        Paragraph("CGPA: 9.15/10", styles["Normal"]),
        Paragraph("Technical Skills: Python, C++, ROS2, PyTorch, Linux, Docker, FastAPI", styles["Normal"]),
        Paragraph("Projects:", styles["Normal"]),
        Paragraph("Autonomous Drone Navigation | ROS2, Python, OpenCV", styles["Normal"]),
        Paragraph("Engineered autonomous path planning algorithm for quadcopter drone.", styles["Normal"]),
        Paragraph("Experience:", styles["Normal"]),
        Paragraph("Robotics Research Intern at DRDO Labs", styles["Normal"]),
        Paragraph("Developed real-time SLAM simulation environments.", styles["Normal"]),
    ]
    doc.build(story)
    pdf_bytes = buf.getvalue()
    
    from app.tools.resume_tools import parse_resume_pdf
    parsed = parse_resume_pdf(pdf_bytes)
    
    assert "Rohan Varma" in parsed["name"]
    assert parsed["email"] == "rohan.varma@example.com"
    assert "9876543210" in parsed["phone"]
    assert "Indian Institute of Technology" in parsed["college"] or "IIT" in parsed["college"]
    assert "B.Tech" in parsed["degree"] or "Computer Science" in parsed["degree"]
    assert parsed["graduation_year"] == 2026
    assert parsed["cgpa"] == 9.15
    assert "ROS2" in parsed["skills"]
    assert "PyTorch" in parsed["skills"]
    assert len(parsed["projects"]) > 0
    assert len(parsed["experience"]) > 0
    
    # Test upload endpoint updates UserProfile
    response = client.post(
        "/api/profiles/upload-resume",
        files={"file": ("rohan_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "SUCCESS"
    assert res_data["profile"]["name"] == "Rohan Varma"
    assert res_data["profile"]["email"] == "rohan.varma@example.com"
    assert res_data["profile"]["cgpa"] == 9.15
    assert res_data["profile"]["graduation_year"] == 2026
    assert "ROS2" in res_data["profile"]["skills"]

