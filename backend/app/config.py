from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AI Teaching Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]  # In production, replace with your frontend URL
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "txt", "docx"]
    
    # Vector store settings
    VECTOR_STORE_PATH: str = "data/vector_store"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # LLM settings
    LLM_PROVIDER: str = "openai"  # Options: "openai", "anthropic", "local"
    
    # Create upload directory if it doesn't exist
    def __init__(self, **values):
        super().__init__(**values)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.VECTOR_STORE_PATH, exist_ok=True)

# Create settings instance
settings = Settings()