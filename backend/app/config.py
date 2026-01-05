from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    GEMINI_API_KEY: str
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100

    # Keep this so your app will NOT crash even if MODEL_NAME exists in .env or Windows env vars
    MODEL_NAME: str = "models/gemini-2.5-flash"

settings = Settings()