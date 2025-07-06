"""
Configuration management for the FastAPI backend.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application Settings
    app_name: str = Field(default="Design Gallery API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Security Settings
    jwt_secret: str = Field(env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=168, env="JWT_EXPIRATION_HOURS")  # 7 days
    
    # Cloudflare D1 Settings
    cloudflare_account_id: str = Field(env="CLOUDFLARE_ACCOUNT_ID")
    cloudflare_d1_database_id: str = Field(env="CLOUDFLARE_D1_DATABASE_ID")
    cloudflare_api_token: str = Field(env="CLOUDFLARE_API_TOKEN")
    
    # Cloudflare R2 Settings
    cloudflare_r2_account_id: str = Field(env="CLOUDFLARE_R2_ACCOUNT_ID")
    cloudflare_r2_access_key: str = Field(env="CLOUDFLARE_R2_ACCESS_KEY")
    cloudflare_r2_secret_key: str = Field(env="CLOUDFLARE_R2_SECRET_KEY")
    cloudflare_r2_bucket_name: str = Field(env="CLOUDFLARE_R2_BUCKET_NAME")
    cloudflare_r2_public_url: str = Field(env="CLOUDFLARE_R2_PUBLIC_URL")
    
    # CORS Settings
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: list = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Database Settings
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # File Upload Settings
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: list = Field(default=["image/jpeg", "image/png", "image/webp"], env="ALLOWED_FILE_TYPES")
    
    # Pagination Settings
    default_page_size: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 