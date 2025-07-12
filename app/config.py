import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings and configuration."""    
    # API Configuration
    app_name: str = "AI Content Moderation API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # CORS Configuration
    allowed_origins: list[str] = Field(
        default=["*"],  # For development - restrict in production
        description="Allowed CORS origins"
    )
    
    # OpenAI Configuration (for text moderation)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")

    # OCR.space Configuration
    ocr_api_key: Optional[str] = Field(default=None, description="OCR API key")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
