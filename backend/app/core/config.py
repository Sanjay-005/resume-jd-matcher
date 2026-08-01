from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    gemini_api_key: str
    hf_api_key: str
    database_url: str = "sqlite:///./test.db"  # temp, until Postgres in Phase 6
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    class Config:
        env_file = ".env"

settings = Settings()