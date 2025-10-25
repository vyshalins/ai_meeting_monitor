from pydantic import BaseSettings

class Settings(BaseSettings):
    # FastAPI settings
    PROJECT_NAME: str = "AI Meeting Monitor"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str
    
    # Other settings can be added here
    # For example, API keys, external service URLs, etc.
    
    class Config:
        env_file = ".env"

settings = Settings()