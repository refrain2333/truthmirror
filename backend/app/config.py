from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseModel):
    # 基础配置
    app_name: str = "真相之镜"
    debug: bool = True
    version: str = "1.0.0"
    
    # 数据库配置 - 使用环境变量或默认值
    database_url: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/truthmirror")
    
    # Redis配置（用于Celery和缓存）
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # AI API配置
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # SearXNG配置
    searxng_url: str = os.getenv("SEARXNG_URL", "https://search.example.com")
    
    # JWT密钥
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 业务逻辑配置
    interest_threshold: int = int(os.getenv("INTEREST_THRESHOLD", "10"))  # 兴趣度阈值
    vote_threshold: int = int(os.getenv("VOTE_THRESHOLD", "10000"))   # 投票总数阈值
    victory_margin: float = float(os.getenv("VICTORY_MARGIN", "0.5"))   # 获胜边际（50%）

settings = Settings()