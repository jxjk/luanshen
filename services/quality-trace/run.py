"""
质量追溯服务启动脚本
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5010,
        reload=True,
        log_level="info"
    )