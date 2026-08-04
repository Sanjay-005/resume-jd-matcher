from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    resume_filename = Column(String(255), nullable=False)
    jd_text = Column(Text, nullable=False)

    semantic_score = Column(Float)
    skill_score = Column(Float)
    composite_score = Column(Float)

    resume_skills = Column(JSON)
    jd_skills = Column(JSON)
    gap_analysis = Column(JSON)
    bias_check = Column(JSON)

    qdrant_point_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
