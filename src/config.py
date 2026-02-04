"""Configuration management for the RAG system"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Endee Configuration
    endee_base_url: str = "http://localhost:8080"
    endee_auth_token: Optional[str] = None
    endee_timeout: int = 30
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Document Processing
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 5
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 500
    
    # Ollama Configuration (alternative to OpenAI)
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
