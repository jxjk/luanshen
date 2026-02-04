"""
API 路由模块
"""
from fastapi import APIRouter

from .alarms import router as alarms_router

__all__ = ["alarms_router"]