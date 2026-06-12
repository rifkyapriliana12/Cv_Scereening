import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple

class CVMatcher:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def compute_similarity(self, cv_text: str, requirement_text: str) -> float:
        cv_embed = self.model.encode(cv_text[:2000], normalize_embeddings=True)
        req_embed = self.model.encode(requirement_text[:2000], normalize_embeddings=True)
        return float(np.dot(cv_embed, req_embed))

    def compute_skill_match(self, cv_skills: List[str], requirement_text: str) -> float:
        if not cv_skills:
            return 0.0
        req_lower = requirement_text.lower()
        matched = sum(1 for skill in cv_skills if skill.lower() in req_lower)
        return matched / max(len(cv_skills), 1)

    def compute_keyword_match(self, cv_text: str, requirement_text: str) -> float:
        keywords = ["architect", "design", "autocad", "sketchup", "revit", "visualization",
                    "project management", "communication", "building code", "interior",
                    "drafting", "construction", "site", "3d", "rendering"]
        req_lower = requirement_text.lower()
        cv_lower = cv_text.lower()

        matched_keywords = 0
        for kw in keywords:
            if kw in req_lower and kw in cv_lower:
                matched_keywords += 1

        relevant_keywords = sum(1 for kw in keywords if kw in req_lower)
        if relevant_keywords == 0:
            return 0.5
        return matched_keywords / relevant_keywords

    def calculate_score(self, cv_data: Dict, vacancy_text: str) -> Dict:
        cv_text = cv_data.get("raw_text", "")
        cv_skills = cv_data.get("skills", [])

        semantic_score = max(0.0, self.compute_similarity(cv_text, vacancy_text))
        skill_score = self.compute_skill_match(cv_skills, vacancy_text)
        keyword_score = self.compute_keyword_match(cv_text, vacancy_text)
        exp_score = cv_data.get("experience_score", 0)

        total = (semantic_score * 0.35 + skill_score * 0.30 +
                 keyword_score * 0.20 + exp_score * 0.15)

        total = min(max(total, 0.0), 1.0)

        return {
            "total_score": round(total * 100, 2),
            "semantic_score": round(semantic_score * 100, 2),
            "skill_match_score": round(skill_score * 100, 2),
            "keyword_match_score": round(keyword_score * 100, 2),
            "experience_score": round(exp_score * 100, 2),
        }

    def rank_candidates(self, cv_data_list: List[Dict], vacancy_text: str) -> List[Tuple[Dict, Dict]]:
        results = []
        for cv_data in cv_data_list:
            scores = self.calculate_score(cv_data, vacancy_text)
            results.append((cv_data, scores))

        results.sort(key=lambda x: x[1]["total_score"], reverse=True)
        return results
