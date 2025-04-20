from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # OpenRouter configuration
    OPENROUTER_API_KEY: str = Field(..., env="OPENROUTER_API_KEY")
    OPENROUTER_DEFAULT_MODEL: str = Field(
        default="mistralai/mistral-small-3.1-24b-instruct:free",
        env="OPENROUTER_DEFAULT_MODEL"
    )
    OPENROUTER_FORCE_MODEL: bool = Field(
        default=True,
        env="OPENROUTER_FORCE_MODEL"
    )
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL"
    )
    
    # Application Configuration
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Data Storage
    DATA_DIR: Path = Path("./data")
    CACHE_DIR: Path = Path("./data/cache")
    
    # API configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    
    # Cache configuration
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Ensure data directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)