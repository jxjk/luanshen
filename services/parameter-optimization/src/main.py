"""
FastAPI 主应用
参数优化服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .config.database import init_db, close_db
from .api.routes import (
    optimization_router,
    materials_router,
    tools_router,
    machines_router,
    strategies_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    print(f"启动 {settings.app_name} v{settings.app_version}")
    init_db()
    print("数据库初始化完成")
    yield
    # 关闭时清理资源
    print("关闭应用...")
    close_db()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="工艺参数优化系统 - 基于微生物遗传算法的智能参数优化服务",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(optimization_router, prefix="/api/v1/optimization")
app.include_router(materials_router, prefix="/api/v1/materials")
app.include_router(tools_router, prefix="/api/v1/tools")
app.include_router(machines_router, prefix="/api/v1/machines")
app.include_router(strategies_router, prefix="/api/v1/strategies")


@app.get("/")
async def root():
    """根路径"""
    return {
        "system": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        },
        "endpoints": {
            "api_documentation": "/docs",
            "health_check": "/api/v1/optimization/health",
            "materials": "/api/v1/materials",
            "tools": "/api/v1/tools",
            "machines": "/api/v1/machines",
            "strategies": "/api/v1/strategies",
            "optimization": "/api/v1/optimization/optimize"
        },
        "links": {
            "swagger_ui": "/docs",
            "re_doc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5007,
        reload=True
    )