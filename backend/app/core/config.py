from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise MLOps Platform"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./mlops.db"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"

    class Config:
        case_sensitive = True

settings = Settings()
