
"""
真相之镜后端启动脚本
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
<<<<<<< HEAD
        port=8000,  # 修正为8000端口
=======
        port=8003,  # 使用8003端口
>>>>>>> 9c5b02b2cae790d904bb1f964a817e5cef3977f1
        reload=True,
        log_level="info"
    )