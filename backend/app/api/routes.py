from fastapi import APIRouter, UploadFile, File, Form
from app.worker.tasks import analyze_task
from app.worker.celery_app import celery_app
from app.services.vector_store import search_similar_resumes
from app.services.embeddings import get_embedding

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