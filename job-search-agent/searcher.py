import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from jobspy import scrape_jobs
from db import JobDatabase
from cv_matcher import CVProjectMatcher
from compensation_parser import CompensationParser
from wellfound_scraper import WellfoundScraper
from config import ROLE_CATEGORIES, DEFAULT_SETTINGS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class JobSearcher:
    def __init__(self, db_path: Optional[str] = None, cv_path: Optional[str] = None):
        self.db = JobDatabase(db_path or DEFAULT_SETTINGS["db_path"])
        self.cv_path = cv_path or DEFAULT_SETTINGS["default_cv_path"]
        self.matcher = CVProjectMatcher(self.cv_path)
        self.wellfound_scraper = WellfoundScraper()
        self.rescore_existing_db()

    def rescore_existing_db(self):
        """Re-scores all existing jobs in the database against the current Master CV."""
        existing_jobs = self.db.get_all_jobs(sort_by="recent")
        if not existing_jobs:
            return
        
        for job in existing_jobs:
            title = str(job.get("title") or "")
            desc = str(job.get("description") or "")
            match_info = self.matcher.match_job_description(title, desc)
            comp_info = CompensationParser.parse_compensation(job)
            self.db.save_job(
                job,
                category=job.get("category", "custom"),
                search_term=job.get("search_term", ""),
                match_info=match_info,
                comp_info=comp_info
            )

    def search(
        self,
        search_term: str,
        location: str = "India",
        category: str = "custom",
        results_wanted: int = 5,
        hours_old: int = 72,
        sites: Optional[List[str]] = None,
        is_remote: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Executes real-time multi-platform job search (LinkedIn, Indeed, Glassdoor, Wellfound).
        Matches job descriptions against Master CV projects and parses stipend/salary.
        """
        target_sites = sites or DEFAULT_SETTINGS["sites"]
        logger.info(f"Searching portals {target_sites} for '{search_term}' in '{location}' (Last {hours_old}h)...")

        all_records = []

        # 1. JobSpy Platforms (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
        jobspy_sites = [s for s in target_sites if s in ["linkedin", "indeed", "glassdoor", "zip_recruiter"]]
        if jobspy_sites:
            try:
                jobs_df = scrape_jobs(
                    site_name=jobspy_sites,
                    search_term=search_term,
                    location=location,
                    results_wanted=results_wanted,
                    hours_old=hours_old,
                    is_remote=is_remote,
                    country_indeed="India" if "india" in location.lower() else "USA"
                )
                if jobs_df is not None and not jobs_df.empty:
                    all_records.extend(jobs_df.to_dict(orient="records"))
            except Exception as e:
                logger.error(f"Error scraping {jobspy_sites} for '{search_term}': {e}")

        # 2. Wellfound Platform (if requested)
        if "wellfound" in target_sites or "all" in target_sites:
            try:
                wellfound_jobs = self.wellfound_scraper.search_jobs(
                    search_term=search_term,
                    location=location,
                    results_wanted=results_wanted
                )
                all_records.extend(wellfound_jobs)
            except Exception as e:
                logger.error(f"Error searching Wellfound: {e}")

        if not all_records:
            logger.warning(f"No results found across platforms for '{search_term}' in '{location}'.")
            return []

        # 3. Match against Master CV projects & Parse Compensation
        new_count = 0
        for rec in all_records:
            title = str(rec.get("title") or "")
            desc = str(rec.get("description") or "")
            
            # Compute Master CV project similarity
            match_info = self.matcher.match_job_description(title, desc)
            
            # Extract and normalize stipend / salary
            comp_info = CompensationParser.parse_compensation(rec)
            
            # Enrich record
            rec["match_score"] = match_info.get("match_score", 0.0)
            rec["best_matching_project"] = match_info.get("best_project", "N/A")
            rec["matched_keywords"] = match_info.get("matched_keywords", [])
            rec["normalized_salary"] = comp_info.get("normalized_yearly_salary", 0.0)
            rec["display_salary"] = comp_info.get("display_salary", "Not Disclosed")

            is_new = self.db.save_job(rec, category=category, search_term=search_term, match_info=match_info, comp_info=comp_info)
            if is_new:
                new_count += 1

        logger.info(f"Processed {len(all_records)} jobs ({new_count} newly added to DB).")
        return all_records

    def search_category(
        self,
        category: str,
        location: str = "India",
        results_per_role: int = 5,
        hours_old: int = 72,
        sites: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Searches all roles defined under a category (e.g., 'sde', 'data', 'core', 'finance').
        """
        roles = ROLE_CATEGORIES.get(category.lower(), [category])
        results_by_role = {}
        total_found = 0

        logger.info(f"[*] Starting category search for [{category.upper()}] ({len(roles)} roles)")
        for role in roles:
            found = self.search(
                search_term=role,
                location=location,
                category=category.lower(),
                results_wanted=results_per_role,
                hours_old=hours_old,
                sites=sites
            )
            results_by_role[role] = found
            total_found += len(found)

        return {
            "category": category,
            "total_jobs": total_found,
            "details": results_by_role
        }

    def search_all_categories(
        self,
        location: str = "India",
        results_per_role: int = 5,
        hours_old: int = 72,
        sites: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Runs batch search for all pre-defined categories (SDE, Data, Core, Finance).
        """
        summary = {}
        for cat in ROLE_CATEGORIES.keys():
            summary[cat] = self.search_category(
                category=cat,
                location=location,
                results_per_role=results_per_role,
                hours_old=hours_old,
                sites=sites
            )
        return summary
