import re
import os
import io
from typing import List, Dict, Any, Tuple, Optional
from pypdf import PdfReader

DOMAIN_KEYWORDS = {
    "sde": [
        "backend", "frontend", "fullstack", "microservices", "api", "grpc", "rest", "react", "next.js",
        "spring", "django", "fastapi", "flask", "node.js", "docker", "kubernetes", "sql", "postgres",
        "redis", "ci/cd", "golang", "c++", "java", "typescript", "javascript", "graphql", "database",
        "distributed systems", "software engineering", "git", "linux", "systems"
    ],
    "data": [
        "data", "spark", "kafka", "etl", "pandas", "numpy", "machine learning", "deep learning",
        "nlp", "rag", "llm", "pytorch", "tensorflow", "analytics", "computer vision", "transformers",
        "scikit-learn", "data science", "neural network", "classification", "forecast", "prediction",
        "xgboost", "time series", "bi", "tableau", "powerbi", "sql", "feature engineering"
    ],
    "product": [
        "product", "product management", "roadmap", "user research", "ui/ux", "wireframe", "figma",
        "agile", "scrum", "feature prioritization", "kpi", "okr", "user persona", "metrics", "a/b testing",
        "stakeholder", "mvp", "go-to-market", "gtm", "market research", "customer feedback"
    ],
    "consult": [
        "consulting", "strategy", "market entry", "due diligence", "profitability", "valuation",
        "operations", "financial modeling", "competitive analysis", "business intelligence", "cost reduction",
        "growth strategy", "supply chain", "framework", "advisory", "benchmarking", "feasibility"
    ],
    "core": [
        "embedded", "firmware", "rtos", "microcontroller", "stm32", "arduino", "esp32", "ros", "ros2",
        "slam", "robotics", "vlsi", "verilog", "fpga", "hardware", "cad", "solidworks", "ansys",
        "fea", "control systems", "pid", "kinematics", "dynamics", "mechanical", "mechatronics",
        "motor driver", "sensor fusion", "autonomous", "actuator", "pcb", "can bus"
    ],
    "finance": [
        "finance", "trading", "quant", "order book", "arbitrage", "risk", "portfolio", "derivatives",
        "market", "equity", "fixed income", "banking", "black-scholes", "monte carlo", "algorithmic trading",
        "backtesting", "crypto", "hedge fund", "asset management", "financial analysis"
    ]
}

class MasterCVParser:
    """
    Comprehensive Master CV Parser & Domain Classifier.
    Parses Master CV text / markdown / PDF containing projects across all domains:
    SDE, Data, Product, Consult, Core (Robotics/Mech/Embedded), Finance.
    """

    @staticmethod
    def infer_domain(text: str) -> str:
        text_lower = text.lower()
        scores = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            count = 0
            for kw in keywords:
                count += len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
            scores[domain] = count

        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] > 0 else "general"

    @staticmethod
    def extract_tech_stack(text: str) -> List[str]:
        all_tech = [
            "Python", "C++", "C", "Java", "Go", "Rust", "TypeScript", "JavaScript", "SQL", "HTML", "CSS", "Bash",
            "ROS2", "ROS", "Gazebo", "MoveIt", "Nav2", "SLAM", "OpenCV", "SolidWorks", "ANSYS", "FEA",
            "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Hugging Face", "Transformers", "YOLO", "YOLOv8",
            "FastAPI", "Flask", "Django", "Node.js", "React", "Next.js", "Gradio", "Streamlit", "Docker", "Kubernetes",
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Unsloth", "QLoRA", "Triton", "Ollama", "Phi-4",
            "LightGBM", "XGBoost", "CatBoost", "Pandas", "NumPy", "Plotly", "Seaborn", "Matplotlib",
            "Arduino", "STM32", "ESP32", "FreeRTOS", "Kalman Filter", "LQR", "PID", "Pure Pursuit"
        ]
        found = []
        for t in all_tech:
            if re.search(rf"\b{re.escape(t)}\b", text, re.IGNORECASE):
                if t not in found:
                    found.append(t)
        return found

    @staticmethod
    def parse_projects_from_markdown(content: str) -> List[Dict[str, Any]]:
        """
        Splits master CV markdown into individual structured project blocks
        and tags each project with its inferred domain, tech stack, and action bullets.
        """
        projects = []
        
        # Split on markdown headers (## or ###) or major project title lines
        # Also handles "PROJECTS" section and split by project titles
        lines = content.splitlines()
        current_proj = None
        in_projects_section = False
        
        # Meta section skip headers
        skip_headers = [
            "personal information", "contact", "education", "skills", "skills and expertise",
            "coursework", "positions of responsibility", "extra curricular", "certifications", "internships"
        ]

        # First try section splitting by markdown headers
        header_sections = re.split(r'\n(?=#{1,4}\s+)', content)
        if len(header_sections) > 3:
            for sec in header_sections:
                sec_lines = [l.strip() for l in sec.strip().split('\n') if l.strip()]
                if not sec_lines:
                    continue
                header = sec_lines[0].lstrip('#').strip()
                if any(header.lower() == s or header.lower().startswith(s) for s in skip_headers):
                    continue
                body = "\n".join(sec_lines[1:]).strip() if len(sec_lines) > 1 else ""
                if len(body) > 20:
                    domain = MasterCVParser.infer_domain(f"{header} {body}")
                    tech = MasterCVParser.extract_tech_stack(f"{header} {body}")
                    bullets = [l.lstrip('-•* ').strip() for l in sec_lines[1:] if l.startswith(('-', '•', '*')) or len(l) > 40]
                    projects.append({
                        "name": header,
                        "domain": domain,
                        "description": body[:300],
                        "full_text": f"{header}\n{body}",
                        "tech_stack": tech,
                        "bullets": bullets if bullets else [body[:150]]
                    })

        if not projects:
            # Parse line by line looking for Project Title patterns
            proj_title_pattern = re.compile(r'^([A-Z0-9][A-Za-z0-9\s\-\:\(\)\,\.\/]+?)\s*(?:\||\[|\(|\—|\–)\s*(?:Self Project|Team|OpenIIT|Challenge|Hackathon|Lab|Research|Project|Advisor|Dr\.|Prof\.|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|202\d)', re.IGNORECASE)
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                # Check for section boundaries
                if any(line.lower().startswith(s) for s in ["education", "skills", "certifications", "coursework information", "positions of responsibility", "extra curricular"]):
                    in_projects_section = False
                elif "project" in line.lower() or "internship" in line.lower():
                    in_projects_section = True
                
                match = proj_title_pattern.search(line)
                # Or line has standalone title followed by bullet points
                is_standalone_header = (not line.startswith(('-', '•', '*')) and len(line) < 100 and i + 1 < len(lines) and lines[i+1].strip().startswith(('•', '-', '*')))

                if match or (in_projects_section and is_standalone_header and not any(line.lower().startswith(s) for s in skip_headers)):
                    title = match.group(1).strip() if match else line.strip()
                    title = re.sub(r'^(?:PROJECTS|INTERNSHIPS|KEY PROJECTS)\s*', '', title, flags=re.I).strip()
                    if len(title) > 3 and not any(title.lower().startswith(s) for s in skip_headers):
                        body_lines = []
                        i += 1
                        while i < len(lines):
                            next_line = lines[i].strip()
                            if not next_line:
                                i += 1
                                continue
                            if any(next_line.lower().startswith(s) for s in ["education", "skills and expertise", "certifications", "coursework", "positions of responsibility", "extra curricular"]):
                                break
                            if proj_title_pattern.search(next_line) or (not next_line.startswith(('-', '•', '*')) and len(next_line) < 100 and i + 1 < len(lines) and lines[i+1].strip().startswith(('•', '-', '*'))):
                                break
                            body_lines.append(next_line)
                            i += 1
                        
                        body_text = "\n".join(body_lines)
                        domain = MasterCVParser.infer_domain(f"{title} {body_text}")
                        tech = MasterCVParser.extract_tech_stack(f"{title} {body_text}")
                        bullets = [l.lstrip('-•* ').strip() for l in body_lines if len(l.strip()) > 20]
                        projects.append({
                            "name": title,
                            "domain": domain,
                            "description": body_text[:300],
                            "full_text": f"{title}\n{body_text}",
                            "tech_stack": tech,
                            "bullets": bullets if bullets else [body_text[:150]]
                        })
                        continue
                i += 1

        return projects

    @staticmethod
    def parse_full_master_cv(content: str, filename: str = "master_cv.md") -> Dict[str, Any]:
        """
        Parses master CV into complete structured candidate profile:
        - name, email, phone, college, degree, graduation_year, cgpa, links
        - skills
        - categorized projects (by domain)
        - work experience / internships
        """
        lines = [l.strip() for l in content.splitlines() if l.strip()]

        # 1. Candidate Name
        name = ""
        for line in lines[:6]:
            clean = line.split("|")[0].split("-")[0].strip("#* ")
            words = clean.split()
            if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.\'\-]+$", w) for w in words):
                if not any(w.lower() in ["resume", "curriculum", "vitae", "cv", "education"] for w in words):
                    name = clean
                    break
        if not name and lines:
            name = lines[0].split("|")[0].strip("#* ")

        # 2. Email & Phone
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
        email = email_match.group(0) if email_match else ""

        phone_match = re.search(r"(?:\+?\d{1,3}[-\s.]?)?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4,6}", content)
        phone = phone_match.group(0).strip() if phone_match else ""

        # 3. College & Degree
        college = "IIT Kharagpur" if "kharagpur" in content.lower() else ""
        if not college:
            college_match = re.search(r"(?:Indian\s+Institute\s+of\s+Technology|IIT|NIT|BITS|IIIT|DTU|NSUT|VIT)\s+[A-Za-z]+", content, re.I)
            if college_match:
                college = college_match.group(0).strip()

        degree = ""
        deg_match = re.search(r"\b(B\.?Tech|B\.?E\.?|Bachelor\s+of\s+Technology|M\.?Tech|Master\s+of\s+Technology|Dual\s+Degree)\b(?:\s*\(Hons\.\))?\s*(?:in\s+([A-Za-z\s\&]+))?", content, re.I)
        if deg_match:
            deg_type = deg_match.group(1).replace(".", "")
            branch = deg_match.group(2)
            degree = f"{deg_type} in {branch.strip()}" if branch else deg_type
        else:
            degree = "B.Tech in Engineering"

        # 4. Graduation Year & CGPA
        grad_year = None
        years = [int(y) for y in re.findall(r"\b(202[4-9]|203[0-5])\b", content)]
        if years:
            grad_year = max(years)

        cgpa = None
        cgpa_match = re.search(r"(?:CGPA|CPI|Marks|Grade)\s*[:=\/]?\s*([0-9]\.[0-9]{1,2})", content, re.I)
        if not cgpa_match:
            cgpa_match = re.search(r"\b([0-9]\.[0-9]{1,2})\s*\/\s*10", content)
        if cgpa_match:
            try:
                cgpa = float(cgpa_match.group(1))
            except ValueError:
                pass

        # 5. Skills
        skills = MasterCVParser.extract_tech_stack(content)

        # 6. Categorized Projects
        projects = MasterCVParser.parse_projects_from_markdown(content)

        # 7. Experience / Internships
        experience = []
        exp_match = re.search(r"(?:INTERNSHIPS|WORK EXPERIENCE|EXPERIENCE)[\s\S]*?(?=(?:PROJECTS|SKILLS|EDUCATION|CERTIFICATIONS|$))", content, re.I)
        if exp_match:
            exp_text = exp_match.group(0)
            exp_lines = [l.strip() for l in exp_text.splitlines() if l.strip()][1:]
            current_exp = None
            for l in exp_lines:
                if ("|" in l or " at " in l) and len(l) < 120 and not l.startswith(('-', '•', '*')):
                    if current_exp and current_exp.get("role"):
                        experience.append(current_exp)
                    parts = l.split("|")
                    current_exp = {
                        "role": parts[0].strip(),
                        "company": parts[1].strip() if len(parts) > 1 else "Research Lab",
                        "duration": parts[2].strip() if len(parts) > 2 else "",
                        "description": l
                    }
                elif current_exp:
                    current_exp["description"] += " " + l.lstrip('-•* ')
            if current_exp and current_exp.get("role"):
                experience.append(current_exp)

        return {
            "name": name or "Candidate",
            "email": email or "candidate@example.com",
            "phone": phone or "+91 9876543210",
            "college": college or "IIT Kharagpur",
            "degree": degree,
            "graduation_year": grad_year or 2028,
            "cgpa": cgpa or 8.39,
            "skills": skills,
            "projects": projects,
            "experience": experience,
            "raw_text": content,
            "filename": filename
        }
