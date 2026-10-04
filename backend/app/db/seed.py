from app.models import UserProfile, Job, Application, FollowUpEvent
from datetime import datetime, timedelta

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
        "description": "Develop autonomous mobile robot navigation, ROS2 sensor drivers, state estimation, and path planning in Python and C++.",
        "required_skills": ["Python", "C++", "ROS2", "Robotics", "Linux"],
        "preferred_skills": ["Navigation2", "Gazebo", "SLAM", "Docker"],
        "education_requirements": ["B.Tech", "M.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-1 years / Student",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028, "degree": ["B.Tech", "M.Tech", "Dual Degree"]},
        "deadline": "2026-11-15",
        "url": "http://localhost:8000/portal/apply/xyz-robotics-001",
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
        "description": "Train and evaluate deep learning vision models, build feature extraction pipelines with PyTorch, and deploy real-time inference services.",
        "required_skills": ["Python", "Machine Learning", "PyTorch", "Data Science"],
        "preferred_skills": ["Computer Vision", "FastAPI", "ONNX", "Docker"],
        "education_requirements": ["B.Tech", "M.Tech", "MS"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-1 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-10-31",
        "url": "http://localhost:8000/portal/apply/abc-ai-002",
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
        "description": "Perception, sensor fusion (camera, LiDAR, radar), Kalman filters, and controls for autonomous navigation systems.",
        "required_skills": ["ROS2", "C++", "Python", "Controls", "Robotics"],
        "preferred_skills": ["EKF", "C++17", "Point Cloud Library", "CAN Bus"],
        "education_requirements": ["B.Tech", "M.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-2 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-11-20",
        "url": "http://localhost:8000/portal/apply/def-auto-003",
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
        "description": "Build real-time 3D object detection, semantic segmentation, and tracking pipelines for humanoid robotic arms and quadrupeds.",
        "required_skills": ["Python", "C++", "Computer Vision", "Machine Learning", "ROS2"],
        "preferred_skills": ["CUDA", "TensorRT", "RealSense", "Isaac Gym"],
        "education_requirements": ["B.Tech", "M.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "Student / 0-1 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-12-01",
        "url": "http://localhost:8000/portal/apply/neural-drive-004",
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
        "description": "Microcontroller programming, motor control (BLDC/FOC), CAN/UART interfaces, and FreeRTOS integration with ROS2 micro-XRCE.",
        "required_skills": ["C++", "Python", "Embedded Systems", "Robotics"],
        "preferred_skills": ["STM32", "FreeRTOS", "micro-ROS", "Altium"],
        "education_requirements": ["B.Tech"],
        "graduation_requirements": {"min_year": 2026, "max_year": 2028},
        "experience_requirements": "0-1 years",
        "eligibility": {"graduation_year_min": 2026, "graduation_year_max": 2028},
        "deadline": "2026-11-10",
        "url": "http://localhost:8000/portal/apply/apex-robotics-005",
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
        "description": "10+ years leading production robotics architecture, ROS safety certifications, and commercial fleet deployments.",
        "required_skills": ["ROS2", "C++", "System Architecture", "Safety Critical Systems"],
        "preferred_skills": ["ISO 26262", "Autosar"],
        "education_requirements": ["M.Tech", "Ph.D"],
        "graduation_requirements": {"min_year": 2010, "max_year": 2018},
        "experience_requirements": "8+ years",
        "eligibility": {"graduation_year_min": 2010, "graduation_year_max": 2018, "required_min_years_experience": 8},
        "deadline": "2026-10-15",
        "url": "http://localhost:8000/portal/apply/ineligible-senior-006",
        "application_method": "form",
        "required_documents": ["resume"],
        "source": "job_board",
        "company_research": {"summary": "Titan Robotics is a defense industrial contractor.", "domain": "Defense Robotics"}
    }
]

def seed_database(db):
    # Ensure default user profile exists
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(
            name="Aarav Sharma",
            email="aarav.sharma@example.com",
            phone="+91 9876543210",
            graduation_year=2027,
            degree="B.Tech in Computer Science & Robotics",
            college="IIT Kharagpur",
            cgpa=8.92,
            skills=["Python", "C++", "ROS2", "Machine Learning", "Robotics", "Controls", "Linux", "PyTorch"],
            projects=[
                {
                    "name": "Quadruped Robot Dynamic Locomotion",
                    "description": "Designed a 12-DOF quadruped robot using ROS2 Humble, Gazebo simulation, and model-predictive controls for dynamic gait stabilization.",
                    "tech_stack": ["ROS2", "C++", "Python", "Gazebo", "Controls"],
                    "link": "https://github.com/aarav-sharma/quadruped-ros2"
                },
                {
                    "name": "Autonomous Navigation with LiDAR SLAM",
                    "description": "Implemented 2D/3D Cartographer SLAM and Nav2 stack with obstacle costmaps on an Ackerman-steered autonomous testbed.",
                    "tech_stack": ["ROS2", "C++", "SLAM", "Navigation2"],
                    "link": "https://github.com/aarav-sharma/nav2-cartographer"
                },
                {
                    "name": "Deep Learning Vision for Robotic Grasping",
                    "description": "Trained YOLOv8 and GG-CNN grasping models with PyTorch to detect 6-DOF grasp poses for industrial robot arm pick-and-place.",
                    "tech_stack": ["Python", "PyTorch", "Computer Vision", "Machine Learning"],
                    "link": "https://github.com/aarav-sharma/robot-grasp-vision"
                }
            ],
            experience=[
                {
                    "role": "Robotics Research Assistant",
                    "company": "Centre for Robotics, IIT Kharagpur",
                    "duration": "May 2025 - Present",
                    "description": "Developed low-latency ROS2 communication nodes and sensor drivers for IMU and LiDAR."
                }
            ],
            preferred_roles=["Robotics Intern", "Robotics Software Intern", "ML Intern", "Autonomous Systems Intern"],
            preferred_locations=["India", "Bangalore", "Hyderabad", "Remote"],
            remote_preference=True,
            minimum_salary=40000.0,
            work_authorization="Citizen of India, fully authorized to work in India",
            prefer_companies=["XYZ Robotics", "NeuralDrive Labs", "ABC AI"],
            avoid_companies=["Unregulated Crypto Corp"],
            resume_filename="Aarav_Sharma_Resume.pdf",
            resume_text="""AARAV SHARMA
Email: aarav.sharma@example.com | Phone: +91 9876543210 | Bangalore / Kharagpur, India
LinkedIn: linkedin.com/in/aarav-sharma | GitHub: github.com/aarav-sharma

EDUCATION
Indian Institute of Technology (IIT) Kharagpur
B.Tech in Computer Science & Robotics | CGPA: 8.92/10.0 | Expected Graduation: 2027

TECHNICAL SKILLS
Languages: Python, C++ (C++17/20), Bash, SQL
Robotics & Control: ROS2 (Humble/Iron), Nav2, Gazebo, SLAM, PID/MPC Control, Micro-ROS
AI / Machine Learning: PyTorch, OpenCV, Scikit-Learn, NumPy, TensorRT, Computer Vision
Tools & Systems: Linux/Ubuntu, Git, Docker, CMake, RealSense, LiDAR

PROJECTS
- Quadruped Robot Dynamic Locomotion: Implemented 12-DOF quadruped gait planning with ROS2 and Gazebo physics.
- Autonomous Navigation with Cartographer SLAM: Deployed Nav2 stack with LiDAR-inertial odometry.
- Deep Learning Vision for Robotic Grasping: 6-DOF robotic grasp pose estimation using PyTorch and OpenCV.

WORK EXPERIENCE
Robotics Research Assistant | Centre for Robotics, IIT Kharagpur | May 2025 - Present
- Engineered high-throughput ROS2 messaging pipelines reducing latency by 35%.
"""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Seed sample jobs
    for job_data in SAMPLE_JOBS:
        existing = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
        if not existing:
            job = Job(**job_data)
            db.add(job)
    db.commit()

    # Seed sample applications if none exist
    if db.query(Application).count() == 0:
        xyz_job = db.query(Job).filter(Job.external_id == "xyz-robotics-001").first()
        if xyz_job:
            app = Application(
                profile_id=profile.id,
                job_id=xyz_job.id,
                status="AWAITING_APPROVAL",
                match_score=94.2,
                match_breakdown={
                    "skills": 95,
                    "education": 100,
                    "experience": 85,
                    "location": 100,
                    "projects": 94
                },
                match_reason="Exceptional alignment with ROS2, Python, C++, and robotics navigation coursework and projects at IIT Kharagpur.",
                why_this_job={
                    "required_present": ["Python", "C++", "ROS2", "Robotics", "Linux"],
                    "missing": ["Navigation2", "Docker"]
                },
                company_research=xyz_job.company_research,
                tailored_resume="""AARAV SHARMA — TAILORED FOR XYZ ROBOTICS
Role: Robotics Software Intern | Bangalore

SUMMARY
CS & Robotics student at IIT Kharagpur with deep hands-on expertise in ROS2 Humble, C++, Python, and autonomous navigation pipelines. Proven experience developing quadruped dynamic locomotion and LiDAR Cartographer SLAM.

CORE MATCHED SKILLS
✓ ROS2, Python, Modern C++, Linux, Navigation2, Gazebo Simulation, Mobile Robotics

SELECTED RELEVANT PROJECTS
1. Quadruped Robot Dynamic Locomotion (ROS2, C++, Gazebo)
   - Built 12-DOF simulation model with state-space controllers and low-latency ROS2 nodes.
2. Autonomous Navigation with Cartographer SLAM (ROS2, LiDAR)
   - Integrated Nav2 costmap layers and real-time obstacle avoidance.

(Truthfully grounded in candidate profile. No qualifications fabricated.)""",
                cover_letter="""Dear XYZ Robotics Hiring Team,

I am writing to express my strong enthusiasm for the Robotics Software Intern position in Bangalore. As a Computer Science & Robotics undergraduate at IIT Kharagpur graduating in 2027, my technical focus directly aligns with XYZ Robotics' work on autonomous mobile robots.

Through my projects, I have implemented autonomous navigation stacks with ROS2 and Cartographer SLAM, as well as dynamic control algorithms in C++ and Python. Having followed XYZ Robotics' recent advancements in warehouse AMR fleets, I would welcome the opportunity to contribute directly to your perception and autonomy engineering team.

Thank you for your time and consideration.

Sincerely,
Aarav Sharma
aarav.sharma@example.com | +91 9876543210""",
                answers={
                    "why_role": "This role allows me to directly apply my hands-on ROS2 and C++ navigation experience to real-world autonomous industrial robots.",
                    "why_company": "XYZ Robotics is leading innovation in autonomous mobile robotics in India, and I admire your engineering rigor and fast deployment velocity.",
                    "relevant_experience": "I have built dynamic quadruped locomotion controllers and deployed Nav2 LiDAR SLAM systems at the IIT Kharagpur Centre for Robotics.",
                    "availability": "Available for a full-time 6-month or summer internship starting immediately or as per company schedule."
                },
                missing_information=[]
            )
            db.add(app)
            db.commit()

            # Seed an interview follow-up event
            follow_up = FollowUpEvent(
                application_id=app.id,
                event_type="INTERVIEW_INVITATION",
                scheduled_for=datetime.utcnow() + timedelta(days=3),
                status="PENDING",
                subject="Interview Invitation: Robotics Software Intern at XYZ Robotics",
                content="XYZ Robotics would like to invite you for a 45-minute Technical Discussion on ROS2 architecture and path planning.",
                interview_details={
                    "date": (datetime.utcnow() + timedelta(days=3)).strftime("%B %d, %Y at 3:00 PM IST"),
                    "round": "Technical Round 1 (Autonomy & ROS2 Architecture)",
                    "interviewers": "Lead Autonomy Engineer",
                    "meeting_link": "https://meet.google.com/xyz-robt-demo"
                },
                prep_notes="Review Cartographer SLAM parameter tuning, Nav2 BT navigator concepts, and C++ memory management (smart pointers)."
            )
            db.add(follow_up)
            db.commit()
