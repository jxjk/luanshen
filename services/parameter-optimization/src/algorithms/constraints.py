"""
约束检查模块
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ConstraintViolation:
    """约束违规信息"""
    constraint_name: str
    actual_value: float
    limit_value: float
    severity: str  # "warning" or "error"


class ConstraintChecker:
    """约束检查器"""

    def __init__(self, constraints: Dict[str, float]):
        """
        初始化约束检查器
        
        Args:
            constraints: 约束值字典
        """
        self.constraints = constraints

    def check_all(self, params: Dict[str, float]) -> Tuple[bool, List[ConstraintViolation]]:
        """
        检查所有约束
        
        Args:
            params: 加工参数
            
        Returns:
            (是否满足所有约束, 违规列表)
        """
        violations = []
        
        # 检查功率约束
        if "power" in params and "max_power" in self.constraints:
            if params["power"] > self.constraints["max_power"]:
                violations.append(ConstraintViolation(
                    constraint_name="power",
                    actual_value=params["power"],
                    limit_value=self.constraints["max_power"],
                    severity="error"
                ))
        
        # 检查扭矩约束
        if "torque" in params and "max_torque" in self.constraints:
            if params["torque"] > self.constraints["max_torque"]:
                violations.append(ConstraintViolation(
                    constraint_name="torque",
                    actual_value=params["torque"],
                    limit_value=self.constraints["max_torque"],
                    severity="error"
                ))
        
        # 检查刀具寿命约束
        if "tool_life" in params and "min_tool_life" in self.constraints:
            if params["tool_life"] < self.constraints["min_tool_life"]:
                violations.append(ConstraintViolation(
                    constraint_name="tool_life",
                    actual_value=params["tool_life"],
                    limit_value=self.constraints["min_tool_life"],
                    severity="error"
                ))
        
        # 检查表面粗糙度约束
        if "bottom_roughness" in params and "min_surface_roughness" in self.constraints:
            if params["bottom_roughness"] > self.constraints["min_surface_roughness"]:
                violations.append(ConstraintViolation(
                    constraint_name="surface_roughness",
                    actual_value=params["bottom_roughness"],
                    limit_value=self.constraints["min_surface_roughness"],
                    severity="error"
                ))
        
        # 检查进给力约束
        if "feed_force" in params and "max_feed_force" in self.constraints:
            if params["feed_force"] > self.constraints["max_feed_force"]:
                violations.append(ConstraintViolation(
                    constraint_name="feed_force",
                    actual_value=params["feed_force"],
                    limit_value=self.constraints["max_feed_force"],
                    severity="error"
                ))
        
        # 检查每齿进给量约束
        if "feed_per_tooth" in params and "max_feed_per_tooth" in self.constraints:
            if params["feed_per_tooth"] > self.constraints["max_feed_per_tooth"]:
                violations.append(ConstraintViolation(
                    constraint_name="feed_per_tooth",
                    actual_value=params["feed_per_tooth"],
                    limit_value=self.constraints["max_feed_per_tooth"],
                    severity="error"
                ))
        
        # 检查线速度约束
        if "cutting_speed" in params and "max_cutting_speed" in self.constraints:
            if params["cutting_speed"] > self.constraints["max_cutting_speed"]:
                violations.append(ConstraintViolation(
                    constraint_name="cutting_speed",
                    actual_value=params["cutting_speed"],
                    limit_value=self.constraints["max_cutting_speed"],
                    severity="error"
                ))
        
        return len(violations) == 0, violations

    def calculate_penalty(self, params: Dict[str, float]) -> float:
        """
        计算约束违规惩罚值
        
        Args:
            params: 加工参数
            
        Returns:
            惩罚值
        """
        _, violations = self.check_all(params)
        
        penalty = 0.0
        for violation in violations:
            # 计算违规程度
            if violation.constraint_name in ["tool_life"]:
                # 约束是下限，值越小惩罚越大
                diff = violation.limit_value - violation.actual_value
            else:
                # 约束是上限，值越大惩罚越大
                diff = violation.actual_value - violation.limit_value
            
            # 平方惩罚
            penalty += diff ** 2
        
        return penalty