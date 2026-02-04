"""
API 路由模块
"""
from .optimization import router as optimization_router
from .materials import router as materials_router
from .tools import router as tools_router
from .machines import router as machines_router
from .strategies import router as strategies_router

__all__ = [
    "optimization_router",
    "materials_router",
    "tools_router",
    "machines_router",
    "strategies_router",
]