"""
目标函数模块
提供多种优化目标函数
"""
from typing import Dict, Callable
from enum import Enum


class ObjectiveType(Enum):
    """目标类型"""
    MAXIMIZE_MRR = "maximize_mrr"  # 最大化材料去除率
    MINIMIZE_TIME = "minimize_time"  # 最小化加工时间
    MINIMIZE_COST = "minimize_cost"  # 最小化加工成本
    MAXIMIZE_TOOL_LIFE = "maximize_tool_life"  # 最大化刀具寿命
    MULTI_OBJECTIVE = "multi_objective"  # 多目标优化


class ObjectiveFunction:
    """目标函数类"""

    @staticmethod
    def maximize_mrr(params: Dict[str, float]) -> float:
        """
        最大化材料去除率
        
        Args:
            params: 加工参数
            
        Returns:
            适应度值
        """
        return params.get("material_removal_rate", 0.0)

    @staticmethod
    def minimize_time(params: Dict[str, float]) -> float:
        """
        最小化加工时间
        
        Args:
            params: 加工参数
            
        Returns:
            适应度值（负值，因为最小化时间即最大化其倒数）
        """
        mrr = params.get("material_removal_rate", 1.0)
        return -1.0 / mrr  # 时间与材料去除率成反比

    @staticmethod
    def minimize_cost(params: Dict[str, float]) -> float:
        """
        最小化加工成本
        
        Args:
            params: 加工参数
            
        Returns:
            适应度值
        """
        # 简化成本模型：考虑刀具寿命和能效
        tool_life = params.get("tool_life", 1.0)
        mrr = params.get("material_removal_rate", 1.0)
        
        # 成本 = 刀具成本/寿命 + 能耗成本
        cost = 100.0 / tool_life + 0.1 / mrr
        return -cost  # 最小化成本

    @staticmethod
    def maximize_tool_life(params: Dict[str, float]) -> float:
        """
        最大化刀具寿命
        
        Args:
            params: 加工参数
            
        Returns:
            适应度值
        """
        return params.get("tool_life", 0.0)

    @staticmethod
    def multi_objective(params: Dict[str, float], weights: Dict[str, float] = None) -> float:
        """
        多目标优化
        
        Args:
            params: 加工参数
            weights: 各目标权重
            
        Returns:
            综合适应度值
        """
        if weights is None:
            weights = {
                "mrr": 0.4,
                "tool_life": 0.3,
                "surface_quality": 0.2,
                "energy_efficiency": 0.1
            }
        
        # 归一化各目标（简化处理）
        mrr_score = params.get("material_removal_rate", 0.0) / 1000.0
        tool_life_score = params.get("tool_life", 0.0) / 100.0
        surface_score = 1.0 / (params.get("bottom_roughness", 1.0) + 1.0)
        efficiency_score = 1.0 / (params.get("power", 1.0) + 1.0)
        
        # 加权求和
        fitness = (
            weights["mrr"] * mrr_score +
            weights["tool_life"] * tool_life_score +
            weights["surface_quality"] * surface_score +
            weights["energy_efficiency"] * efficiency_score
        )
        
        return fitness

    @classmethod
    def get_objective_function(cls, objective_type: str) -> Callable:
        """
        获取目标函数
        
        Args:
            objective_type: 目标类型
            
        Returns:
            目标函数
        """
        objective_map = {
            ObjectiveType.MAXIMIZE_MRR.value: cls.maximize_mrr,
            ObjectiveType.MINIMIZE_TIME.value: cls.minimize_time,
            ObjectiveType.MINIMIZE_COST.value: cls.minimize_cost,
            ObjectiveType.MAXIMIZE_TOOL_LIFE.value: cls.maximize_tool_life,
            ObjectiveType.MULTI_OBJECTIVE.value: cls.multi_objective,
        }
        
        return objective_map.get(objective_type, cls.maximize_mrr)