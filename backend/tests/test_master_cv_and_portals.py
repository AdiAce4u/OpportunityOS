import unittest
import os
import uuid
from app.tools.cv_parser_engine import MasterCVParser
from app.tools.portal_search_engine import search_live_portals, ROLE_CATEGORIES, CVProjectMatcher, CompensationParser
from app.tools.resume_tailor_engine import ResumeTailorEngine
from app.db.session import init_db, SessionLocal
from app.models import Job, UserProfile, Application

class TestMasterCVAndPortals(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_master_cv_multi_domain_parsing(self):
        sample_cv_text = """
VAIBHAV ANAND | 24ME10168
B.Tech in MECHANICAL ENGINEERING
IIT Kharagpur | CGPA: 8.39 / 10 | 2028

SKILLS
Python, C++, PyTorch, ROS2, FastAPI, Docker, Node.js, SolidWorks

PROJECTS
Graph-Based Rail Navigation and Route Optimization Platform | Self Project
• Built a full-stack rail navigation system using C++ Dijkstra and Node.js REST API with sub-second routing across 25 stations.
• Deployed with Docker container on cloud.

Fine-Tuned LLM Conversational Agent | Self Project
• Engineered an empathetic conversational AI by fine-tuning a 7B-parameter Qwen2.5 LLM using PyTorch and QLoRA.
• Optimized GPU memory footprint by 60% via 4-bit quantization and Triton kernels.

Path Tracking and Control of Autonomous Vehicles | Self Project
• Developed a modular simulator implementing Pure Pursuit and LQR path-tracking controllers with Kalman Filter on ROS2.
• LQR achieved 0.67m RMSE outperforming baseline by 24%.

LSTM-Powered Stock Forecasting API | Self Project
• Built a 2-layer stacked LSTM financial forecasting model for 8 tickers with FastAPI and Plotly.
"""
        parsed = MasterCVParser.parse_full_master_cv(sample_cv_text)
        self.assertEqual(parsed["name"], "VAIBHAV ANAND")
        self.assertEqual(parsed["college"], "IIT Kharagpur")
        self.assertGreaterEqual(len(parsed["projects"]), 3)

        domains = [p["domain"] for p in parsed["projects"]]
        self.assertTrue(any(d in domains for d in ["sde", "data", "core", "finance", "product", "consult"]))

    def test_multi_portal_search_and_project_matching(self):
        candidate_projects = [
            {
                "name": "Graph-Based Rail Navigation and Route Optimization",
                "domain": "sde",
                "full_text": "Graph-Based Rail Navigation with C++ and FastAPI backend microservices",
                "tech_stack": ["C++", "FastAPI", "Docker"]
            },
            {
                "name": "Fine-Tuned LLM Conversational Agent",
                "domain": "data",
                "full_text": "Fine-Tuned LLM with PyTorch QLoRA and Transformers",
                "tech_stack": ["PyTorch", "QLoRA", "LLM"]
            }
        ]

        results = search_live_portals(
            search_term="Backend Engineer",
            location="Bangalore",
            category="sde",
            results_wanted=3,
            candidate_projects=candidate_projects
        )

        self.assertGreaterEqual(len(results), 1)
        top_match = results[0]
        self.assertIn("match_score", top_match)
        self.assertIn("best_matching_project", top_match)
        self.assertIn("display_salary", top_match)
        self.assertGreater(top_match["match_score"], 0)

    def test_jd_tailored_1page_ats_cv_generation(self):
        job = {
            "title": "Machine Learning Engineer",
            "company": "AI Tech Corp",
            "location": "Remote",
            "required_skills": ["Python", "PyTorch", "LLM", "Transformers"],
            "description": "Looking for ML engineer with experience in LLM fine-tuning and PyTorch models."
        }

        profile = {
            "name": "Vaibhav Anand",
            "email": "vaibhav@example.com",
            "phone": "+91 9876543210",
            "college": "IIT Kharagpur",
            "degree": "B.Tech",
            "graduation_year": 2028,
            "cgpa": 8.39,
            "skills": ["Python", "PyTorch", "C++", "ROS2", "Docker", "Transformers"],
            "projects": [
                {
                    "name": "Fine-Tuned LLM Conversational Agent",
                    "domain": "data",
                    "description": "Fine-tuned 7B Qwen2.5 with PyTorch and QLoRA.",
                    "tech_stack": ["PyTorch", "Transformers", "QLoRA"],
                    "bullets": ["Engineered LLM fine-tuning pipeline reducing GPU memory by 60%."]
                },
                {
                    "name": "2D Von Mises Stress Field Predictor",
                    "domain": "core",
                    "description": "FEA simulation in SOLIDWORKS.",
                    "tech_stack": ["SolidWorks", "ANSYS"],
                    "bullets": ["Generated stress contour maps."]
                }
            ],
            "experience": []
        }

        selected = ResumeTailorEngine.select_relevant_projects(profile["projects"], job, max_projects=1)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["name"], "Fine-Tuned LLM Conversational Agent")

        tailored_cv = ResumeTailorEngine.tailor_cv(job, profile)
        self.assertIn("VAIBHAV ANAND", tailored_cv)
        self.assertIn("Fine-Tuned LLM Conversational Agent", tailored_cv)
        self.assertIn("PyTorch", tailored_cv)

        os.makedirs("uploads", exist_ok=True)
        pdf_path = os.path.join("uploads", "test_tailored_ats_cv.pdf")
        ResumeTailorEngine.generate_pdf(tailored_cv, pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 500)

    def test_permission_and_approval_workflow(self):
        rand_id = f"test-job-{uuid.uuid4().hex[:8]}"
        job = Job(
            external_id=rand_id,
            title="Software Engineer",
            company="Acme Corp",
            location="Remote"
        )
        self.db.add(job)
        self.db.commit()

        app = Application(
            job_id=job.id,
            status="AWAITING_APPROVAL",
            match_score=95.0,
            tailored_resume="Tailored CV content"
        )
        self.db.add(app)
        self.db.commit()

        self.assertEqual(app.status, "AWAITING_APPROVAL")

if __name__ == "__main__":
    unittest.main()
