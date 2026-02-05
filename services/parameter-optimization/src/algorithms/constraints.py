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

    def check_vendor_params(
        self, 
        params: Dict[str, float], 
        vendor_params: Dict[str, float]
    ) -> Tuple[bool, List[ConstraintViolation]]:
        """
        检查刀具供应商参数
        
        Args:
            params: 加工参数
            vendor_params: 供应商推荐参数
            
        Returns:
            (是否满足供应商参数, 违规列表)
        """
        violations = []
        
        # 检查转速范围
        speed = params.get("speed", 0)
        if "recommended_speed_min" in vendor_params and speed < vendor_params["recommended_speed_min"]:
            violations.append(ConstraintViolation(
                constraint_name="speed_min",
                actual_value=speed,
                limit_value=vendor_params["recommended_speed_min"],
                severity="warning"
            ))
        
        if "recommended_speed_max" in vendor_params and speed > vendor_params["recommended_speed_max"]:
            violations.append(ConstraintViolation(
                constraint_name="speed_max",
                actual_value=speed,
                limit_value=vendor_params["recommended_speed_max"],
                severity="error"
            ))
        
        # 检查进给范围
        feed = params.get("feed", 0)
        if "recommended_feed_min" in vendor_params and feed < vendor_params["recommended_feed_min"]:
            violations.append(ConstraintViolation(
                constraint_name="feed_min",
                actual_value=feed,
                limit_value=vendor_params["recommended_feed_min"],
                severity="warning"
            ))
        
        if "recommended_feed_max" in vendor_params and feed > vendor_params["recommended_feed_max"]:
            violations.append(ConstraintViolation(
                constraint_name="feed_max",
                actual_value=feed,
                limit_value=vendor_params["recommended_feed_max"],
                severity="error"
            ))
        
        # 检查切深
        cut_depth = params.get("cut_depth", 0)
        if "recommended_cut_depth_max" in vendor_params and cut_depth > vendor_params["recommended_cut_depth_max"]:
            violations.append(ConstraintViolation(
                constraint_name="cut_depth_max",
                actual_value=cut_depth,
                limit_value=vendor_params["recommended_cut_depth_max"],
                severity="error"
            ))
        
        # 检查切宽
        cut_width = params.get("cut_width", 0)
        if "recommended_cut_width_max" in vendor_params and cut_width > vendor_params["recommended_cut_width_max"]:
            violations.append(ConstraintViolation(
                constraint_name="cut_width_max",
                actual_value=cut_width,
                limit_value=vendor_params["recommended_cut_width_max"],
                severity="error"
            ))
        
        return len(violations) == 0, violations
    
    def check_physical_strength(
        self, 
        params: Dict[str, float], 
        tool_params: Dict[str, float]
    ) -> Tuple[bool, List[ConstraintViolation]]:
        """
        检查物理强度约束
        
        Args:
            params: 加工参数
            tool_params: 刀具物理参数
            
        Returns:
            (是否满足物理强度约束, 违规列表)
        """
        violations = []
        
        # 计算切削力
        cutting_force = self._calculate_cutting_force(params, tool_params)
        max_tool_force = tool_params.get("tool_stiffness", 1000) * 0.1  # 变形不超过 0.1mm
        
        if cutting_force > max_tool_force:
            violations.append(ConstraintViolation(
                constraint_name="cutting_force",
                actual_value=cutting_force,
                limit_value=max_tool_force,
                severity="critical"
            ))
        
        # 计算刀具变形
        deflection = cutting_force / tool_params.get("tool_stiffness", 1000)
        max_deflection = 0.1  # 最大允许变形 0.1mm
        
        if deflection > max_deflection:
            violations.append(ConstraintViolation(
                constraint_name="tool_deflection",
                actual_value=deflection,
                limit_value=max_deflection,
                severity="error"
            ))
        
        # 检查刀具悬伸限制
        tool_overhang = tool_params.get("tool_overhang", 0)
        tool_diameter = tool_params.get("diameter", 10)
        cut_depth = params.get("cut_depth", 0)
        
        if tool_overhang > tool_diameter * 3 and cut_depth > tool_diameter * 0.3:
            violations.append(ConstraintViolation(
                constraint_name="tool_overhang",
                actual_value=cut_depth,
                limit_value=tool_diameter * 0.3,
                severity="warning"
            ))
        
        return len(violations) == 0, violations
    
    def _calculate_cutting_force(
        self, 
        params: Dict[str, float], 
        tool_params: Dict[str, float]
    ) -> float:
        """计算切削力"""
        feed = params.get("feed", 0)
        cut_depth = params.get("cut_depth", 0)
        cut_width = params.get("cut_width", 0)
        
        # 基于材料切削力系数
        force_coefficient = tool_params.get("cutting_force_coefficient", 2000)
        
        force = (
            force_coefficient * 
            cut_depth * cut_width * 
            (feed / 1000) ** 0.5
        )
        
        return force
    
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