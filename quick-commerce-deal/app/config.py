"""Configuration settings for the Quick Commerce Deals application."""

import os
from typing import Optional
from pydantic import BaseModel

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    database_url: str = "sqlite:///./quick_commerce.db"
    database_echo: bool = False
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    
    # Application Settings
    app_name: str = "Quick Commerce Deals"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Data Generation
    generate_sample_data: bool = True
    sample_data_size: str = "large"
    
    # Performance
    query_cache_expire_seconds: int = 300
    max_query_results: int = 1000
    enable_query_monitoring: bool = True
    
    # Quick Commerce Platforms
    supported_platforms: list = [
        "Blinkit",
        "Zepto", 
        "Instamart",
        "BigBasket Now",
        "Dunzo",
        "Grofers",
        "Amazon Fresh",
        "Flipkart Quick"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 