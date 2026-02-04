"""
刀具数据仓储
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from .base_repository import BaseRepository
from ..models.tool import Tool


class ToolRepository(BaseRepository[Tool]):
    """刀具数据仓储"""

    def __init__(self, db: Session):
        super().__init__(Tool, db)

    def get_by_type(self, tool_type: str) -> List[Tool]:
        """
        根据类型获取刀具
        
        Args:
            tool_type: 刀具类型
            
        Returns:
            刀具列表
        """
        return self.db.query(Tool).filter(Tool.type == tool_type).all()

    def get_by_diameter(self, diameter: float) -> List[Tool]:
        """
        根据直径获取刀具
        
        Args:
            diameter: 刀具直径
            
        Returns:
            刀具列表
        """
        return self.db.query(Tool).filter(Tool.zhi_jing == diameter).all()

    def search_by_name(self, name: str) -> List[Tool]:
        """
        根据名称搜索刀具
        
        Args:
            name: 刀具名称（模糊匹配）
            
        Returns:
            刀具列表
        """
        return self.db.query(Tool).filter(Tool.name.like(f"%{name}%")).all()

    def get_all_types(self) -> List[str]:
        """
        获取所有刀具类型
        
        Returns:
            刀具类型列表
        """
        tools = self.get_all()
        types = set(tool.type for tool in tools if tool.type)
        return sorted(list(types))