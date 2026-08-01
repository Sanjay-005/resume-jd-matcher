from pydantic import BaseModel

class AnalyzeResponse(BaseModel):
    resume_text: str
    jd_text: str
    similarity_score: float