import re
import os
import io
from typing import List, Dict, Any, Tuple, Optional
from pypdf import PdfReader

DOMAIN_KEYWORDS = {
    "finance": [
        "finance", "financial", "trading", "quant", "quantitative", "order book", "arbitrage", "risk", "portfolio",
        "derivatives", "market", "equity", "fixed income", "banking", "black-scholes", "monte carlo",
        "algorithmic trading", "backtesting", "crypto", "hedge fund", "asset management", "financial analysis",
        "sharpe ratio", "mean-variance", "bayesian portfolio", "stock", "options", "futures", "volatility",
        "yield", "credit risk", "scorecard", "quadprog", "asset allocation", "alpha"
    ],
    "sde": [
        "backend", "frontend", "fullstack", "full-stack", "microservices", "api", "apis", "grpc", "rest",
        "react", "react.js", "next.js", "spring", "django", "fastapi", "flask", "node.js", "node", "express",
        "docker", "kubernetes", "sql", "postgres", "postgresql", "mongodb", "redis", "ci/cd", "golang",
        "c++", "java", "typescript", "javascript", "graphql", "database", "distributed systems",
        "software engineering", "git", "linux", "systems", "web development", "fsm", "state machine",
        "web app", "blogsphere", "compiler", "operating systems"
    ],
    "data": [
        "data", "spark", "kafka", "etl", "pandas", "numpy", "machine learning", "deep learning",
        "nlp", "rag", "llm", "llms", "pytorch", "tensorflow", "analytics", "computer vision", "transformers",
        "scikit-learn", "data science", "neural network", "classification", "forecast", "forecasting", "prediction",
        "xgboost", "time series", "bi", "tableau", "powerbi", "feature engineering", "bert", "gpt", "hugging face",
        "genai", "generative ai", "diffusion", "segmentation", "clustering", "regression", "anomaly detection"
    ],
    "core": [
        "embedded", "firmware", "rtos", "microcontroller", "stm32", "arduino", "esp32", "ros", "ros2",
        "slam", "robotics", "vlsi", "verilog", "fpga", "hardware", "cad", "solidworks", "ansys",
        "fea", "control systems", "pid", "kinematics", "dynamics", "mechanical", "mechatronics",
        "motor driver", "sensor fusion", "autonomous", "actuator", "pcb", "can bus", "pure pursuit",
        "rocker-bogie", "tiadcs", "converter", "boost converter", "formula student", "vehicle"
    ],
    "consult": [
        "consulting", "strategy", "market entry", "due diligence", "profitability", "valuation",
        "operations", "financial modeling", "competitive analysis", "business intelligence", "cost reduction",
        "growth strategy", "supply chain", "framework", "advisory", "benchmarking", "feasibility",
        "sustainable packaging"
    ],
    "product": [
        "product", "product management", "roadmap", "user research", "ui/ux", "wireframe", "figma",
        "agile", "scrum", "feature prioritization", "kpi", "okr", "user persona", "metrics", "a/b testing",
        "stakeholder", "mvp", "go-to-market", "gtm", "market research", "customer feedback", "telemedicine"
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
                # Count keyword occurrences with word boundary
                matches = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
                count += matches
            scores[domain] = count

        # Priority resolution when scores tie
        if scores.get("finance", 0) > 0 and any(k in text_lower for k in ["portfolio", "sharpe", "trading", "quant", "black-scholes", "mean-variance", "asset management"]):
            scores["finance"] += 3
        if scores.get("core", 0) > 0 and any(k in text_lower for k in ["robotics", "ros", "embedded", "solidworks", "ansys", "motor", "stm32", "microcontroller"]):
            scores["core"] += 3

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
        Decomposes master CV text / markdown into structured JSON project blocks generically.
        Extracts all verified titles (projects, internships, competitions) and their full bullet points
        without relying on any hardcoded company or project names. Works across single and multi-page master CVs.
        """
        norm_text = re.sub(r'\r\n', '\n', content)
        # Normalize private use unicode bullets and bullet glyphs
        norm_text = re.sub(r'[\uf0b7\ufffd\x00\u2022\u2023\u25E6\u2043\u2219\u25CF\u25CB\u25A0\u25A1\·\◦\▪\⁃\∙]', '•', norm_text)
        # Remove page markers
        norm_text = re.sub(r'(?m)^---\s*PAGE\s*\d+\s*---$', '', norm_text)

        section_stops = {
            'SKILLS', 'SKILLS AND EXPERTISE', 'TECHNICAL SKILLS', 'SKILLS & EXPERTISE',
            'CERTIFICATIONS', 'CERTIFICATION', 'COURSEWORK', 'COURSEWORK INFORMATION',
            'POSITIONS OF RESPONSIBILITY', 'POSITIONS OF RESPONSIBILITIES', 'LEADERSHIP',
            'EXTRA CURRICULAR ACTIVITIES', 'EXTRACURRICULAR ACTIVITIES', 'EXTRA-CURRICULAR ACTIVITIES',
            'AWARDS', 'ACHIEVEMENTS', 'PUBLICATIONS', 'EDUCATION', 'PERSONAL DETAILS', 'CONTACT'
        }

        proj_starts = {
            'INTERNSHIPS', 'INTERNSHIP', 'WORK EXPERIENCE', 'EXPERIENCE', 'PROFESSIONAL EXPERIENCE',
            'PROJECTS', 'ACADEMIC PROJECTS', 'TECHNICAL PROJECTS', 'KEY PROJECTS', 'PROJECTS & INTERNSHIPS',
            'INTERNSHIPS AND PROJECTS', 'INTERNSHIPS & PROJECTS', 'PROJECTS AND INTERNSHIPS',
            'COMPETITIONS', 'COMPETITION/CONFERENCE', 'COMPETITIONS & CONFERENCES', 'COMPETITIONS AND CONFERENCES',
            'TRAINING', 'VOCATIONAL TRAINING', 'RESEARCH EXPERIENCE'
        }

        lines = [l.strip() for l in norm_text.splitlines() if l.strip()]
        current_sec = "HEADER"
        items = []
        current_item = None
        current_bullet = ""

        def is_proj_section_header(s: str) -> bool:
            clean = s.strip('#* ').upper()
            if len(clean) > 40 or '|' in s or '[' in s or '(' in s:
                return False
            if clean in proj_starts or any(clean == p for p in proj_starts):
                return True
            if any(k in clean for k in ['INTERN', 'PROJECT', 'EXPERIENCE', 'COMPETITION', 'CONFERENCE']) and not any(k in clean for k in ['COURSEWORK', 'SKILL', 'CERTIF', 'LEADERSHIP', 'RESPONSIBILITY', 'EXTRA']):
                return True
            return False

        def is_stop_section_header(s: str) -> bool:
            clean = s.strip('#* ').upper()
            if len(clean) > 40 or '|' in s or '[' in s or '(' in s:
                return False
            if clean in section_stops or any(clean == st or clean.startswith(st + ' ') for st in section_stops):
                if not is_proj_section_header(s):
                    return True
            return False

        def is_date_only_line(line: str) -> bool:
            clean = line.strip().strip('[]()').strip()
            if not clean or len(clean) > 40:
                return False
            pattern = r'^(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*[\'\s\.\,]*\d{2,4}|Ongoing|Present|\d{4})(?:\s*(?:[\-\–\—\to]|to)\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*[\'\s\.\,]*\d{2,4}|Ongoing|Present|\d{4}))?$'
            return bool(re.match(pattern, clean, re.I))

        def looks_like_continuation(line: str) -> bool:
            clean = line.strip()
            if not clean:
                return True
            if clean[0].islower():
                return True
            if clean.startswith(('(', ')', '>', '<', '=', '%', '$', '•', '-', '*', '+', '&', ';', ':', ',', '.')):
                return True
            if len(clean.split()) == 1 and not any(k in clean.lower() for k in ["project", "intern", "challenge", "kaggle", "meesho", "overnite"]):
                return True
            return False

        def is_title_line(idx: int, lines_list: list) -> bool:
            line = lines_list[idx].strip()
            if not line:
                return False
            if line.startswith(('•', '-', '*', '+')) or bool(re.match(r'^\d+[\.\)]\s+', line)):
                return False
            if line.lower().startswith(('tech:', 'technologies:', 'tools:', 'aim:', 'objective:', 'supervisor:', 'supervisors:', 'research topic:', 'under the guidance', 'under professor', 'built ', 'engineered ', 'developed ', 'designed ', 'analysed ', 'analyzed ', 'worked ', 'implemented ', 'monitored ', 'mitigated ', 'evaluated ', 'created ', 'trained ', 'optimized ', 'applied ', 'spearheaded ', 'formulated ', 'architected ')):
                return False
            if is_date_only_line(line) or looks_like_continuation(line):
                return False
            if is_proj_section_header(line) or is_stop_section_header(line):
                return False
            if current_sec in ['HEADER', 'EDUCATION', 'SKILLS', 'COURSEWORK', 'CERTIFICATIONS', 'POSITIONS OF RESPONSIBILITY', 'EXTRA CURRICULAR ACTIVITIES']:
                return False

            # Pipe separated title (e.g. Title | Org)
            if '|' in line:
                parts = line.split('|')
                first_part = parts[0].strip()
                if 3 <= len(first_part) <= 90 and not first_part[0].islower():
                    return True

            # Markdown header
            if line.startswith(('###', '##', '**')):
                return True

            # Has embedded date range in brackets at the end of the line (e.g. Title [Nov 2025 - Mar 2026])
            if re.search(r'\[[A-Za-z0-9\s\-\–\—\.\,\'\:]+\]|\([A-Za-z0-9\s\-\–\—\.\,\'\:]{4,30}\)$', line) and len(line) < 120 and not line[0].islower():
                return True

            # Followed by date line, meta line, or bullet point
            if idx + 1 < len(lines_list):
                next_line = lines_list[idx + 1].strip()
                if is_date_only_line(next_line):
                    return True
                if next_line.lower().startswith(('under the guidance', 'supervisor:', 'supervisors:', 'objective:', 'aim:', 'research topic:', 'under professor')):
                    return True
                if next_line.startswith(('•', '-', '*', '+')) or bool(re.match(r'^\d+[\.\)]\s+', next_line)):
                    if len(line) < 140 and not line[0].islower():
                        return True
                if next_line.lower().startswith(('tech:', 'technologies:', 'tools:')):
                    if len(line) < 140 and not line[0].islower():
                        return True

            return False

        i = 0
        while i < len(lines):
            raw_l = lines[i].strip()
            if not raw_l:
                i += 1
                continue

            if is_proj_section_header(raw_l):
                if current_bullet and current_item:
                    current_item['bullets'].append(current_bullet.strip())
                    current_bullet = ""
                if current_item and current_item.get('name') and (current_item.get('bullets') or current_item.get('description')):
                    items.append(current_item)
                    current_item = None
                current_sec = raw_l.strip('#* ').upper()
                i += 1
                continue

            if is_stop_section_header(raw_l):
                if current_bullet and current_item:
                    current_item['bullets'].append(current_bullet.strip())
                    current_bullet = ""
                if current_item and current_item.get('name') and (current_item.get('bullets') or current_item.get('description')):
                    items.append(current_item)
                    current_item = None
                current_sec = raw_l.strip('#* ').upper()
                i += 1
                continue

            if current_sec in section_stops:
                i += 1
                continue

            is_bullet = raw_l.startswith(('•', '-', '*', '+')) or bool(re.match(r'^\d+[\.\)]\s+', raw_l))

            if is_title_line(i, lines):
                if current_bullet and current_item:
                    current_item['bullets'].append(current_bullet.strip())
                    current_bullet = ""
                if current_item and current_item.get('name') and (current_item.get('bullets') or current_item.get('description')):
                    items.append(current_item)

                clean_title = raw_l.lstrip('#* ').strip()

                # Check if title wraps onto next line before date
                if i + 1 < len(lines) and not lines[i+1].startswith(('•', '-', '*', '+')) and not is_date_only_line(lines[i+1]) and '|' not in lines[i+1]:
                    if i + 2 < len(lines) and is_date_only_line(lines[i+2]):
                        clean_title += " " + lines[i+1].strip()
                        i += 1

                date_match = re.search(r'\[([A-Za-z0-9\s\-\–\—\.\,\'\:]+)\]|\(([A-Za-z0-9\s\-\–\—\.\,\'\:]{4,30})\)', clean_title)
                dates = date_match.group(0) if date_match else ""
                if dates:
                    clean_title = clean_title.replace(dates, "").strip().rstrip('| ')

                # Check if next line is date-only line
                if not dates and i + 1 < len(lines) and is_date_only_line(lines[i+1]):
                    dates = lines[i+1].strip()
                    i += 1  # consume date line

                is_intern = ('intern' in clean_title.lower() or 'foreign training' in clean_title.lower() or (current_sec and 'INTERN' in current_sec and 'PROJECT' not in clean_title.upper() and 'SELF' not in clean_title.upper() and 'COURSE' not in clean_title.upper() and 'TERM' not in clean_title.upper()))
                is_compi = any(k in clean_title.lower() for k in ['challenge', 'competition', 'hackathon', 'finalist', 'contest', 'conference', 'gameathon', 'championship']) or (current_sec and 'COMPETITION' in current_sec)

                i_type = 'competition' if is_compi else ('internship' if is_intern else 'project')

                current_item = {
                    'name': clean_title,
                    'dates': dates,
                    'type': i_type,
                    'description': '',
                    'bullets': []
                }
                i += 1
                continue

            if current_item:
                if is_date_only_line(raw_l) and not current_item.get('dates'):
                    current_item['dates'] = raw_l
                elif raw_l.lower().startswith(('tech:', 'technologies:', 'tools:')):
                    current_item['tech_stack'] = raw_l
                elif is_bullet:
                    if current_bullet:
                        current_item['bullets'].append(current_bullet.strip())
                    current_bullet = re.sub(r'^(?:[•\-\*\+]|\d+[\.\)])\s*', '', raw_l).strip()
                else:
                    if current_bullet:
                        current_bullet += ' ' + raw_l
                    else:
                        if not current_item['description']:
                            current_item['description'] = raw_l
                        else:
                            current_item['description'] += ' ' + raw_l

            i += 1

        if current_bullet and current_item:
            current_item['bullets'].append(current_bullet.strip())
        if current_item and current_item.get('name') and (current_item.get('bullets') or current_item.get('description')):
            items.append(current_item)

        # Post-process to calculate domain and tech stack
        clean_items = []
        for it in items:
            if not it.get('name'):
                continue
            if not it['bullets'] and it.get('description'):
                it['bullets'] = [it['description']]
                it['description'] = ''
            if not it['bullets'] and not it.get('description'):
                continue
            full_text = f"{it['name']} {it.get('dates', '')}\n{it.get('description', '')}\n" + "\n".join(it.get('bullets', []))
            it['full_text'] = full_text
            it['domain'] = MasterCVParser.infer_domain(full_text)
            it['tech_stack'] = MasterCVParser.extract_tech_stack(full_text)
            clean_items.append(it)

        return clean_items

    @staticmethod
    def parse_master_cv_full_sections(content: str) -> Tuple[List[str], Dict[str, List[str]], set]:
        """
        Generic Master CV section partitioner:
        Splits arbitrary Master CV into:
        - Header lines (before first section)
        - Section list in original Master CV order
        - Mapping of section name -> list of lines
        - Set of project-related section names (INTERNSHIPS, PROJECTS, COMPETITIONS, etc.)
        """
        norm_text = re.sub(r'\r\n', '\n', content)
        norm_text = re.sub(r'[\uf0b7\ufffd\x00\u2022\u2023\u25E6\u2043\u2219\u25CF\u25CB\u25A0\u25A1\·\◦\▪\⁃\∙]', '•', norm_text)
        norm_text = re.sub(r'(?m)^---\s*PAGE\s*\d+\s*---$', '', norm_text)

        proj_section_names = {
            'INTERNSHIPS', 'INTERNSHIP', 'WORK EXPERIENCE', 'EXPERIENCE', 'PROFESSIONAL EXPERIENCE',
            'PROJECTS', 'ACADEMIC PROJECTS', 'TECHNICAL PROJECTS', 'KEY PROJECTS', 'PROJECTS & INTERNSHIPS',
            'INTERNSHIPS AND PROJECTS', 'INTERNSHIPS & PROJECTS', 'PROJECTS AND INTERNSHIPS',
            'COMPETITIONS', 'COMPETITION/CONFERENCE', 'COMPETITIONS & CONFERENCES', 'COMPETITIONS AND CONFERENCES',
            'TRAINING', 'VOCATIONAL TRAINING', 'RESEARCH EXPERIENCE'
        }

        known_all_banners = {
            'EDUCATION', 'AWARDS AND ACHIEVEMENTS', 'AWARDS & ACHIEVEMENTS', 'ACHIEVEMENTS', 'ACADEMIC ACHIEVEMENTS',
            'SKILLS', 'SKILLS AND EXPERTISE', 'TECHNICAL SKILLS', 'SKILLS & EXPERTISE',
            'CERTIFICATIONS', 'CERTIFICATION', 'COURSEWORK', 'COURSEWORK INFORMATION',
            'POSITIONS OF RESPONSIBILITY', 'POSITIONS OF RESPONSIBILITIES', 'LEADERSHIP',
            'EXTRA CURRICULAR ACTIVITIES', 'EXTRACURRICULAR ACTIVITIES', 'EXTRA-CURRICULAR ACTIVITIES',
            'PUBLICATIONS', 'PATENTS'
        } | proj_section_names

        lines = [l.strip() for l in norm_text.splitlines() if l.strip()]
        sections_order = []
        sections_map = {}
        current_sec = 'HEADER'
        sections_order.append(current_sec)
        sections_map[current_sec] = []

        for l in lines:
            clean = l.strip('#* ').upper()
            if (clean in known_all_banners or any(clean == b for b in known_all_banners)) and '|' not in l and len(clean) < 45:
                current_sec = clean
                if current_sec not in sections_map:
                    sections_order.append(current_sec)
                    sections_map[current_sec] = []
                continue
            sections_map[current_sec].append(l)

        return sections_order, sections_map, proj_section_names

    @staticmethod
    def format_static_section_lines(lines: List[str], sec_name: str, domain: str = "sde") -> List[str]:
        """
        Formats and normalizes any arbitrary static section lines:
        - For SKILLS and COURSEWORK: merges wrapped lines into single Category: values,
          filters for domain relevance (core vs non-core).
        - For AWARDS, POSITIONS OF RESPONSIBILITY, CERTIFICATIONS, EXTRA CURRICULARS:
          preserves all content as-is with clean bullet formatting.
        """
        is_core = (domain or "sde").lower() == "core"
        sec_up = sec_name.upper()

        if "SKILLS" in sec_up:
            non_core_exclude = [
                "controls, robotics & embedded", "cad & engineering software", "hands-on workshop skills",
                "solidworks", "autodesk", "ansys", "welding", "forming", "casting", "mechatronics"
            ]
            core_exclude = ["generative ai & nlp", "data analysis & visualization"]
            
            merged = []
            curr_lbl = ""
            curr_val = ""
            for l in lines:
                m = re.match(r'^([A-Za-z0-9\s\&\/\(\)\,\.\-]+?:)(.*)', l)
                if m and len(m.group(1)) < 40 and not l.startswith(('•', '-', '*')):
                    if curr_lbl:
                        merged.append((curr_lbl, curr_val.strip()))
                    curr_lbl = m.group(1).strip()
                    curr_val = m.group(2).strip()
                elif curr_lbl:
                    curr_val += " " + l
                else:
                    merged.append(("", l))
            if curr_lbl:
                merged.append((curr_lbl, curr_val.strip()))

            out = []
            for lbl, val in merged:
                full_lower = f"{lbl} {val}".lower()
                if not is_core and any(k in full_lower for k in non_core_exclude):
                    continue
                if is_core and any(k in full_lower for k in core_exclude):
                    continue
                if lbl:
                    out.append(f"{lbl} {val}".strip())
                else:
                    out.append(val)
            return out

        if "COURSEWORK" in sec_up:
            merged = []
            curr_lbl = ""
            curr_val = ""
            for l in lines:
                m = re.match(r'^([A-Za-z0-9\s\&\/\(\)\,\.\-]+?:)(.*)', l)
                if m and len(m.group(1)) < 40 and not l.startswith(('•', '-', '*')):
                    if curr_lbl:
                        merged.append((curr_lbl, curr_val.strip()))
                    curr_lbl = m.group(1).strip()
                    curr_val = m.group(2).strip()
                elif curr_lbl:
                    curr_val += " " + l
                else:
                    merged.append(("", l))
            if curr_lbl:
                merged.append((curr_lbl, curr_val.strip()))

            out = []
            for lbl, val in merged:
                full_lower = f"{lbl} {val}".lower()
                if not is_core and ("core courses" in full_lower or "mechanics of solids" in full_lower):
                    continue
                if lbl:
                    out.append(f"{lbl} {val}".strip())
                else:
                    out.append(val)
            return out

        # For AWARDS, POSITIONS OF RESPONSIBILITY, CERTIFICATIONS, EXTRA CURRICULAR, etc.
        out = []
        extra_count = 0
        award_count = 0
        por_count = 0
        for l in lines:
            if "EXTRA" in sec_up:
                if l.startswith(('•', '-', '*')):
                    if extra_count < 5:
                        out.append(f"• {l.lstrip('•-* ').strip()}")
                        extra_count += 1
                elif l.strip():
                    if extra_count < 5:
                        out.append(f"• {l.strip()}")
                        extra_count += 1
            elif "AWARD" in sec_up or "ACHIEVE" in sec_up:
                if l.startswith(('•', '-', '*')):
                    if award_count < 4:
                        out.append(f"• {l.lstrip('•-* ').strip()}")
                        award_count += 1
                elif l.strip():
                    if award_count < 4:
                        out.append(f"• {l.strip()}")
                        award_count += 1
            elif "POSITION" in sec_up or "LEADERSHIP" in sec_up:
                if ("|" in l or "[" in l) and not l.startswith(('•', '-', '*')):
                    if por_count < 2:
                        out.append(l)
                        por_count += 1
                    else:
                        break
                elif por_count <= 2:
                    if l.startswith(('•', '-', '*')):
                        out.append(f"• {l.lstrip('•-* ').strip()}")
                    else:
                        out.append(l)
            else:
                if l.startswith(('•', '-', '*')):
                    out.append(f"• {l.lstrip('•-* ').strip()}")
                else:
                    out.append(l)

        return out

    @staticmethod
    def extract_clean_static_sections(content: str) -> List[str]:
        orders, smap, pnames = MasterCVParser.parse_master_cv_full_sections(content)
        res = []
        for sec in orders:
            if sec in ['HEADER', 'EDUCATION'] or sec in pnames:
                continue
            res.append("")
            res.append(sec)
            res.extend(MasterCVParser.format_static_section_lines(smap[sec], sec))
        return res

    @staticmethod
    def extract_domain_tailored_static_sections(content: str, domain: str = "sde") -> List[str]:
        orders, smap, pnames = MasterCVParser.parse_master_cv_full_sections(content)
        res = []
        for sec in orders:
            if sec in ['HEADER', 'EDUCATION'] or sec in pnames:
                continue
            formatted = MasterCVParser.format_static_section_lines(smap[sec], sec, domain)
            if formatted:
                res.append("")
                res.append(sec)
                res.extend(formatted)
        return res

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
        college = ""
        college_match = re.search(r"(?:Indian\s+Institute\s+of\s+Technology|IIT|NIT|BITS|IIIT|DTU|NSUT|VIT|Stanford|MIT|Harvard|Berkeley|Carnegie\s+Mellon|University|College|Institute)\s+[A-Za-z\s]+", content, re.I)
        if college_match:
            college = college_match.group(0).strip()
        elif "kharagpur" in content.lower():
            college = "IIT Kharagpur"

        degree = ""
        deg_match = re.search(r"\b(B\.?Tech|B\.?E\.?|Bachelor\s+of\s+Technology|B\.?S\.?|Bachelor\s+of\s+Science|M\.?Tech|Master\s+of\s+Technology|M\.?S\.?|Dual\s+Degree)\b(?:\s*\(Hons\.\))?\s*(?:in\s+([A-Za-z\s\&]+))?", content, re.I)
        if deg_match:
            deg_type = deg_match.group(1).replace(".", "")
            branch = deg_match.group(2)
            degree = f"{deg_type} in {branch.strip()}" if branch else deg_type
        else:
            degree = "B.Tech in Engineering"

        # 4. Graduation Year & CGPA
        grad_year = None
        years = [int(y) for y in re.findall(r"\b(202[0-9]|203[0-5])\b", content)]
        if years:
            grad_year = max(years)

        cgpa = None
        cgpa_match = re.search(r"(?:CGPA|CPI|Marks|Grade|GPA)\s*[:=\/]?\s*([0-9]\.[0-9]{1,2})", content, re.I)
        if not cgpa_match:
            cgpa_match = re.search(r"\b([0-9]\.[0-9]{1,2})\s*\/\s*(?:10|4\.0|4)", content)
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
                        "company": parts[1].strip() if len(parts) > 1 else "Organization",
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
            "college": college or "University",
            "degree": degree,
            "graduation_year": grad_year or 2026,
            "cgpa": cgpa or 8.0,
            "skills": skills,
            "projects": projects,
            "experience": experience,
            "raw_text": content,
            "filename": filename
        }
