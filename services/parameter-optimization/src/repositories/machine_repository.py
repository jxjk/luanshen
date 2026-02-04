"""
设备数据仓储
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models.machine import Machine


class MachineRepository(BaseRepository[Machine]):
    """设备数据仓储"""

    def __init__(self, db: Session):
        super().__init__(Machine, db)

    def get_by_type(self, machine_type: str) -> List[Machine]:
        """
        根据类型获取设备
        
        Args:
            machine_type: 设备类型
            
        Returns:
            设备列表
        """
        return self.db.query(Machine).filter(Machine.type == machine_type).all()

    def get_by_power_range(self, min_power: float, max_power: float) -> List[Machine]:
        """
        根据功率范围获取设备
        
        Args:
            min_power: 最小功率
            max_power: 最大功率
            
        Returns:
            设备列表
        """
        return self.db.query(Machine).filter(
            Machine.pw_max >= min_power,
            Machine.pw_max <= max_power
        ).all()

    def search_by_name(self, name: str) -> List[Machine]:
        """
        根据名称搜索设备
        
        Args:
            name: 设备名称（模糊匹配）
            
        Returns:
            设备列表
        """
        return self.db.query(Machine).filter(Machine.name.like(f"%{name}%")).all()