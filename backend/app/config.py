from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 基础配置
    app_name: str = "真相之镜"
    debug: bool = False
    version: str = "1.0.0"
    
    # 数据库配置
    database_url: str = "mysql+pymysql://user:password@localhost/truthmirror"
    
    # Redis配置（用于Celery和缓存）
    redis_url: str = "redis://localhost:6379"
    
    # AI API配置
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # SearXNG配置
    searxng_url: str = "https://search.example.com"
    
    # JWT密钥
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # 业务逻辑配置
    interest_threshold: int = 10  # 兴趣度阈值
    vote_threshold: int = 10000   # 投票总数阈值
    victory_margin: float = 0.5   # 获胜边际（50%）
    
    class Config:
        env_file = ".env"

settings = Settings()