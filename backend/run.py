
"""
真相之镜后端启动脚本
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,  # 修正为8000端口
        reload=True,
        log_level="info"
    )