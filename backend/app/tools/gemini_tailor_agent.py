import os
import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings

logger = logging.getLogger("opportunityos.gemini_tailor")
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# GEMINI SYSTEM PROMPT FOR AGENTIC MASTER CV DECOMPOSITION & TAILORING
# ==============================================================================
GEMINI_RESUME_TAILOR_SYSTEM_PROMPT = """
You are an expert AI Resume Intelligence Agent for OpportunityOS.
Your job is to analyze a candidate's complete Master CV, extract all verified projects and internships without losing any bullet points, classify them by technical domain, and produce a JD-tailored 1-page CV selection.

### STRICT RULES:
1. **PROJECT BOUNDARY & BULLET INTEGRITY**:
   - Each project or internship starts with a Title Line (often formatted as `Title | Affiliation/Type [Dates]`).
   - Each project may have a subtitle / Tech stack line or a 1-line overview.
   - Each project has bullet points starting with `•`, `-`, or `*`.
   - A blank line or the next title marks the end of a project.
   - **DO NOT TRUNCATE, SUMMARIZE, OR SHORTEN ANY BULLET POINT.** Every bullet point under a selected project must be copied 100% in full.
   - **DO NOT INVENT SYNTHETIC FACTS OR NUMBERS.** Strictly use verified facts from the Master CV.

2. **DOMAIN CLASSIFICATION**:
   Classify each project and internship into one of the 5 domains:
   - `sde`: Software Engineering, Backend, Frontend, Full-stack, REST APIs, Microservices, Systems, Distributed Systems, C++, Java, Node.js, FastAPI, Docker, Kubernetes, Database, Routing, Concurrency, Algorithms, Web App.
   - `data`: Machine Learning, Deep Learning, NLP, LLMs, Computer Vision, Transformers, PyTorch, TensorFlow, Data Science, Analytics, BI, XGBoost, Scikit-learn, Feature Engineering, Churn, Crop Health, Skin Lesion, Qwen, Unsloth, QLoRA.
   - `core`: Robotics, Embedded, Microcontrollers (STM32, Arduino, ESP32), ROS, ROS2, Control Systems (PID, LQR, Pure Pursuit), Kinematics, Dynamics, Mechanical, Mechatronics, FEA, SOLIDWORKS, ANSYS, Motor Drivers, Sensors, Drones, Rover, IRC, Vehicle Simulation, Steam Turbine, Stress Field.
   - `finance`: Quantitative Finance, Trading, Arbitrage, Risk Management, Order Book, Backtesting, Time Series, Stock Forecasting, LSTM, Derivatives, Portfolio Optimization.
   - `consult`: Consulting, Business Strategy, Market Entry, Operations, Due Diligence, Business Intelligence, Case Study, Product Management, Netflix Content Strategy.

3. **DOMAIN VALIDATION GUARDRAIL**:
   - If the candidate's Master CV contains **ZERO (0)** projects or internships matching the target job domain, you MUST return:
     `{"error": "NO_DOMAIN_PROJECTS", "message": "No projects found matching the {domain} domain in your Master CV. Please upload or add relevant projects to apply for this role."}`

4. **SELECTION & RANKING**:
   - If projects are available, select the **top 2-3 closest projects/internships** that best align with the Target Job Description so that all bullet points fit completely on 1 single A4 page.

5. **DYNAMIC INTERNSHIP SEGREGATION**:
   - If the candidate has **2 or more (>=2) internships/research internships** matching the target profile:
     Set `"has_separate_internships": true`, and place them in `"selected_internships"`. Place regular projects in `"selected_projects"`.
   - If there is **1 internship**:
     Set `"has_separate_internships": false`, and put it at the top of `"selected_internships_and_projects"`.
   - If there are **0 internships**:
     Set `"has_separate_internships": false`, and put the projects in `"selected_projects"`.

6. **OUTPUT FORMAT**:
   Return ONLY a valid JSON object matching this schema:
   ```json
   {
     "target_domain": "sde | data | core | finance | consult",
     "has_separate_internships": boolean,
     "selected_internships": [
       {
         "name": "Full Title | Organization / Advisor",
         "dates": "[Month Year - Month Year]",
         "tech_stack": "Tech: ... (or empty string)",
         "description": "1-line overview (or empty string)",
         "bullets": ["Full non-truncated bullet 1", "Full non-truncated bullet 2"]
       }
     ],
     "selected_projects": [
       {
         "name": "Full Project Title | Type",
         "dates": "[Month Year - Month Year]",
         "tech_stack": "Tech: ... (or empty string)",
         "description": "1-line overview (or empty string)",
         "bullets": ["Full non-truncated bullet 1", "Full non-truncated bullet 2", "Full non-truncated bullet 3"]
       }
     ],
     "rationale": "Brief reason why these projects were chosen for this JD"
   }
   ```
"""

class GeminiTailorAgent:
    """
    Agentic LLM Tailor Engine with Fallback AST Chunking.
    Handles project extraction, domain classification, validation guardrails,
    and complete non-truncated bullet retention.
    """

    @staticmethod
    def infer_target_domain(job: Dict[str, Any]) -> str:
        title = (job.get('title') or '').lower()
        skills = " ".join(job.get('required_skills', [])).lower()
        desc = (job.get('description') or '').lower()
        combined = f"{title} {desc} {skills}"

        # 1. Check title first (highest precision)
        if any(k in title for k in ["sde", "software", "backend", "frontend", "fullstack", "full stack", "web dev", "developer"]):
            return "sde"
        if any(k in title for k in ["data", "machine learning", "ml", "ai", "deep learning", "nlp", "computer vision"]):
            return "data"
        if any(k in title for k in ["robotics", "embedded", "hardware", "mechanical", "control", "mechatronics"]):
            return "core"
        if any(k in title for k in ["quant", "finance", "financial", "trader", "trading", "analyst"]):
            return "finance"
        if any(k in title for k in ["consult", "consulting", "strategy", "product manager", "operations"]):
            return "consult"

        # 2. Check combined text
        if any(k in combined for k in ["robotics", "embedded", "ros", "ros2", "mechanical", "control", "hardware", "firmware", "slam", "kinematics", "solidworks", "ansys", "fea", "drone"]):
            return "core"
        if any(k in combined for k in ["machine learning", "deep learning", "nlp", "llm", "pytorch", "tensorflow", "computer vision", "data science", "analytics", "transformers", "ai"]):
            return "data"
        if any(k in combined for k in ["quant", "trading", "finance", "financial", "arbitrage", "risk", "portfolio", "derivatives", "options"]):
            return "finance"
        if any(k in combined for k in ["consult", "consulting", "strategy", "market entry", "operations", "product manager", "product management", "business intelligence"]):
            return "consult"
        return "sde"

    @staticmethod
    def parse_blocks_from_raw_cv(master_cv_text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Deterministic block-level parser using blank lines and bold project titles
        to extract projects and internships with 100% full multi-line bullets.
        """
        norm_text = re.sub(r'\r\n', '\n', master_cv_text)
        
        # Match project and internship header lines
        pattern = re.compile(
            r'(?m)^([A-Z0-9][A-Za-z0-9\s\-\:\(\)\,\.\/\&]+?\s*\|\s*(?:Self Project|Team|OpenIIT|Challenge|Hackathon|Lab|Research|Project|Advisor|Dr\.|Prof\.|Mechatronics|LTF|Carnegie|Bajaj|NTPC|CoEAMT|Finalist|Google|DeepLearning|Singrauli|Vocational|Technology Filmmaking)[^\n]*)'
        )

        matches = list(pattern.finditer(norm_text))
        projects = []
        internships = []

        for idx, match in enumerate(matches):
            header_full = match.group(1).strip()
            
            # Clean non-title prefixes if attached
            for prefix in ["INTERNSHIPS", "PROJECTS", "COMPETITION/CONFERENCE", "COMPETITIONS"]:
                if header_full.startswith(prefix):
                    header_full = header_full[len(prefix):].strip()

            start_pos = match.end()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(norm_text)
            
            body_block = norm_text[start_pos:end_pos].strip()
            
            # Stop if hit other major sections (Skills, Certifications, Coursework, etc.)
            sec_break = re.search(r'(?m)^(SKILLS AND EXPERTISE|SKILLS|CERTIFICATIONS|COURSEWORK INFORMATION|COURSEWORK|POSITIONS OF RESPONSIBILITY|EXTRA CURRICULAR ACTIVITIES)', body_block)
            if sec_break:
                body_block = body_block[:sec_break.start()].strip()

            lines = [l.strip() for l in body_block.splitlines() if l.strip()]

            # Extract date from header line
            date_match = re.search(r'\[([A-Za-z0-9\s\-\–\—\.]+)\]', header_full)
            dates = date_match.group(0) if date_match else ""
            clean_title = header_full
            if dates:
                clean_title = header_full.replace(dates, "").strip().rstrip('| ')

            tech_line = ""
            summary_lines = []
            bullets = []
            current_bullet = ""

            for l in lines:
                if l.lower().startswith("tech:"):
                    tech_line = l
                elif l.startswith(('•', '-', '*')):
                    if current_bullet:
                        bullets.append(current_bullet.strip())
                    current_bullet = l.lstrip('•-* ').strip()
                else:
                    if current_bullet:
                        current_bullet += " " + l
                    else:
                        summary_lines.append(l)

            if current_bullet:
                bullets.append(current_bullet.strip())

            full_text = f"{clean_title} {dates}\n{tech_line}\n" + " ".join(summary_lines) + "\n" + "\n".join(bullets)
            from app.tools.cv_parser_engine import MasterCVParser
            domain = MasterCVParser.infer_domain(full_text)
            tech = MasterCVParser.extract_tech_stack(full_text)

            item = {
                "name": clean_title,
                "dates": dates,
                "tech_stack": tech_line,
                "description": " ".join(summary_lines).strip(),
                "bullets": bullets if bullets else [" ".join(summary_lines).strip()],
                "domain": domain,
                "tech_list": tech,
                "full_text": full_text
            }

            is_intern = ("intern" in clean_title.lower() or "advisor" in clean_title.lower() or "cmu" in clean_title.lower() or "ntpc" in clean_title.lower() or "coeamt" in clean_title.lower())
            if is_intern and "PROJECT" not in clean_title.upper() and "SELF PROJECT" not in clean_title.upper():
                internships.append(item)
            else:
                projects.append(item)

        return projects, internships

    @staticmethod
    def tailor_with_llm(
        master_cv_text: str,
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the Gemini LLM agent to classify and select relevant projects.
        Falls back to AST chunking if offline or API key not present.
        """
        target_domain = GeminiTailorAgent.infer_target_domain(job)
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("LLM_API_KEY", "")

        logger.info(f"🧠 [GeminiTailorAgent] Invoked for Role: '{job.get('title')}' at '{job.get('company')}' (Target Domain: {target_domain.upper()})")
        logger.info(f"🔑 [GeminiTailorAgent] Gemini API Key present: {bool(api_key)}")

        # Step 1: Extract block-level projects & internships
        all_projects, all_internships = GeminiTailorAgent.parse_blocks_from_raw_cv(master_cv_text)
        logger.info(f"📦 [GeminiTailorAgent] Extracted {len(all_projects)} projects and {len(all_internships)} internships from Master CV")

        # Step 2: If Gemini API is available, invoke Gemini
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)

                user_prompt = f"""
TARGET JOB:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location', 'India')}
Required Skills: {', '.join(job.get('required_skills', []))}
Description: {job.get('description', '')}
Target Domain Track: {target_domain}

CANDIDATE MASTER CV (RAW TEXT):
{master_cv_text}
"""
                response = None
                model_candidates = [
                    settings.llm_model,
                    "gemini-flash-latest",
                    "gemini-3.8-flash",
                    "gemini-3.5-flash",
                    "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite",
                    "gemini-pro-latest"
                ]
                seen_models = set()
                for m_name in model_candidates:
                    if not m_name or m_name in seen_models:
                        continue
                    seen_models.add(m_name)
                    try:
                        logger.info(f"🚀 [GeminiTailorAgent] Sending request to {m_name}...")
                        model = genai.GenerativeModel(m_name, system_instruction=GEMINI_RESUME_TAILOR_SYSTEM_PROMPT)
                        response = model.generate_content(user_prompt)
                        if response and response.text:
                            logger.info(f"✅ [GeminiTailorAgent] Successfully received output from {m_name}")
                            break
                    except Exception as me:
                        logger.warning(f"⚠️ [GeminiTailorAgent] {m_name} failed: {me}")

                if response and response.text:
                    raw_resp = response.text.strip()
                    logger.info(f"📥 [GeminiTailorAgent] Received response ({len(raw_resp)} chars)")

                    clean_json = raw_resp.lstrip("```json").rstrip("```").strip()
                    parsed = json.loads(clean_json)

                    if parsed.get("error") == "NO_DOMAIN_PROJECTS":
                        raise ValueError(parsed.get("message", f"No projects found matching the {target_domain.upper()} domain in your Master CV."))

                    if parsed.get("selected_projects") or parsed.get("selected_internships"):
                        return parsed

            except ValueError as ve:
                raise ve
            except Exception as e:
                logger.warning(f"⚠️ [GeminiTailorAgent] Gemini API fallback to AST Engine: {e}")

        # Step 3: High-Precision Deterministic AST Engine Fallback
        domain_projects = [
            p for p in all_projects
            if p.get("domain", "").lower() == target_domain
        ]

        if not domain_projects:
            combined_jd = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('required_skills', []))}".lower()
            for p in all_projects:
                p_text = f"{p.get('name', '')} {p.get('description', '')} {' '.join(p.get('bullets', []))}".lower()
                if any(w in p_text for w in combined_jd.split() if len(w) > 4):
                    domain_projects.append(p)

        # STRICT GUARDRAIL: If 0 projects found in domain
        if not domain_projects and not all_internships:
            domain_label = {
                "core": "Core (Robotics/Mechanical/Embedded)",
                "sde": "Software Development (SDE/Backend/Fullstack)",
                "data": "Data Science / Machine Learning / AI",
                "finance": "Quantitative Finance / Trading",
                "consult": "Consulting / Strategy / Product"
            }.get(target_domain, target_domain.upper())
            raise ValueError(
                f"No projects found matching the {domain_label} domain in your Master CV. "
                f"Please add relevant projects for {job.get('title', 'this role')} before applying."
            )

        # Score and rank domain projects
        req_skills = [s.lower() for s in job.get("required_skills", [])]
        scored = []
        for p in domain_projects if domain_projects else all_projects:
            score = 0.0
            p_text = f"{p.get('name', '')} {p.get('description', '')} {' '.join(p.get('bullets', []))}".lower()
            for s in req_skills:
                if s in p_text:
                    score += 5.0
            for tok in job.get("title", "").lower().split():
                if len(tok) > 3 and tok in p_text:
                    score += 3.5
            if p.get("domain") == target_domain:
                score += 4.0
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        
        has_separate_internships = len(all_internships) >= 2
        selected_internships = all_internships[:2] if has_separate_internships else all_internships[:1]
        proj_count = 2 if has_separate_internships else 3
        selected_projects = [p for _, p in scored[:proj_count]]

        return {
            "target_domain": target_domain,
            "has_separate_internships": has_separate_internships,
            "selected_internships": selected_internships,
            "selected_projects": selected_projects,
            "rationale": f"Selected top {len(selected_projects)} domain-aligned projects and {len(selected_internships)} internships matching {job.get('title')}."
        }
