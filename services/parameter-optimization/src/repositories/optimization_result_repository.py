"""
优化结果数据仓储
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from .base_repository import BaseRepository
from ..models.optimization_result import OptimizationResult


class OptimizationResultRepository(BaseRepository[OptimizationResult]):
    """优化结果数据仓储"""

    def __init__(self, db: Session):
        super().__init__(OptimizationResult, db)

    def get_by_input_ids(
        self,
        material_id: Optional[int],
        tool_id: Optional[int],
        machine_id: Optional[int],
        method_id: Optional[int]
    ) -> List[OptimizationResult]:
        """
        根据输入参数ID获取优化结果
        
        Args:
            material_id: 材料ID
            tool_id: 刀具ID
            machine_id: 设备ID
            method_id: 策略ID
            
        Returns:
            优化结果列表
        """
        query = self.db.query(OptimizationResult)
        
        if material_id is not None:
            query = query.filter(OptimizationResult.ci_liao_id == material_id)
        if tool_id is not None:
            query = query.filter(OptimizationResult.tool_id == tool_id)
        if machine_id is not None:
            query = query.filter(OptimizationResult.machine_id == machine_id)
        if method_id is not None:
            query = query.filter(OptimizationResult.method_id == method_id)
            
        return query.order_by(desc(OptimizationResult.created_at)).all()

    def get_latest_results(self, limit: int = 10) -> List[OptimizationResult]:
        """
        获取最新的优化结果
        
        Args:
            limit: 返回数量
            
        Returns:
            优化结果列表
        """
        return self.db.query(OptimizationResult).order_by(
            desc(OptimizationResult.created_at)
        ).limit(limit).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[OptimizationResult]:
        """
        根据日期范围获取优化结果
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            优化结果列表
        """
        return self.db.query(OptimizationResult).filter(
            OptimizationResult.created_at >= start_date,
            OptimizationResult.created_at <= end_date
        ).order_by(desc(OptimizationResult.created_at)).all()