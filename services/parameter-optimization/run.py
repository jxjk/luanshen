"""
服务启动脚本
"""
import uvicorn
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import settings


def main():
    """启动服务"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              工艺参数优化系统 - 参数优化服务              ║
╠══════════════════════════════════════════════════════════╣
║  版本: {settings.app_version:<46} ║
║  环境: {settings.environment:<46} ║
╠══════════════════════════════════════════════════════════╣
║  API 地址: http://{settings.api_host}:{settings.api_port:<20} ║
║  API 文档: http://{settings.api_host}:{settings.api_port}/docs<{14} ║
║  健康检查: http://{settings.api_host}:{settings.api_port}/api/v1/optimization/health<{4} ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=1 if settings.api_reload else settings.api_workers,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()