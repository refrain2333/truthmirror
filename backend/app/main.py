from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
# 使用新的pymysql API模块
from .api import events, users, votes, search, analysis

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="真相之镜 - 基于AI和众包验证的事件真相验证平台（使用pymysql）"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],  # 允许前端访问所有响应头
)

# 包含API路由 - 全部使用pymysql
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(votes.router, prefix="/api/v1", tags=["votes"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])

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
    uvicorn.run(app, host="127.0.0.1", port=8003)