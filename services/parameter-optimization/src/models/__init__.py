"""
数据模型模块
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass

from .material import Material
from .tool import Tool
from .machine import Machine
from .strategy import Strategy
from .optimization_result import OptimizationResult

__all__ = [
    "Base",
    "Material",
    "Tool",
    "Machine",
    "Strategy",
    "OptimizationResult",
]