"""
FastAPI 主应用
报警管理服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config.settings import settings
from .config.database import init_db, close_db
from .api.routes import alarms_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info(f"环境: {settings.environment}")
    
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    yield
    
    # 关闭时清理
    logger.info("关闭应用...")
    close_db()
    logger.info("所有连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="报警管理服务 - 多级报警、自动推送、闭环管理",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(alarms_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "system": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        },
        "endpoints": {
            "api_documentation": "/docs",
            "health_check": "/api/v1/health",
            "alarms": "/api/v1/alarms",
            "statistics": "/api/v1/alarms/statistics/summary",
        },
        "links": {
            "swagger_ui": "/docs",
            "re_doc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }


@app.get("/api/v1/health")
@app.head("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5009,
        reload=settings.debug
    )