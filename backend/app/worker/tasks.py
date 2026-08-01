from app.worker.celery_app import celery_app
from app.services.parser import parse_resume
from app.services.embeddings import get_embedding
from app.services.scoring import cosine_similarity, skill_match_score, composite_score
from app.services.llm import extract_skills, gap_analysis, bias_check
from app.services.vector_store import store_resume

@celery_app.task(name="analyze_task")
def analyze_task(filename: str, resume_bytes_hex: str, jd_text: str) -> dict:
    resume_bytes = bytes.fromhex(resume_bytes_hex)
    resume_text = parse_resume(filename, resume_bytes)

    resume_vec = get_embedding(resume_text)

    point_id = store_resume(
    resume_id=filename,
    vector=resume_vec,
    metadata={"filename": filename, "resume_snippet": resume_text[:300]}
)
    
    
    jd_vec = get_embedding(jd_text)
    semantic_score = cosine_similarity(resume_vec, jd_vec)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    skill_score = skill_match_score(resume_skills, jd_skills)

    scores = composite_score(semantic_score, skill_score)
    gaps = gap_analysis(resume_text, jd_text)
    bias = bias_check(jd_text)
    

    return {
        "scores": scores,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "gap_analysis": gaps,
        "bias_check": bias,
        "point_id": point_id
    }


