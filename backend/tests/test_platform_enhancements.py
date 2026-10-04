import os
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.models import UserProfile, Job, Application
from app.tools.extraction_tools import parse_custom_jd, compute_job_hash
from app.tools.matching_tools import generate_evidence_table, calculate_job_match
from app.tools.resume_tools import select_relevant_projects, format_action_result_bullet

client = TestClient(app)

class TestPlatformEnhancements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        db = SessionLocal()
        seed_database(db)
        db.close()

    def test_evidence_citation_table(self):
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
        self.assertGreaterEqual(len(table), 3)
        
        ros2_evidence = next(item for item in table if item["requirement"] == "ROS2")
        self.assertEqual(ros2_evidence["rating"], "STRONG")
        self.assertIn("Autonomous Rover", ros2_evidence["evidence"])

        docker_evidence = next(item for item in table if item["requirement"] == "Docker")
        self.assertEqual(docker_evidence["rating"], "STRONG")
        self.assertIn("Agility Systems", docker_evidence["evidence"])

    def test_action_result_bullet_transformation(self):
        weak_bullet = "worked on a robot simulation and improved speed"
        strong_bullet = format_action_result_bullet(weak_bullet)
        self.assertTrue(strong_bullet.startswith(("Developed", "Engineered", "Implemented")))
        
        unmeasured_bullet = "Designed circuit board for battery monitor"
        enhanced_bullet = format_action_result_bullet(unmeasured_bullet)
        self.assertTrue(any(k in enhanced_bullet.lower() for k in ["throughput", "efficiency", "performance", "optimizing"]))

    def test_single_page_project_segregation(self):
        job = {
            "title": "Machine Learning Intern",
            "required_skills": ["PyTorch", "Computer Vision", "Python"],
            "description": "Vision classification models"
        }
        many_projects = [
            {"name": "Mechanical Gearbox CAD", "tech_stack": ["SolidWorks", "ANSYS"], "description": "FEA Stress"},
            {"name": "PyTorch Vision Classifier", "tech_stack": ["PyTorch", "Python", "Computer Vision"], "description": "ResNet classifier with 92% accuracy"},
            {"name": "C++ Game Engine", "tech_stack": ["C++", "OpenGL"], "description": "2D renderer"},
            {"name": "Deep Learning Object Detection", "tech_stack": ["PyTorch", "YOLO"], "description": "Real-time object detection"}
        ]
        
        selected = select_relevant_projects(many_projects, job, max_projects=2)
        self.assertEqual(len(selected), 2)
        selected_names = [p["name"] for p in selected]
        self.assertIn("PyTorch Vision Classifier", selected_names)
        self.assertIn("Deep Learning Object Detection", selected_names)

    def test_custom_jd_api_flow(self):
        payload = {
            "title": "Autonomous Navigation Intern",
            "company": "NextGen Robotics",
            "jd_text": "We are hiring an autonomous navigation intern with hands-on experience in ROS2, SLAM, C++, and Python for Bangalore office. Stipend is ₹50,000/month."
        }
        res = client.post("/api/jobs/analyze-custom-jd", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["job"]["company"], "NextGen Robotics")
        self.assertIn("ROS2", data["job"]["required_skills"])
        self.assertTrue(data["is_eligible"])
        self.assertGreaterEqual(data["match_score"], 60.0)

if __name__ == "__main__":
    unittest.main()
