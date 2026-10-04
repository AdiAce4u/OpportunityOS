import sqlite3
import os
import json
from datetime import datetime

class JobDatabase:
    def __init__(self, db_path="jobs_database.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    site TEXT,
                    category TEXT,
                    search_term TEXT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    job_url TEXT,
                    job_type TEXT,
                    date_posted TEXT,
                    interval TEXT,
                    min_amount REAL,
                    max_amount REAL,
                    currency TEXT,
                    is_remote INTEGER,
                    description TEXT,
                    match_score REAL DEFAULT 0.0,
                    best_matching_project TEXT,
                    matched_keywords TEXT,
                    normalized_salary REAL DEFAULT 0.0,
                    display_salary TEXT DEFAULT 'Not Disclosed',
                    first_seen_at TEXT
                )
            """)
            conn.commit()

            # Ensure newly added columns exist in older database files
            existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(jobs)").fetchall()]
            new_cols = {
                "match_score": "REAL DEFAULT 0.0",
                "best_matching_project": "TEXT",
                "matched_keywords": "TEXT",
                "normalized_salary": "REAL DEFAULT 0.0",
                "display_salary": "TEXT DEFAULT 'Not Disclosed'"
            }
            for col_name, col_type in new_cols.items():
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
            conn.commit()

    @staticmethod
    def _clean_val(val, default=""):
        import math
        if val is None:
            return default
        if isinstance(val, float) and math.isnan(val):
            return default
        return val

    def save_job(self, job_dict, category, search_term, match_info=None, comp_info=None) -> bool:
        """
        Saves a job to the database with similarity match and compensation data.
        Returns True if a new job was inserted, False if already present.
        """
        job_id = str(job_dict.get("id") or job_dict.get("job_url"))
        if not job_id:
            return False

        match_info = match_info or {}
        comp_info = comp_info or {}

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
            if cursor.fetchone():
                # Update match scores / salary if needed
                cursor.execute("""
                    UPDATE jobs SET 
                        match_score = ?,
                        best_matching_project = ?,
                        matched_keywords = ?,
                        normalized_salary = ?,
                        display_salary = ?
                    WHERE id = ?
                """, (
                    self._clean_val(match_info.get("match_score"), 0.0),
                    str(self._clean_val(match_info.get("best_project"), "N/A")),
                    json.dumps(match_info.get("matched_keywords", [])),
                    self._clean_val(comp_info.get("normalized_yearly_salary"), 0.0),
                    str(self._clean_val(comp_info.get("display_salary"), "Not Disclosed")),
                    job_id
                ))
                conn.commit()
                return False

            cursor.execute("""
                INSERT INTO jobs (
                    id, site, category, search_term, title, company, location,
                    job_url, job_type, date_posted, interval, min_amount,
                    max_amount, currency, is_remote, description,
                    match_score, best_matching_project, matched_keywords,
                    normalized_salary, display_salary, first_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                str(self._clean_val(job_dict.get("site"), "linkedin")),
                category,
                search_term,
                str(self._clean_val(job_dict.get("title"), "")),
                str(self._clean_val(job_dict.get("company"), "")),
                str(self._clean_val(job_dict.get("location"), "")),
                str(self._clean_val(job_dict.get("job_url"), "")),
                str(self._clean_val(job_dict.get("job_type"), "")),
                str(self._clean_val(job_dict.get("date_posted"), "")),
                str(self._clean_val(job_dict.get("interval"), "")),
                self._clean_val(job_dict.get("min_amount"), None),
                self._clean_val(job_dict.get("max_amount"), None),
                str(self._clean_val(job_dict.get("currency"), "")),
                1 if job_dict.get("is_remote") else 0,
                str(self._clean_val(job_dict.get("description"), "")),
                self._clean_val(match_info.get("match_score"), 0.0),
                str(self._clean_val(match_info.get("best_project"), "N/A")),
                json.dumps(match_info.get("matched_keywords", [])),
                self._clean_val(comp_info.get("normalized_yearly_salary"), 0.0),
                str(self._clean_val(comp_info.get("display_salary"), "Not Disclosed")),
                datetime.now().isoformat()
            ))
            conn.commit()
            return True

    def get_all_jobs(self, category=None, sort_by="match"):
        """
        Retrieves jobs with sorting:
          - 'match': Order by match_score DESC
          - 'salary': Order by normalized_salary DESC
          - 'recent': Order by first_seen_at DESC
        """
        order_clause = "match_score DESC, first_seen_at DESC"
        if sort_by == "salary":
            order_clause = "normalized_salary DESC, match_score DESC"
        elif sort_by == "recent":
            order_clause = "first_seen_at DESC"

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if category and category != "all":
                cursor.execute(f"SELECT * FROM jobs WHERE category = ? ORDER BY {order_clause}", (category,))
            else:
                cursor.execute(f"SELECT * FROM jobs ORDER BY {order_clause}")
            rows = cursor.fetchall()
            
            jobs = []
            for row in rows:
                d = dict(row)
                try:
                    d["matched_keywords"] = json.loads(d.get("matched_keywords") or "[]")
                except:
                    d["matched_keywords"] = []
                jobs.append(d)
            return jobs
