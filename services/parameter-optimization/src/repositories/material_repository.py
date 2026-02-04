"""
材料数据仓储
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from .base_repository import BaseRepository
from ..models.material import Material


class MaterialRepository(BaseRepository[Material]):
    """材料数据仓储"""

    def __init__(self, db: Session):
        super().__init__(Material, db)

    def get_by_group(self, group: str) -> Optional[Material]:
        """
        根据材料组获取材料
        
        Args:
            group: 材料组（如 P1, M1, K1 等）
            
        Returns:
            找到的材料，不存在则返回 None
        """
        return self.db.query(Material).filter(Material.cai_liao_zu == group).first()

    def get_all_groups(self) -> List[str]:
        """
        获取所有材料组
        
        Returns:
            材料组列表
        """
        materials = self.get_all()
        return [m.cai_liao_zu for m in materials]

    def search_by_name(self, name: str) -> List[Material]:
        """
        根据名称搜索材料
        
        Args:
            name: 材料名称（模糊匹配）
            
        Returns:
            匹配的材料列表
        """
        return self.db.query(Material).filter(Material.name.like(f"%{name}%")).all()

    def get_by_strength_range(self, rm_min: int, rm_max: int) -> List[Material]:
        """
        根据强度范围获取材料
        
        Args:
            rm_min: 最小强度
            rm_max: 最大强度
            
        Returns:
            符合条件的材料列表
        """
        return self.db.query(Material).filter(
            Material.rm_min >= rm_min,
            Material.rm_max <= rm_max
        ).all()