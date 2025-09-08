from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine
from .models.models import Base
from .api import events, users, votes, search

# 创建数据库表（仅在数据库可用时）
try:
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功")
except Exception as e:
    print(f"数据库连接失败，请确保MySQL已启动并创建了truthmirror数据库: {e}")
    print("应用仍可启动，但数据库相关功能暂时不可用")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="真相之镜 - 基于AI和众包验证的事件真相验证平台"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(votes.router, prefix="/api/v1", tags=["votes"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])

@app.get("/")
async def root():
    return {
        "message": "欢迎使用真相之镜API",
        "version": settings.version,
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)