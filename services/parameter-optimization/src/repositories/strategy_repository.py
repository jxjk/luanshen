"""
加工策略数据仓储
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models.strategy import Strategy


class StrategyRepository(BaseRepository[Strategy]):
    """加工策略数据仓储"""

    def __init__(self, db: Session):
        super().__init__(Strategy, db)

    def get_by_type(self, strategy_type: str) -> List[Strategy]:
        """
        根据类型获取策略
        
        Args:
            strategy_type: 加工类型
            
        Returns:
            策略列表
        """
        return self.db.query(Strategy).filter(Strategy.type == strategy_type).all()

    def get_all_types(self) -> List[str]:
        """
        获取所有加工类型
        
        Returns:
            加工类型列表
        """
        strategies = self.get_all()
        types = set(strategy.type for strategy in strategies if strategy.type)
        return sorted(list(types))

    def search_by_name(self, name: str) -> List[Strategy]:
        """
        根据名称搜索策略
        
        Args:
            name: 策略名称（模糊匹配）
            
        Returns:
            策略列表
        """
        return self.db.query(Strategy).filter(Strategy.name.like(f"%{name}%")).all()