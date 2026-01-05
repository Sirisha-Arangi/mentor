from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AI Teaching Assistant"
    
    # Gemini Configuration
    GEMINI_API_KEY: str = "AIzaSyDHRmUf6srCdtKbGp7T36xMzKSn4TvyH24"
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    
    # RAG Configuration
    EMBEDDING_MODEL: str = "models/embedding-001"
    CHAT_MODEL: str = "gemini-pro"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()