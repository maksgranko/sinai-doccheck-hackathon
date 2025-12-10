"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # База данных MySQL (удаленная БД на сервере)
    DATABASE_URL: str = "mysql+pymysql://sinai_hackat:^R6E=>k[\\OVxT?l*@195.209.210.97:3306/sinai_hackat?charset=utf8mb4"
    DB_HOST: str = "195.209.210.97"
    DB_PORT: int = 3306
    DB_NAME: str = "sinai_hackat"
    DB_USER: str = "sinai_hackat"
    DB_PASSWORD: str = "^R6E=>k[\\OVxT?l*"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_SECRET_KEY: str = "change-this-in-production"
    API_DEBUG: bool = False
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Redis (опционально)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()



