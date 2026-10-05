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
Your job is to analyze a candidate's complete Master CV (which may contain 40-50+ projects across various domains), classify every project, internship, and competition into technical domain tracks, and produce an optimal, JD-tailored 1-page ATS resume selection.

### DOMAIN DEFINITIONS & DISAMBIGUATION (CRITICAL):
- **sde (Software Development)**: Full-Stack Web/App Development, Backend, Frontend, Distributed Systems, Microservices, REST APIs, Database Systems, State Machines, Systems Programming, Compilers.
  * Examples: BlogSphere Full-Stack, Coal India Summer Intern, Movie Explorer Web App, Distributed Cache, REST APIs.
  * DO NOT pick Quantitative Finance or Robotics projects for SDE roles!
- **data (Data Science / AI / ML)**: Machine Learning, Deep Learning, Generative AI, Large Language Models (LLMs), NLP, Computer Vision, Data Science, Data Engineering, Analytics, Forecasting, Recommender Systems.
  * Examples: BharatGen JEE/NEET Platform, Review Helpfulness Prediction, Image Product Attribute Prediction, Land Cover Classification, Traffic Safety Analytics.
  * DO NOT pick Quantitative Finance projects for generic Data roles unless the job is specifically in Quantitative Finance.
- **finance (Quantitative Finance & Trading)**: Quantitative Trading, Algorithmic Trading, Portfolio Optimization (e.g. Bayesian Portfolio Optimizer in C++), Sharpe Ratio, Mean-Variance, Backtesting, Risk Management, Options Pricing, Financial Modeling, Credit Risk Scorecard, HFT.
  * Examples: Bayesian Portfolio Optimizer using C++, Godrej Housing Finance Risk Analytics, Tata Motors Finance Intern, The Big Brand Theory.
- **core (Robotics / Mechanical / Embedded / Hardware)**: Robotics, ROS/ROS2, Embedded Systems, Firmware, Microcontrollers (STM32, Arduino, ESP32), Mechanical Design, CAD, SolidWorks, ANSYS, FEA, Control Systems, Power Electronics, Mechatronics, Automotive/EV, Formula Student.
  * Examples: KE1 Formula Student EV, International Rover Challenge (IRC), STMicroelectronics TIADC Calibration, Digital Voltage Boost Converter.
- **consult / product (Strategy & Product)**: Business Strategy, Market Entry, Operations Research, Product Management, Case Competitions, Supply Chain Optimization.

### STRICT RULES & PRIORITY ORDER:
1. **DOMAIN FILTERING & CLASSIFICATION (TOP PRIORITY)**:
   - Accurately classify every entry into its true technical domain (`sde`, `data`, `finance`, `core`, `consult`).
   - ONLY select items whose primary domain matches the target job domain (`target_domain`)!
   - Select top 4-5 relevant experience items adhering to the priority order:
     **COMPETITIONS/CONFERENCES > INTERNSHIPS > PROJECTS**.

2. **SECTION ORGANIZATION**:
   - **Competitions & Conferences**:
     * If the candidate has participated in relevant competitions/hackathons matching the target domain, place them in `"selected_competitions"`.
     * If 0 domain competitions, set `"selected_competitions": []`.
   - **Internships**:
     * If candidate has >= 2 domain-relevant internships, select top 2 in `"selected_internships"` (set `"has_separate_internships": true`).
     * If candidate has 1 domain-relevant internship, select 1 in `"selected_internships"` (set `"has_separate_internships": false`).
     * If candidate has 0 domain-relevant internships, leave `"selected_internships": []` (set `"has_separate_internships": false`).
   - **Projects**:
     * Select domain-relevant projects in `"selected_projects"`. Total items across Comps + Interns + Projects must be 4-5.

3. **EXACT VERBATIM TEXT STYLE RETENTION (CRITICAL)**:
   - Do NOT rewrite, condense, truncate, or paraphrase bullet points or descriptions!
   - Keep the candidate's exact wording, phrasing, punctuation, and style from the Master CV.
   - Do NOT convert non-bulleted text into bullets, and do NOT remove existing bullets.
   - If an item has a description, keep it in full. If it has bullets, keep all bullets in full.

4. **CLEAN TITLES & NO TECH LINE**:
   - Do NOT emit any `Tech: ...` subtitle lines.
   - Include date range on the header (e.g., `[Nov 2025 - Mar 2026]`).

5. **STATIC SECTIONS PRESERVATION**:
   - Skills, Coursework, Certifications, Positions of Responsibility, and Extra Curriculars are preserved verbatim from the Master CV in their exact text style. Do not invent or replace categories.

7. **DOMAIN VALIDATION GUARDRAIL**:
   - If candidate Master CV contains **0** projects/internships matching the target job domain, return:
     `{"error": "NO_DOMAIN_PROJECTS", "message": "No projects found matching the {domain} domain in your Master CV. Please upload or add relevant projects to apply for this role."}`

8. **OUTPUT FORMAT (JSON ONLY)**:
   ```json
   {
     "target_domain": "sde | data | core | finance | consult",
     "selected_competitions": [
       {
         "name": "Full Title | Organization / Challenge",
         "dates": "[Month Year - Month Year]",
         "description": "",
         "bullets": ["Single-line action bullet 1 (max 115 chars)", "Single-line action bullet 2 (max 115 chars)"]
       }
     ],
     "has_separate_internships": boolean,
     "selected_internships": [
       {
         "name": "Full Title | Organization / Advisor",
         "dates": "[Month Year - Month Year]",
         "description": "",
         "bullets": ["Single-line action bullet 1 (max 115 chars)", "Single-line action bullet 2 (max 115 chars)"]
       }
     ],
     "selected_projects": [
       {
         "name": "Full Title | Type",
         "dates": "[Month Year - Month Year]",
         "description": "",
         "bullets": ["Single-line action bullet 1 (max 115 chars)", "Single-line action bullet 2 (max 115 chars)"]
       }
     ],
     "selected_skills": [
       "Programming Languages: Python | C | C++ | SQL | Node.js",
       "Backend & System Design: FastAPI | REST APIs | Pydantic | PostgreSQL | Docker"
     ],
     "selected_certifications": [
       {
         "name": "Machine Learning Specialization | DeepLearning.AI & Stanford University",
         "bullets": ["Trained neural networks with optimization strategies and deep learning deployment"]
       }
     ],
     "selected_coursework": [
       "Computer Science & ML: Programming and Data Structures (with Lab) | Essentials of Machine Learning"
     ],
     "selected_extracurriculars": [
       "• Secured Gold in Ad Design at the Inter-Hall General Championship (2026), representing Nehru Hall",
       "• Secured 2nd runners-up position in the OpenIIT Data Analytics (2025), delivering analytical insights",
       "• Revived Open IIT Digital Music Making after 2 years, managing end-to-end execution solo at zero cost",
       "• Introduced Open IIT Rap in Sep'24 to promote rap culture, overseeing budgeting, logistics, and outreach",
       "• Competed in Inter-Hall General Championship Data Analytics (2026) as part of the hall team"
     ],
     "rationale": "Brief selection rationale"
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
    def parse_blocks_from_raw_cv(master_cv_text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generic block-level parser using MasterCVParser to extract projects, internships,
        and competitions without hardcoded regexes.
        """
        from app.tools.cv_parser_engine import MasterCVParser
        all_items = MasterCVParser.parse_projects_from_markdown(master_cv_text)
        projects = []
        internships = []
        competitions = []

        for item in all_items:
            i_type = item.get("type", "project")
            if i_type == "competition":
                competitions.append(item)
            elif i_type == "internship":
                internships.append(item)
            else:
                projects.append(item)

        return projects, internships, competitions

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

        # Step 1: Extract block-level projects, internships & competitions
        all_projects, all_internships, all_competitions = GeminiTailorAgent.parse_blocks_from_raw_cv(master_cv_text)
        logger.info(f"📦 [GeminiTailorAgent] Extracted {len(all_projects)} projects, {len(all_internships)} internships, {len(all_competitions)} competitions from Master CV")

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
                    "gemini-2.5-flash",
                    settings.llm_model,
                    "gemini-1.5-flash",
                    "gemini-flash-latest",
                    "gemini-2.0-flash",
                    "gemini-3.5-flash",
                    "gemini-3.8-flash",
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

                    if parsed.get("selected_projects") or parsed.get("selected_internships") or parsed.get("selected_competitions"):
                        return parsed

            except ValueError as ve:
                raise ve
            except Exception as e:
                logger.warning(f"⚠️ [GeminiTailorAgent] Gemini API fallback to AST Engine: {e}")

        # Step 3: High-Precision Deterministic AST Engine Fallback
        def condense_bullet(b_str: str, max_chars: int = 115) -> str:
            clean = b_str.strip().lstrip('•-* ')
            if len(clean) <= max_chars:
                return clean
            # Trim trailing clauses / secondary phrases if overly long
            parts = re.split(r'[,;]\s*(?:achieving|reducing|resulting|delivering|thus|with|across|supporting)\b', clean, flags=re.I)
            if len(parts) > 1 and len(parts[0]) >= 40:
                shortened = parts[0].strip()
                if len(shortened) <= max_chars:
                    return shortened
            # Fallback concise word truncation
            words = clean.split()
            cand = ""
            for w in words:
                if len(cand) + len(w) + 1 <= max_chars:
                    cand = (cand + " " + w).strip()
                else:
                    break
            return cand or clean[:max_chars]

        req_skills = [s.lower() for s in job.get("required_skills", [])]
        combined_jd = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('required_skills', []))}".lower()

        def score_item(item: Dict[str, Any]) -> float:
            score = 0.0
            i_type = item.get("type", "project").lower()
            name_lower = item.get("name", "").lower()
            p_text = f"{item.get('name', '')} {item.get('description', '')} {' '.join(item.get('bullets', []))}".lower()
            
            # 1. Domain Relevance (Highest Weight)
            if item.get("domain") == target_domain:
                score += 25.0
            else:
                for s in req_skills:
                    if s in p_text:
                        score += 6.0
                for tok in job.get("title", "").lower().split():
                    if len(tok) > 3 and tok in p_text:
                        score += 4.0

            # 2. Priority Order: Competition > Internship > Project
            if any(k in name_lower for k in ["challenge", "competition", "hackathon", "finalist", "contest", "conference"]) or i_type == "competition":
                score += 5.0
            elif i_type == "internship" or "intern" in name_lower or "advisor" in name_lower:
                score += 3.0
            else:
                score += 1.0

            for s in req_skills:
                if s in p_text:
                    score += 3.0

            return score

        all_items = all_competitions + all_internships + all_projects
        domain_items = [it for it in all_items if it.get("domain", "").lower() == target_domain]
        if not domain_items:
            for it in all_items:
                it_text = f"{it.get('name', '')} {it.get('description', '')} {' '.join(it.get('bullets', []))}".lower()
                if any(w in it_text for w in combined_jd.split() if len(w) > 4):
                    domain_items.append(it)

        if not domain_items:
            domain_items = all_items

        scored_comps = [(score_item(it), it) for it in all_competitions]
        scored_comps.sort(key=lambda x: x[0], reverse=True)

        scored_internships = [(score_item(it), it) for it in all_internships]
        scored_internships.sort(key=lambda x: x[0], reverse=True)

        scored_projects = [(score_item(it), it) for it in all_projects]
        scored_projects.sort(key=lambda x: x[0], reverse=True)

        def prepare_item(it_dict):
            return {
                "name": it_dict.get("name", ""),
                "dates": it_dict.get("dates", ""),
                "description": it_dict.get("description", ""),
                "bullets": list(it_dict.get("bullets", []))
            }

        # Filter domain competitions, internships, and projects
        domain_comps = [it for it in scored_comps if it[1].get("domain") == target_domain or it[0] >= 20.0]
        domain_interns = [it for it in scored_internships if it[1].get("domain") == target_domain or it[0] >= 20.0]
        if not domain_interns and scored_internships:
            domain_interns = scored_internships[:1]

        domain_projs = [it for it in scored_projects if it[1].get("domain") == target_domain or it[0] >= 20.0]
        if not domain_projs and scored_projects:
            domain_projs = scored_projects

        selected_comps = [prepare_item(it[1]) for it in domain_comps[:1]] if domain_comps else []
        has_separate_internships = len(domain_interns) >= 2
        selected_internships = [prepare_item(it[1]) for it in domain_interns[:2]] if has_separate_internships else ([prepare_item(it[1]) for it in domain_interns[:1]] if domain_interns else [])

        total_used = len(selected_comps) + len(selected_internships)
        needed_projects = max(1, 5 - total_used)
        selected_projects = [prepare_item(it[1]) for it in domain_projs[:needed_projects]]
        all_available_projects = [prepare_item(it[1]) for it in scored_projects]

        return {
            "target_domain": target_domain,
            "selected_competitions": selected_comps,
            "has_separate_internships": has_separate_internships,
            "selected_internships": selected_internships,
            "selected_projects": selected_projects,
            "all_available_projects": all_available_projects,
            "rationale": f"Selected top domain-aligned experience in priority COMPS > INTERN > PROJECT."
        }
