"""
Configuration management for AgenticOne Backend
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "AgenticOne Backend"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://agenticone.vercel.app"
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    VERTEX_AI_MODEL: str = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro")
    
    # Vector Search Configuration
    VECTOR_SEARCH_INDEX_ID: str = os.getenv("VECTOR_SEARCH_INDEX_ID", "")
    VECTOR_SEARCH_DIMENSIONS: int = int(os.getenv("VECTOR_SEARCH_DIMENSIONS", "768"))
    
    # Firestore Configuration
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "")
    FIRESTORE_DATABASE_ID: str = os.getenv("FIRESTORE_DATABASE_ID", "(default)")
    
    # Cloud Storage Configuration
    CLOUD_STORAGE_BUCKET: str = os.getenv("CLOUD_STORAGE_BUCKET", "")
    
    # Agent Configuration
    MAX_ANALYSIS_RETRIES: int = int(os.getenv("MAX_ANALYSIS_RETRIES", "3"))
    ANALYSIS_TIMEOUT: int = int(os.getenv("ANALYSIS_TIMEOUT", "300"))  # 5 minutes
    
    # Report Generation
    REPORT_TEMPLATE_PATH: str = os.getenv("REPORT_TEMPLATE_PATH", "templates/")
    REPORT_OUTPUT_PATH: str = os.getenv("REPORT_OUTPUT_PATH", "reports/")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

# Global settings instance
settings = Settings()
