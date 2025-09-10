
"""
真相之镜后端启动脚本
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8003,  # 使用8003端口
        reload=True,
        log_level="info"
    )