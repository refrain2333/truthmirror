#!/usr/bin/env python
"""
真相之镜后端启动脚本
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8002,  # 使用8002端口（已验证可用）
        reload=True,
        log_level="info"
    )