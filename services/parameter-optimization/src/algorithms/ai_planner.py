"""
AI 规划器模块
基于刀具供应商参数、材料特性和机床能力，智能设定参数搜索范围
"""
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class ToolVendorParams:
    """刀具供应商参数"""
    tool_type: str  # 刀具类型（面铣刀、立铣刀、钻头等）
    tool_material: str  # 刀具材料（硬质合金、高速钢、陶瓷等）
    coating: str  # 涂层类型
    
    # 供应商推荐参数范围
    recommended_speed_min: float  # 最小转速 (r/min)
    recommended_speed_max: float  # 最大转速 (r/min)
    recommended_feed_min: float  # 最小进给 (mm/min)
    recommended_feed_max: float  # 最大进给 (mm/min)
    recommended_cut_depth_max: float  # 最大切深 (mm)
    recommended_cut_width_max: float  # 最大切宽 (mm)
    
    # 物理限制
    max_cutting_speed: float  # 最大切削速度 (m/min)
    max_feed_per_tooth: float  # 最大每齿进给 (mm)
    tool_stiffness: float  # 刀具刚度 (N/μm)
    tool_overhang: float  # 刀具悬伸 (mm)
    
    # 刀具几何参数
    diameter: float  # 刀具直径 (mm)
    teeth: int  # 齿数
    corner_radius: float  # 刀尖圆角半径 (mm)
    helix_angle: float  # 螺旋角 (°)
    
    # 热性能
    max_operating_temp: float  # 最高工作温度 (°C)
    thermal_conductivity: float  # 热导率 (W/(m·K))


@dataclass
class MaterialProperties:
    """材料特性"""
    material_id: str  # 材料编号
    material_name: str  # 材料名称
    material_group: str  # 材料组别（P钢/M不锈钢/K铸铁/N有色金属）
    
    # 机械性能
    hardness: float  # 硬度 (HB)
    tensile_strength: float  # 抗拉强度 (MPa)
    yield_strength: float  # 屈服强度 (MPa)
    elongation: float  # 延伸率 (%)
    
    # 切削性能
    machinability: float  # 可加工性指数 (0-1)
    cutting_force_coefficient: float  # 切削力系数
    specific_cutting_energy: float  # 比切削能 (J/mm³)
    
    # 热性能
    thermal_conductivity: float  # 热导率 (W/(m·K))
    specific_heat: float  # 比热容 (J/(kg·K))
    melting_point: float  # 熔点 (°C)


@dataclass
class MachineCapabilities:
    """机床能力"""
    machine_type: str  # 机床类型（铣床、钻床、镗床、车床）
    
    # 主轴性能
    max_spindle_speed: float  # 最大转速 (r/min)
    max_spindle_power: float  # 最大功率 (kW)
    max_spindle_torque: float  # 最大扭矩 (N·m)
    
    # 进给性能
    max_feed_rate: float  # 最大进给速度 (mm/min)
    max_feed_force: float  # 最大进给力 (N)
    
    # 行程
    x_travel: float  # X轴行程 (mm)
    y_travel: float  # Y轴行程 (mm)
    z_travel: float  # Z轴行程 (mm)
    
    # 精度
    positioning_accuracy: float  # 定位精度 (mm)
    repeatability: float  # 重复定位精度 (mm)
    
    # 刚度
    spindle_stiffness: float  # 主轴刚度 (N/μm)
    table_stiffness: float  # 工作台刚度 (N/μm)


@dataclass
class SearchRange:
    """参数搜索范围"""
    speed_range: Tuple[float, float]  # 转速范围 (r/min)
    feed_range: Tuple[float, float]  # 进给范围 (mm/min)
    cut_depth_range: Tuple[float, float]  # 切深范围 (mm)
    cut_width_range: Tuple[float, float]  # 切宽范围 (mm)
    
    # 搜索范围说明
    reason: str  # 设定该范围的原因
    safety_factor: float  # 安全系数（相对于供应商推荐值）


class AIPlanner:
    """AI 规划器 - 智能设定参数搜索范围"""
    
    def __init__(
        self,
        tool_params: ToolVendorParams,
        material_props: MaterialProperties,
        machine_caps: MachineCapabilities
    ):
        """
        初始化 AI 规划器
        
        Args:
            tool_params: 刀具供应商参数
            material_props: 材料特性
            machine_caps: 机床能力
        """
        self.tool = tool_params
        self.material = material_props
        self.machine = machine_caps
        
        # 安全系数配置
        self.safety_factors = {
            "speed": 0.9,  # 转速安全系数
            "feed": 0.85,  # 进给安全系数
            "cut_depth": 0.8,  # 切深安全系数
            "cut_width": 0.85,  # 切宽安全系数
        }
    
    def plan_search_range(self, machining_method: str = "MILLING") -> SearchRange:
        """
        规划参数搜索范围
        
        Args:
            machining_method: 加工方法
            
        Returns:
            搜索范围对象
        """
        # 1. 基于刀具供应商参数
        speed_range = self._plan_speed_range()
        feed_range = self._plan_feed_range()
        cut_depth_range = self._plan_cut_depth_range()
        cut_width_range = self._plan_cut_width_range()
        
        # 2. 基于材料特性调整
        speed_range = self._adjust_for_material(speed_range, "speed")
        feed_range = self._adjust_for_material(feed_range, "feed")
        cut_depth_range = self._adjust_for_material(cut_depth_range, "cut_depth")
        
        # 3. 基于机床能力限制
        speed_range = self._limit_by_machine(speed_range, "speed")
        feed_range = self._limit_by_machine(feed_range, "feed")
        
        # 4. 基于加工方法调整
        if machining_method == "DRILLING":
            # 钻孔特殊处理
            cut_width_range = (0, 0)  # 钻孔无切宽
            cut_depth_range = (0, self.tool.diameter * 2.5)  # 钻深限制
        
        reason = self._generate_reason()
        safety_factor = min(self.safety_factors.values())
        
        return SearchRange(
            speed_range=speed_range,
            feed_range=feed_range,
            cut_depth_range=cut_depth_range,
            cut_width_range=cut_width_range,
            reason=reason,
            safety_factor=safety_factor
        )
    
    def _plan_speed_range(self) -> Tuple[float, float]:
        """规划转速范围"""
        # 基于刀具供应商推荐值
        min_speed = self.tool.recommended_speed_min
        max_speed = self.tool.recommended_speed_max
        
        # 应用安全系数
        max_speed = max_speed * self.safety_factors["speed"]
        
        # 确保不低于最小值
        min_speed = max(min_speed, 100)  # 最小 100 r/min
        
        # 基于刀具直径校验（避免共振）
        critical_speed = 30000 / self.tool.diameter  # 临界转速估算
        if max_speed > critical_speed * 0.8:
            max_speed = critical_speed * 0.8  # 避开共振区
        
        # 基于切削速度限制
        max_speed_by_cutting_speed = (
            self.tool.max_cutting_speed * 318.0 / self.tool.diameter
        )
        max_speed = min(max_speed, max_speed_by_cutting_speed)
        
        return (min_speed, max_speed)
    
    def _plan_feed_range(self) -> Tuple[float, float]:
        """规划进给范围"""
        # 基于刀具供应商推荐值
        min_feed = self.tool.recommended_feed_min
        max_feed = self.tool.recommended_feed_max
        
        # 应用安全系数
        max_feed = max_feed * self.safety_factors["feed"]
        
        # 基于每齿进给限制
        max_feed_by_per_tooth = (
            self.tool.max_feed_per_tooth * self.tool.teeth * self.tool.recommended_speed_min
        )
        max_feed = min(max_feed, max_feed_by_per_tooth)
        
        # 基于刀具刚度校验
        max_feed_by_stiffness = self._calculate_max_feed_by_stiffness()
        max_feed = min(max_feed, max_feed_by_stiffness)
        
        # 确保不低于最小值
        min_feed = max(min_feed, 10)  # 最小 10 mm/min
        
        return (min_feed, max_feed)
    
    def _plan_cut_depth_range(self) -> Tuple[float, float]:
        """规划切深范围"""
        # 基于刀具供应商推荐值
        min_cut_depth = 0.1  # 最小切深 0.1mm
        max_cut_depth = self.tool.recommended_cut_depth_max
        
        # 应用安全系数
        max_cut_depth = max_cut_depth * self.safety_factors["cut_depth"]
        
        # 基于刀具直径限制
        max_cut_depth_by_diameter = self.tool.diameter * 0.5  # 切深不超过直径的50%
        max_cut_depth = min(max_cut_depth, max_cut_depth_by_diameter)
        
        # 基于刀具刚度校验
        max_cut_depth_by_stiffness = self._calculate_max_cut_depth_by_stiffness()
        max_cut_depth = min(max_cut_depth, max_cut_depth_by_stiffness)
        
        # 基于刀具悬伸限制
        max_cut_depth_by_overhang = self.tool.diameter * (self.tool.diameter / self.tool.overhang)
        max_cut_depth = min(max_cut_depth, max_cut_depth_by_overhang)
        
        return (min_cut_depth, max_cut_depth)
    
    def _plan_cut_width_range(self) -> Tuple[float, float]:
        """规划切宽范围"""
        # 基于刀具供应商推荐值
        min_cut_width = 0.1  # 最小切宽 0.1mm
        max_cut_width = self.tool.recommended_cut_width_max
        
        # 应用安全系数
        max_cut_width = max_cut_width * self.safety_factors["cut_width"]
        
        # 基于刀具直径限制
        max_cut_width_by_diameter = self.tool.diameter * 0.7  # 切宽不超过直径的70%
        max_cut_width = min(max_cut_width, max_cut_width_by_diameter)
        
        return (min_cut_width, max_cut_width)
    
    def _adjust_for_material(
        self, 
        range_tuple: Tuple[float, float], 
        param_type: str
    ) -> Tuple[float, float]:
        """基于材料特性调整参数范围"""
        min_val, max_val = range_tuple
        
        # 材料硬度调整
        hardness_factor = 1.0
        if self.material.hardness > 300:
            hardness_factor = 0.8  # 硬材料降低参数
        elif self.material.hardness < 150:
            hardness_factor = 1.1  # 软材料提高参数
        
        # 可加工性调整
        machinability_factor = self.material.machinability
        
        # 综合调整因子
        adjustment_factor = hardness_factor * machinability_factor
        
        if param_type in ["speed", "feed"]:
            # 转速和进给与材料可加工性正相关
            adjusted_max = max_val * adjustment_factor
        else:
            # 切深和切宽与材料硬度负相关
            adjusted_max = max_val * hardness_factor
        
        return (min_val, adjusted_max)
    
    def _limit_by_machine(
        self, 
        range_tuple: Tuple[float, float], 
        param_type: str
    ) -> Tuple[float, float]:
        """基于机床能力限制参数范围"""
        min_val, max_val = range_tuple
        
        if param_type == "speed":
            # 转速限制
            max_val = min(max_val, self.machine.max_spindle_speed)
        elif param_type == "feed":
            # 进给限制
            max_val = min(max_val, self.machine.max_feed_rate)
        
        return (min_val, max_val)
    
    def _calculate_max_feed_by_stiffness(self) -> float:
        """基于刀具刚度计算最大进给"""
        # 简化模型：刀具变形不超过 0.1mm
        max_force = self.tool.tool_stiffness * 0.1  # N
        max_feed = max_force / self.material.cutting_force_coefficient
        return max_feed
    
    def _calculate_max_cut_depth_by_stiffness(self) -> float:
        """基于刀具刚度计算最大切深"""
        # 简化模型：考虑刀具悬伸和刚度
        stiffness_factor = (self.tool.diameter / self.tool.overhang) ** 2
        max_cut_depth = self.tool.diameter * stiffness_factor * 0.5
        return max_cut_depth
    
    def _generate_reason(self) -> str:
        """生成搜索范围说明"""
        reasons = []
        
        reasons.append(f"基于刀具供应商推荐参数（{self.tool.tool_type}，{self.tool.tool_material}）")
        reasons.append(f"考虑材料特性（{self.material.material_name}，硬度{self.material.hardness}HB）")
        reasons.append(f"考虑机床能力（{self.machine.machine_type}，最大功率{self.machine.max_spindle_power}kW）")
        reasons.append(f"应用安全系数：转速{self.safety_factors['speed']}，进给{self.safety_factors['feed']}，切深{self.safety_factors['cut_depth']}")
        
        return "；".join(reasons)
    
    def get_optimization_suggestions(self) -> Dict[str, str]:
        """
        获取优化建议
        
        Returns:
            优化建议字典
        """
        suggestions = {}
        
        # 转速建议
        if self.material.hardness > 300:
            suggestions["speed"] = "材料硬度较高，建议降低转速以提高刀具寿命"
        elif self.material.hardness < 150:
            suggestions["speed"] = "材料硬度较低，可适当提高转速以提高效率"
        
        # 进给建议
        if self.tool.tool_material == "硬质合金":
            suggestions["feed"] = "硬质合金刀具可承受较高进给，建议在推荐范围内选择较大值"
        else:
            suggestions["feed"] = "刀具材料较软，建议适当降低进给以保护刀具"
        
        # 切深建议
        if self.tool.tool_overhang > self.tool.diameter * 3:
            suggestions["cut_depth"] = "刀具悬伸较大，建议降低切深以避免振动"
        
        # 综合建议
        suggestions["general"] = (
            f"推荐优先优化材料去除率，同时确保刀具寿命不低于{self.tool.recommended_cut_depth_max * 0.5}分钟"
        )
        
        return suggestions