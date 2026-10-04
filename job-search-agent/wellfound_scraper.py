import logging
import requests
import json
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class WellfoundScraper:
    """
    Lightweight scraper for Wellfound (formerly AngelList Talent) public job listings.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def search_jobs(self, search_term: str, location: str = "Remote", results_wanted: int = 5) -> List[Dict[str, Any]]:
        """
        Searches Wellfound jobs matching the search_term.
        """
        logger.info(f"Searching Wellfound for '{search_term}'...")
        jobs = []
        try:
            # Wellfound role slug matching
            role_slug = re.sub(r'[^a-z0-9]+', '-', search_term.lower()).strip('-')
            loc_slug = "india" if "india" in location.lower() else "remote"
            url = f"https://wellfound.com/role/{role_slug}"
            
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extract job cards or JSON data embedded in page
                job_cards = soup.find_all("div", class_=re.compile(r"styles_jobListing|styles_resultCard|component_styles", re.I))
                for card in job_cards[:results_wanted]:
                    title_elem = card.find(["h2", "h3", "h4", "a"])
                    company_elem = card.find("span", class_=re.compile(r"company|name", re.I))
                    link_elem = card.find("a", href=re.compile(r"/jobs/|/company/"))
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Wellfound Startup"
                        link = f"https://wellfound.com{link_elem['href']}" if link_elem and link_elem.get('href', '').startswith('/') else (link_elem['href'] if link_elem else "https://wellfound.com/jobs")
                        
                        jobs.append({
                            "site": "wellfound",
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_url": link,
                            "description": f"{title} at {company}. Wellfound startup opportunity in {location}.",
                            "min_amount": None,
                            "max_amount": None,
                            "currency": "USD" if "remote" in location.lower() else "INR"
                        })
        except Exception as e:
            logger.debug(f"Wellfound query notice: {e}")

        return jobs
