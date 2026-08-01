import numpy as np

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    a, b = np.array(vec1), np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def skill_match_score(resume_skills: list[str], jd_skills: list[str]) -> float:
    if not jd_skills:
        return 0.0
    resume_set = {s.lower().strip() for s in resume_skills}
    jd_set = {s.lower().strip() for s in jd_skills}
    matched = jd_set & resume_set
    return len(matched) / len(jd_set)

def composite_score(semantic_score: float, skill_score: float) -> dict:
    weights = {"semantic": 0.6, "skill": 0.4}
    composite = (semantic_score * weights["semantic"]) + (skill_score * weights["skill"])
    return {
        "semantic_score": round(semantic_score, 3),
        "skill_score": round(skill_score, 3),
        "composite_score": round(composite, 3),
        "weights": weights
    }