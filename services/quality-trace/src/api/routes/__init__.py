"""
API 路由模块
"""
from fastapi import APIRouter

from .traces import router as traces_router

__all__ = ["traces_router"]