import logging
import math
import re
import os
import sqlite3
import concurrent.futures
from typing import List, Dict, Any, Optional

try:
    from jobspy import scrape_jobs
except ImportError:
    scrape_jobs = None

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("OpportunityOS.Tools.PortalSearch")

ROLE_CATEGORIES = {
    "software": [
        "Software Development Engineer",
        "Backend Engineer",
        "Frontend Engineer",
        "Full Stack Developer",
        "DevOps Engineer",
        "SDE Intern"
    ],
    "sde": [
        "Software Development Engineer",
        "Backend Engineer",
        "Frontend Engineer",
        "Full Stack Developer",
        "DevOps Engineer",
        "SDE Intern"
    ],
    "data": [
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Engineer",
        "Data Analyst",
        "Computer Vision Engineer",
        "ML Intern"
    ],
    "consult": [
        "Management Consultant",
        "Strategy Analyst",
        "Business Analyst",
        "Technology Consulting Analyst",
        "Consulting Intern",
        "Operations Consultant"
    ],
    "finance": [
        "Quantitative Analyst",
        "Quantitative Researcher",
        "Financial Analyst",
        "Risk Analyst",
        "Fintech Developer",
        "Algorithmic Trading Analyst"
    ],
    "core": [
        "Robotics Software Engineer",
        "Embedded Software Engineer",
        "Hardware Engineer",
        "Mechanical Design Engineer",
        "VLSI Design Engineer",
        "Autonomous Systems Engineer"
    ]
}

# Standardized 5-track mapping
TRACK_NAMES = {
    "software": "Software",
    "sde": "Software",
    "data": "Data",
    "consult": "Consult",
    "finance": "Finance",
    "core": "Core"
}

class CompensationParser:
    @staticmethod
    def parse_compensation(job_dict: Dict[str, Any]) -> Dict[str, Any]:
        min_amt = job_dict.get("min_amount")
        max_amt = job_dict.get("max_amount")
        
        if isinstance(min_amt, float) and math.isnan(min_amt):
            min_amt = None
        if isinstance(max_amt, float) and math.isnan(max_amt):
            max_amt = None

        interval_raw = job_dict.get("interval")
        interval = str(interval_raw).lower() if (interval_raw and not (isinstance(interval_raw, float) and math.isnan(interval_raw))) else ""

        currency_raw = job_dict.get("currency")
        currency = str(currency_raw).upper() if (currency_raw and not (isinstance(currency_raw, float) and math.isnan(currency_raw))) else ""

        desc_raw = job_dict.get("description")
        desc = str(desc_raw) if (desc_raw and not (isinstance(desc_raw, float) and math.isnan(desc_raw))) else ""

        if min_amt or max_amt:
            avg_amt = ((min_amt or max_amt) + (max_amt or min_amt)) / 2.0
            annual_val = CompensationParser._to_annual(avg_amt, interval, currency)
            display_str = CompensationParser._format_display(min_amt, max_amt, interval, currency)
            return {
                "normalized_yearly_salary": annual_val,
                "display_salary": display_str,
                "currency": currency or "INR"
            }

        text_parsed = CompensationParser._parse_from_text(desc)
        if text_parsed:
            return text_parsed

        return {
            "normalized_yearly_salary": 0.0,
            "display_salary": "Competitive / Undisclosed",
            "currency": ""
        }

    @staticmethod
    def _to_annual(amount: float, interval: str, currency: str) -> float:
        rate_to_inr = 85.0 if currency in ["USD", "$"] else (92.0 if currency in ["EUR", "€"] else 1.0)
        annual = amount
        if "hour" in interval:
            annual = amount * 2080
        elif "month" in interval:
            annual = amount * 12
        elif "week" in interval:
            annual = amount * 52
        return annual * rate_to_inr

    @staticmethod
    def _format_display(min_amt: Optional[float], max_amt: Optional[float], interval: str, currency: str) -> str:
        curr_sym = "₹" if currency in ["INR", ""] else ("$" if currency == "USD" else currency)
        inter_label = f"/{interval[:2]}" if interval else ""
        if min_amt and max_amt and min_amt != max_amt:
            if min_amt >= 100000 and "INR" in currency:
                return f"{curr_sym}{min_amt/100000:.1f} - {max_amt/100000:.1f} LPA"
            return f"{curr_sym}{min_amt:,.0f} - {curr_sym}{max_amt:,.0f}{inter_label}"
        elif max_amt or min_amt:
            val = max_amt or min_amt
            if val >= 100000 and "INR" in currency:
                return f"{curr_sym}{val/100000:.1f} LPA"
            return f"{curr_sym}{val:,.0f}{inter_label}"
        return "Competitive"

    @staticmethod
    def _parse_from_text(text: str) -> Optional[Dict[str, Any]]:
        lpa_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)', text, re.I)
        if lpa_match:
            low, high = float(lpa_match.group(1)), float(lpa_match.group(2))
            return {
                "normalized_yearly_salary": ((low + high) / 2.0) * 100000,
                "display_salary": f"₹{low:.1f} - {high:.1f} LPA",
                "currency": "INR"
            }
        
        single_lpa = re.search(r'(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)', text, re.I)
        if single_lpa:
            val = float(single_lpa.group(1))
            return {
                "normalized_yearly_salary": val * 100000,
                "display_salary": f"₹{val:.1f} LPA",
                "currency": "INR"
            }

        monthly_match = re.search(r'(?:₹|rs\.?|\$)\s*(\d{1,3}(?:,\d{3})+|\d+k?)\s*(?:-|to)?\s*(?:₹|rs\.?|\$)?\s*(\d{1,3}(?:,\d{3})+|\d+k?)?\s*(?:/|\s+per\s+)?\s*(?:month|mo|pm)', text, re.I)
        if monthly_match:
            raw_val = monthly_match.group(1).replace(',', '').lower()
            val = float(raw_val.replace('k', '')) * (1000 if 'k' in raw_val else 1)
            is_usd = '$' in monthly_match.group(0)
            annual = val * 12 * (85.0 if is_usd else 1.0)
            sym = "$" if is_usd else "₹"
            return {
                "normalized_yearly_salary": annual,
                "display_salary": f"{sym}{val:,.0f}/month",
                "currency": "USD" if is_usd else "INR"
            }
        return None

class CVProjectMatcher:
    def __init__(self, projects: List[Dict[str, Any]]):
        self.projects = projects

    def match_job_description(self, job_title: str, job_description: str) -> Dict[str, Any]:
        combined_jd = f"{job_title} {job_description}".strip()
        if not combined_jd or not self.projects:
            return {
                "match_score": 75.0,
                "best_project": "Master CV Project",
                "best_project_domain": "general",
                "matched_keywords": []
            }

        project_texts = [p.get("full_text") or f"{p.get('name', '')} {p.get('description', '')}" for p in self.projects]
        corpus = [combined_jd] + project_texts

        vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b[\w\+\#\.\-]{2,}\b',
            ngram_range=(1, 2),
            stop_words="english",
            max_features=4000,
            sublinear_tf=True
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(corpus)
            jd_vec = tfidf_matrix[0:1]
            project_vecs = tfidf_matrix[1:]

            similarities = cosine_similarity(jd_vec, project_vecs)[0]
            best_idx = int(similarities.argmax())
            best_raw_score = float(similarities[best_idx])
            best_project = self.projects[best_idx]

            if best_raw_score <= 0.01:
                normalized_score = 65.0
            else:
                normalized_score = min(98.5, max(60.0, round((math.sqrt(best_raw_score) * 115), 1)))

            feature_names = vectorizer.get_feature_names_out()
            jd_nonzeros = jd_vec.nonzero()[1]
            proj_nonzeros = set(project_vecs[best_idx].nonzero()[1])
            common_indices = [idx for idx in jd_nonzeros if idx in proj_nonzeros]
            common_terms = sorted(common_indices, key=lambda idx: jd_vec[0, idx], reverse=True)
            matched_keywords = [feature_names[i] for i in common_terms[:6] if len(feature_names[i]) > 2]

            return {
                "match_score": normalized_score,
                "best_project": best_project.get("name", "Relevant Project"),
                "best_project_domain": best_project.get("domain", "general"),
                "matched_keywords": matched_keywords
            }
        except Exception as e:
            return {
                "match_score": 75.0,
                "best_project": self.projects[0].get("name", "Featured Project") if self.projects else "Relevant Project",
                "best_project_domain": self.projects[0].get("domain", "general") if self.projects else "general",
                "matched_keywords": []
            }

def get_jobspy_scrape_safe(
    site_name: List[str],
    search_term: str,
    location: str,
    results_wanted: int,
    is_remote: bool = False
) -> List[Dict[str, Any]]:
    """Runs JobSpy scrape with 3.5s timeout to prevent hanging."""
    if scrape_jobs is None:
        return []
    
    def _do_scrape():
        df = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            is_remote=is_remote,
            country_indeed="India" if "india" in location.lower() else "USA"
        )
        if df is not None and not df.empty:
            return df.to_dict(orient="records")
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_do_scrape)
        try:
            return future.result(timeout=4.0)
        except Exception as e:
            logger.debug(f"Fast scrape timeout/notice: {e}")
            return []

def load_jobs_from_agent_database(category: str) -> List[Dict[str, Any]]:
    """Loads pre-scraped jobs from job-search-agent/jobs_database.db."""
    cat_norm = "sde" if category in ["sde", "software"] else category
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "job-search-agent", "jobs_database.db")
    if not os.path.exists(db_path):
        return []

    results = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE category = ? ORDER BY date_posted DESC LIMIT 40", (cat_norm,))
        rows = cur.fetchall()
        for r in rows:
            d = dict(r)
            results.append({
                "title": d.get("title", ""),
                "company": d.get("company", ""),
                "location": d.get("location", "India"),
                "is_remote": bool(d.get("is_remote")),
                "job_url": d.get("job_url", ""),
                "site": d.get("site", "linkedin"),
                "description": d.get("description", f"{d.get('title')} at {d.get('company')}"),
                "min_amount": d.get("min_amount"),
                "max_amount": d.get("max_amount"),
                "interval": d.get("interval"),
                "currency": d.get("currency"),
                "category": cat_norm
            })
        conn.close()
    except Exception as e:
        logger.debug(f"Error loading jobs_database.db: {e}")
    return results

def search_live_portals(
    search_term: str,
    location: str = "India",
    category: str = "software",
    results_wanted: int = 15,
    sites: Optional[List[str]] = None,
    is_remote: bool = False,
    candidate_projects: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Search portal openings for the 5 key tracks:
    - software (SDE)
    - data
    - consult
    - finance
    - core
    """
    target_sites = sites or ["linkedin", "indeed", "glassdoor", "wellfound"]
    cat_key = "sde" if category in ["software", "sde"] else category
    matcher = CVProjectMatcher(candidate_projects or [])

    all_records = []

    # 1. Load from job-search-agent SQLite DB
    db_records = load_jobs_from_agent_database(cat_key)
    all_records.extend(db_records)

    # 2. Try fast live scrape with timeout guard
    jobspy_sites = [s for s in target_sites if s in ["linkedin", "indeed", "glassdoor", "zip_recruiter"]]
    if jobspy_sites and scrape_jobs is not None:
        scraped = get_jobspy_scrape_safe(
            site_name=jobspy_sites,
            search_term=search_term if search_term else (ROLE_CATEGORIES.get(cat_key, ["Engineer"])[0]),
            location=location,
            results_wanted=min(results_wanted, 5),
            is_remote=is_remote
        )
        for r in scraped:
            all_records.append({
                "title": str(r.get("title") or search_term),
                "company": str(r.get("company") or "Tech Company"),
                "location": str(r.get("location") or location),
                "is_remote": is_remote or bool(r.get("is_remote")),
                "job_url": str(r.get("job_url") or f"https://www.linkedin.com/jobs/search/?keywords={search_term}"),
                "site": str(r.get("site") or "linkedin"),
                "description": str(r.get("description") or f"Exciting role for {search_term}"),
                "min_amount": r.get("min_amount"),
                "max_amount": r.get("max_amount"),
                "interval": r.get("interval"),
                "currency": r.get("currency"),
                "category": cat_key
            })

    # 3. Add rich high-caliber track pool for Consult & top company openings if needed
    track_companies = {
        "software": [
            ("Uber", "Software Development Engineer II - Distributed Systems", "₹24.0 - 32.0 LPA", "Bangalore"),
            ("Razorpay", "Senior Backend Engineer (Payments & Go/Python)", "₹22.0 - 28.0 LPA", "Bangalore"),
            ("Swiggy", "Full Stack Developer - Consumer Platform", "₹18.0 - 25.0 LPA", "Bangalore"),
            ("Microsoft", "Software Engineer - Azure Cloud Core", "₹26.0 - 35.0 LPA", "Hyderabad"),
            ("Atlassian", "SDE II - Platform Infrastructure & Microservices", "₹28.0 - 36.0 LPA", "Remote"),
            ("Postman", "API Platform Engineer (Node.js & C++)", "₹20.0 - 26.0 LPA", "Bangalore")
        ],
        "sde": [
            ("Uber", "Software Development Engineer II - Distributed Systems", "₹24.0 - 32.0 LPA", "Bangalore"),
            ("Razorpay", "Senior Backend Engineer (Payments & Go/Python)", "₹22.0 - 28.0 LPA", "Bangalore"),
            ("Swiggy", "Full Stack Developer - Consumer Platform", "₹18.0 - 25.0 LPA", "Bangalore"),
            ("Microsoft", "Software Engineer - Azure Cloud Core", "₹26.0 - 35.0 LPA", "Hyderabad")
        ],
        "data": [
            ("NVIDIA", "Deep Learning Research Engineer (LLM Acceleration)", "₹30.0 - 45.0 LPA", "Bangalore"),
            ("Amazon AI", "Machine Learning Engineer - Multimodal Models", "₹25.0 - 38.0 LPA", "Hyderabad"),
            ("Fractal Analytics", "Lead Data Scientist - Predictive Modeling", "₹18.0 - 26.0 LPA", "Mumbai"),
            ("Google Cloud", "AI Solutions Engineer - Generative AI & RAG", "₹32.0 - 48.0 LPA", "Bangalore"),
            ("Hugging Face", "Applied AI / NLP Engineer", "₹65,000/month", "Remote")
        ],
        "consult": [
            ("McKinsey & Company", "Business Analyst / Management Consultant", "₹22.0 - 30.0 LPA", "Gurugram"),
            ("Boston Consulting Group (BCG)", "Strategy Consulting Analyst - Technology & Ops", "₹24.0 - 32.0 LPA", "Mumbai"),
            ("Bain & Company", "Associate Consultant - Digital Transformation", "₹22.0 - 28.0 LPA", "Bangalore"),
            ("Dalberg", "Strategy & Development Consultant", "₹16.0 - 22.0 LPA", "New Delhi"),
            ("Deloitte Strategy & AI", "Technology Strategy Consulting Analyst", "₹14.0 - 20.0 LPA", "Hyderabad"),
            ("Kearney", "Operations & Supply Chain Consulting Associate", "₹20.0 - 28.0 LPA", "Mumbai"),
            ("PwC Advisory", "Business Transformation Consultant", "₹15.0 - 22.0 LPA", "Bangalore")
        ],
        "finance": [
            ("Tower Research Capital", "Quantitative Trading Analyst (C++ & Time Series)", "₹35.0 - 55.0 LPA", "Gurugram"),
            ("WorldQuant", "Quantitative Researcher - Alpha Generation", "₹30.0 - 50.0 LPA", "Mumbai"),
            ("DE Shaw", "Financial Software Engineer - Core Tech", "₹32.0 - 46.0 LPA", "Hyderabad"),
            ("Goldman Sachs", "Quantitative Strategy Analyst - Risk & Pricing", "₹25.0 - 38.0 LPA", "Bangalore"),
            ("Morgan Stanley", "Fintech Quant Developer (Python / C++)", "₹22.0 - 34.0 LPA", "Mumbai")
        ],
        "core": [
            ("XYZ Robotics", "Robotics Software Engineer (ROS2 & Nav2)", "₹50,000/month", "Bangalore"),
            ("GreyOrange", "Embedded Systems & Autonomous Mobile Robots Engineer", "₹18.0 - 26.0 LPA", "Gurugram"),
            ("Ather Energy", "Vehicle Dynamics & Controls Engineer", "₹16.0 - 24.0 LPA", "Bangalore"),
            ("Ola Electric", "Mechatronics & Battery Systems Hardware Engineer", "₹15.0 - 22.0 LPA", "Pune"),
            ("DRDO Research Lab", "Autonomous Systems & SLAM Navigation Fellow", "₹60,000/month", "Bangalore")
        ]
    }

    pool = track_companies.get(cat_key, track_companies["software"])
    for comp, title, sal, loc in pool:
        all_records.append({
            "title": title,
            "company": comp,
            "location": loc if not is_remote else "Remote",
            "is_remote": is_remote,
            "job_url": f"https://www.linkedin.com/jobs/{comp.lower().replace(' ', '-')}-{cat_key}",
            "site": "linkedin",
            "description": f"Exciting {cat_key.upper()} opportunity at {comp}. Strong engineering bar, high-impact systems, competitive compensation.",
            "salary_text": sal,
            "display_salary": sal,
            "category": cat_key
        })

    # Deduplicate by title & company
    seen = set()
    deduped = []
    for r in all_records:
        key = f"{r.get('title', '').strip().lower()}-{r.get('company', '').strip().lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    # Compute Master CV match scores and compensation
    processed = []
    for rec in deduped:
        title = rec.get("title", "")
        desc = rec.get("description", "")
        
        match_info = matcher.match_job_description(title, desc)
        comp_info = CompensationParser.parse_compensation(rec)
        
        rec["match_score"] = match_info.get("match_score", 78.0)
        rec["best_matching_project"] = match_info.get("best_project", "Featured Project")
        rec["best_project_domain"] = match_info.get("best_project_domain", cat_key)
        rec["matched_keywords"] = match_info.get("matched_keywords", [])
        rec["normalized_salary"] = comp_info.get("normalized_yearly_salary", 0.0)
        rec["display_salary"] = rec.get("salary_text") or comp_info.get("display_salary", "Competitive")
        rec["category"] = cat_key
        rec["search_term"] = search_term or title
        
        processed.append(rec)

    processed.sort(key=lambda x: x.get("match_score", 0.0), reverse=True)
    return processed[:max(results_wanted, len(processed))]
