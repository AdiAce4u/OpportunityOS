from typing import Any
from app.db.session import SessionLocal
from app.models import Job

COMPANY_KNOWLEDGE_BASE = {
    "XYZ Robotics": {
        "company_summary": "XYZ Robotics builds next-generation autonomous industrial mobile robots (AMRs) for smart warehousing.",
        "domain": "Autonomous Robotics & Industrial Automation",
        "size": "50-150 employees",
        "technology": ["ROS2 Humble", "Modern C++", "Python", "Gazebo", "SLAM", "NVIDIA Jetson"],
        "recent_news": [
            "Secured $12M Series A funding for automated warehouse expansion across Asia-Pacific.",
            "Launched new heavy-payload omnidirectional AMR platform."
        ],
        "reputation_notes": [
            "High engineering bar and rigorous hardware-in-the-loop development cycle.",
            "Strong internship conversion rate to full-time engineering roles."
        ]
    },
    "ABC AI": {
        "company_summary": "ABC AI is an applied machine intelligence research lab developing computer vision and multimodal foundation models.",
        "domain": "Applied Artificial Intelligence & Computer Vision",
        "size": "100-250 employees",
        "technology": ["PyTorch", "Python", "Transformers", "CUDA", "TensorRT", "FastAPI"],
        "recent_news": [
            "Published state-of-the-art vision benchmark paper accepted at CVPR.",
            "Released open-weights perception model for edge devices."
        ],
        "reputation_notes": [
            "Exceptional research freedom and mentorship from ex-FAANG AI scientists.",
            "100% remote-first asynchronous engineering culture."
        ]
    },
    "DEF Autonomy": {
        "company_summary": "DEF Autonomy designs drive-by-wire autonomy kits and navigation platforms for heavy industrial machinery.",
        "domain": "Autonomous Vehicles & Mining Automation",
        "size": "200-500 employees",
        "technology": ["ROS2", "C++17", "LiDAR Fusion", "Kalman Filters", "Real-Time Linux"],
        "recent_news": [
            "Logged over 500,000 autonomous hours without a single safety incident in open-pit mines.",
            "Partnered with leading equipment OEM for factory-installed autonomy."
        ],
        "reputation_notes": [
            "Industry leader in functional safety and harsh-environment ruggedized robotics."
        ]
    },
    "NeuralDrive Labs": {
        "company_summary": "NeuralDrive Labs builds generalist robotic dexterity algorithms and bipedal humanoid platforms.",
        "domain": "Embodied AI & Humanoid Robotics",
        "size": "30-80 employees",
        "technology": ["PyTorch", "ROS2 Humble", "Isaac Gym", "NVIDIA Jetson", "C++20"],
        "recent_news": [
            "Demonstrated whole-body teleoperation and dexterous manipulation via VR headset.",
            "Backed by top Silicon Valley and Indian robotics angels."
        ],
        "reputation_notes": [
            "High-energy startup culture with access to massive GPU clusters and prototype hardware."
        ]
    },
    "Apex Robotics": {
        "company_summary": "Apex Robotics manufactures drone avionics, autopilot boards, and agricultural spraying rovers.",
        "domain": "Drones & Precision AgriTech",
        "size": "80-150 employees",
        "technology": ["STM32", "FreeRTOS", "micro-ROS", "C++", "Python", "KiCad"],
        "recent_news": [
            "Obtained DGCA commercial type certification for 25kg payload drone.",
            "Expanded precision farming contracts across 100,000 acres."
        ],
        "reputation_notes": [
            "Great hands-on hardware lab for firmware, board design, and motor control."
        ]
    }
}

def research_company(company_name: str) -> dict[str, Any]:
    """
    Researches the company background, tech stack, and recent updates.
    """
    for name, data in COMPANY_KNOWLEDGE_BASE.items():
        if name.lower() in company_name.lower() or company_name.lower() in name.lower():
            return {
                "company_name": name,
                **data
            }
            
    # Generic fallback
    return {
        "company_name": company_name,
        "company_summary": f"{company_name} is an active technology organization hiring technical specialists.",
        "domain": "Engineering & Technology",
        "size": "50-500 employees",
        "technology": ["Python", "Modern Software Stack", "Linux"],
        "recent_news": [f"{company_name} is expanding engineering teams for next-generation products."],
        "reputation_notes": ["Active engineering culture with positive candidate reviews."]
    }
