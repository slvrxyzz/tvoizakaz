"""
Конфигурация приложения с поддержкой переменных окружения
Enterprise-level configuration management
"""
import os
from secrets import token_urlsafe
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    app_name: str = "TeenFreelance"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "production"
    
    # Безопасность
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", token_urlsafe(48)))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_reset_token_ttl: int = 3600
    
    # База данных
    database_url: str = Field(default_factory=lambda: os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./teenfreelance.db",
    ))
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_recycle: int = 3600
    database_pool_pre_ping: bool = True
    
    # Redis
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    redis_password: Optional[str] = None
    
    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: (
            [item.strip() for item in os.getenv("CORS_ORIGINS", "").split(",") if item.strip()]
            if os.getenv("CORS_ORIGINS")
            else ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"]
        )
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v

    @validator('cors_origins', 'cors_allow_methods', 'cors_allow_headers', pre=True)
    def ensure_list(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return list(value)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (кэшированные)"""
    return Settings()


# Глобальные настройки
settings = get_settings()
