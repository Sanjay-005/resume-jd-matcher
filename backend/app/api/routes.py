from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.worker.tasks import analyze_task
from app.worker.celery_app import celery_app
from app.services.vector_store import search_similar_resumes
from app.services.embeddings import get_embedding
from app.db.database import get_db
from app.db.models import AnalysisRecord

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/analyze")
async def analyze(resume: UploadFile = File(...), jd_text: str = Form(...)):
    resume_bytes = await resume.read()
    task = analyze_task.delay(resume.filename, resume_bytes.hex(), jd_text)
    return {"task_id": task.id, "status": "processing"}

@router.post("/batch-rank")
async def batch_rank(jd_text: str = Form(...), top_k: int = Form(10)):
    jd_vec = get_embedding(jd_text)
    results = search_similar_resumes(jd_vec, top_k=top_k)
    return {"jd_text": jd_text, "ranked_resumes": results}

@router.get("/result/{task_id}")
def get_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "SUCCESS":
        return {"status": "completed", "result": result.result}
    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.info)}
    return {"status": result.state}

@router.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    records = (
        db.query(AnalysisRecord)
        .order_by(AnalysisRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "resume_filename": r.resume_filename,
                "semantic_score": r.semantic_score,
                "skill_score": r.skill_score,
                "composite_score": r.composite_score,
                "resume_skills": r.resume_skills,
                "jd_skills": r.jd_skills,
                "gap_analysis": r.gap_analysis,
                "bias_check": r.bias_check,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
    }
