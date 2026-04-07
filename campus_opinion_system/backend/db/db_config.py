import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # MongoDB配置
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "campus_opinion")
    
    # PostgreSQL配置
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://postgres:password@localhost:5432/campus_opinion")
    
    # Redis配置（用于Celery）
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()