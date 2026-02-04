"""
API 路由模块
"""
from fastapi import APIRouter

from .devices import router as devices_router
from .monitoring import router as monitoring_router
from .ws import router as ws_router

__all__ = ["devices_router", "monitoring_router", "ws_router"]