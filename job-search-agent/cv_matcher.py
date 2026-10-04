import re
import os
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CVProjectMatcher:
    def __init__(self, cv_path: str = "master_cv.md"):
        self.cv_path = cv_path
        self.projects = self._load_and_parse_cv(cv_path)
        self.full_cv_text = self._load_full_text(cv_path)

    def _load_full_text(self, cv_path: str) -> str:
        if not os.path.exists(cv_path):
            return ""
        with open(cv_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _load_and_parse_cv(self, cv_path: str) -> List[Dict[str, str]]:
        """
        Parses Master CV into distinct project blocks.
        Splits by markdown headers (### or ##) or bullet clusters.
        """
        if not os.path.exists(cv_path):
            return []

        with open(cv_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Split on markdown project headers (### or ##)
        sections = re.split(r'\n(?=#{2,3}\s+)', content)
        projects = []

        skip_keywords = ["personal information", "contact", "education", "skills", "projects & technical experience", "experience", "projects"]

        for sec in sections:
            lines = sec.strip().split('\n')
            if not lines:
                continue
            header = lines[0].lstrip('#').strip()
            # Ignore meta section headers
            if any(header.lower() == skip or header.lower().startswith(skip) for skip in skip_keywords):
                continue
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
            if len(body) > 30:  # Valid project or experience section
                inferred_domain = self._infer_domain(f"{header} {body}")
                projects.append({
                    "title": header,
                    "content": f"{header}\n{body}",
                    "inferred_domain": inferred_domain
                })

        return projects

    def _infer_domain(self, text: str) -> str:
        text_lower = text.lower()
        scores = {
            "sde": len(re.findall(r'\b(backend|frontend|fullstack|microservices|api|grpc|rest|react|spring|django|docker|kubernetes|sql|postgres|redis|ci/cd)\b', text_lower)),
            "data": len(re.findall(r'\b(data|spark|kafka|etl|pandas|numpy|machine learning|deep learning|nlp|rag|llm|pytorch|tensorflow|analytics)\b', text_lower)),
            "core": len(re.findall(r'\b(embedded|firmware|rtos|microcontroller|stm32|ros|slam|robotics|vlsi|verilog|fpga|hardware|c\+\+|cad)\b', text_lower)),
            "finance": len(re.findall(r'\b(finance|trading|quant|order book|arbitrage|risk|portfolio|derivatives|market|equity|fixed income|banking)\b', text_lower))
        }
        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] > 0 else "general"

    def match_job_description(self, job_title: str, job_description: str) -> Dict[str, Any]:
        """
        Computes the cosine similarity between the Job Description and candidate projects.
        Returns:
          - match_score: float (0.0 to 100.0)
          - best_project_title: str
          - matched_keywords: List[str]
          - inferred_domain: str
        """
        combined_jd = f"{job_title} {job_description}".strip()
        if not combined_jd or not self.projects:
            return {
                "match_score": 0.0,
                "best_project": "N/A",
                "matched_keywords": [],
                "inferred_domain": "general"
            }

        # Compute TF-IDF similarity against each project in master CV
        project_texts = [p["content"] for p in self.projects]
        corpus = [combined_jd] + project_texts

        vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b[\w\+\#\.\-]{2,}\b',
            ngram_range=(1, 2),
            stop_words="english",
            max_features=5000,
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

            # Normalize to 0-100% scale (0.05 raw -> 30%, 0.20 raw -> 75%, 0.35+ -> 95%)
            if best_raw_score <= 0.01:
                normalized_score = 0.0
            else:
                # Log-linear scaling for natural distribution
                import math
                normalized_score = min(99.0, max(15.0, round((math.sqrt(best_raw_score) * 115), 1)))

            # Extract matching keywords
            feature_names = vectorizer.get_feature_names_out()
            jd_nonzeros = jd_vec.nonzero()[1]
            proj_nonzeros = set(project_vecs[best_idx].nonzero()[1])
            common_indices = [idx for idx in jd_nonzeros if idx in proj_nonzeros]
            
            # Sort matching terms by TF-IDF weight in JD
            common_terms = sorted(common_indices, key=lambda idx: jd_vec[0, idx], reverse=True)
            matched_keywords = [feature_names[i] for i in common_terms[:6] if len(feature_names[i]) > 2]

            return {
                "match_score": normalized_score,
                "best_project": best_project["title"],
                "best_project_domain": best_project["inferred_domain"],
                "matched_keywords": matched_keywords
            }
        except Exception:
            return {
                "match_score": 0.0,
                "best_project": "N/A",
                "best_project_domain": "general",
                "matched_keywords": []
            }
