import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://wisdom:wisdom123@localhost:5432/wisdom_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    CHROMADB_HOST: str = "http://localhost:8001"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_USE_SSL: bool = False
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    OPENAI_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None
    
    LEARNING_ENABLED: bool = True
    DOUYIN_KEYWORDS: str = "职场话术,领导意图,官场智慧,人情世故,社交技巧"
    BILIBILI_KEYWORDS: str = "职场沟通,心理学,人际关系,情商提升"
    
    VIDEO_STORAGE_PATH: str = "/data/videos"
    WHISPER_MODEL: str = "base"
    
    class Config:
        env_file = ".env"


settings = Settings()
