from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid
from app.core.config import settings

client = QdrantClient(url=settings.qdrant_url)

RESUME_COLLECTION = "resumes"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

def ensure_collection():
    collections = [c.name for c in client.get_collections().collections]
    if RESUME_COLLECTION not in collections:
        client.create_collection(
            collection_name=RESUME_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

def store_resume(resume_id: str, vector: list[float], metadata: dict) -> str:
    ensure_collection()
    point_id = str(uuid.uuid4())
    client.upsert(
        collection_name=RESUME_COLLECTION,
        points=[PointStruct(id=point_id, vector=vector, payload={**metadata, "resume_id": resume_id})]
    )
    return point_id

def search_similar_resumes(jd_vector: list[float], top_k: int = 10) -> list[dict]:
    ensure_collection()
    results = client.query_points(
        collection_name=RESUME_COLLECTION,
        query=jd_vector,
        limit=top_k,
    ).points
    return [{"score": r.score, "payload": r.payload} for r in results]
