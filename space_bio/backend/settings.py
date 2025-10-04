"""
Application settings using PydanticSettings for configuration management.
Handles environment variables and default values.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini API configuration
    GEMINI_API_KEY: str = Field(
        ...,
        description="Google Gemini API key for LLM functionality"
    )
    
    # Database configuration
    DATABASE_URL: str = Field(
        default="postgresql://postgres.mosdmbhepyzmzqygiixz:Sai_Parvathi16@db.mosdmbhepyzmzqygiixz.supabase.co:5432/postgres",
        description="PostgreSQL database URL with psycopg2 driver"
    )
    
    # CORS configuration
    ALLOW_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    @property
    def allow_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.ALLOW_ORIGINS.split(",") if origin.strip()]
    
    # Model configuration
    MODEL_NAME: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model name to use"
    )
    
    # Application settings
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # API settings
    MAX_MESSAGE_LENGTH: int = Field(
        default=4000,
        description="Maximum length for user messages"
    )
    
    MAX_RESPONSE_TOKENS: int = Field(
        default=800,
        description="Maximum tokens for AI responses"
    )
    
    # RAG settings
    MAX_CONTEXT_DOCS: int = Field(
        default=8,
        description="Maximum number of context documents to retrieve"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
