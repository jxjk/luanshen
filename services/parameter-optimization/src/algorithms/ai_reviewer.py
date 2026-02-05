"""
AI 审查器模块
验证优化结果的物理合理性和安全性
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class ReviewSeverity(Enum):
    """审查严重程度"""
    SAFE = "safe"  # 安全，通过
    WARNING = "warning"  # 警告，需要关注
    ERROR = "error"  # 错误，必须修正
    CRITICAL = "critical"  # 严重错误，禁止使用


@dataclass
class ReviewItem:
    """审查项"""
    item_name: str  # 审查项名称
    current_value: float  # 当前值
    limit_value: float  # 限制值
    severity: ReviewSeverity  # 严重程度
    message: str  # 审查意见
    recommendation: str  # 改进建议


@dataclass
class ReviewResult:
    """审查结果"""
    passed: bool  # 是否通过审查
    total_items: int  # 总审查项数
    safe_count: int  # 安全项数
    warning_count: int  # 警告项数
    error_count: int  # 错误项数
    critical_count: int  # 严重错误项数
    items: List[ReviewItem]  # 审查项列表
    overall_assessment: str  # 总体评估
    safety_score: float  # 安全评分 (0-100)


class AIReviewer:
    """AI 审查器 - 验证优化结果的物理合理性"""
    
    def __init__(
        self,
        tool_params,
        material_props,
        machine_caps
    ):
        """
        初始化 AI 审查器
        
        Args:
            tool_params: 刀具参数
            material_props: 材料特性
            machine_caps: 机床能力
        """
        self.tool = tool_params
        self.material = material_props
        self.machine = machine_caps
        
        # 安全阈值配置
        self.safety_thresholds = {
            "power": 0.85,  # 功率使用率不超过 85%
            "torque": 0.85,  # 扭矩使用率不超过 85%
            "feed_force": 0.85,  # 进给力使用率不超过 85%
            "tool_life": 1.2,  # 刀具寿命不低于推荐值的 1.2 倍
            "surface_roughness": 1.1,  # 表面粗糙度不超过要求值的 1.1 倍
        }
    
    def review_optimization_result(
        self, 
        params: Dict[str, float]
    ) -> ReviewResult:
        """
        审查优化结果
        
        Args:
            params: 优化参数字典
            
        Returns:
            审查结果对象
        """
        items = []
        
        # 1. 刀具强度审查
        items.extend(self._review_tool_strength(params))
        
        # 2. 机床能力审查
        items.extend(self._review_machine_capacity(params))
        
        # 3. 材料适应性审查
        items.extend(self._review_material_adaptability(params))
        
        # 4. 刀具供应商参数审查
        items.extend(self._review_vendor_params(params))
        
        # 5. 安全性审查
        items.extend(self._review_safety(params))
        
        # 统计结果
        safe_count = sum(1 for item in items if item.severity == ReviewSeverity.SAFE)
        warning_count = sum(1 for item in items if item.severity == ReviewSeverity.WARNING)
        error_count = sum(1 for item in items if item.severity == ReviewSeverity.ERROR)
        critical_count = sum(1 for item in items if item.severity == ReviewSeverity.CRITICAL)
        
        # 判断是否通过
        passed = (error_count == 0) and (critical_count == 0)
        
        # 计算安全评分
        safety_score = self._calculate_safety_score(items)
        
        # 生成总体评估
        overall_assessment = self._generate_overall_assessment(
            safe_count, warning_count, error_count, critical_count
        )
        
        return ReviewResult(
            passed=passed,
            total_items=len(items),
            safe_count=safe_count,
            warning_count=warning_count,
            error_count=error_count,
            critical_count=critical_count,
            items=items,
            overall_assessment=overall_assessment,
            safety_score=safety_score
        )
    
    def _review_tool_strength(self, params: Dict[str, float]) -> List[ReviewItem]:
        """审查刀具强度"""
        items = []
        
        # 切削力审查
        cutting_force = self._calculate_cutting_force(params)
        max_tool_force = self._calculate_max_tool_force()
        
        force_ratio = cutting_force / max_tool_force
        
        if force_ratio > 1.0:
            severity = ReviewSeverity.CRITICAL
            message = f"切削力 {cutting_force:.2f}N 超过刀具最大承受力 {max_tool_force:.2f}N"
            recommendation = "立即降低进给量或切深，避免刀具断裂"
        elif force_ratio > 0.9:
            severity = ReviewSeverity.ERROR
            message = f"切削力 {cutting_force:.2f}N 接近刀具极限 {max_tool_force:.2f}N（使用率 {force_ratio*100:.1f}%）"
            recommendation = "建议降低进给量或切深，保留安全裕度"
        elif force_ratio > 0.75:
            severity = ReviewSeverity.WARNING
            message = f"切削力 {cutting_force:.2f}N 较高（使用率 {force_ratio*100:.1f}%）"
            recommendation = "建议监控刀具磨损情况，定期检查"
        else:
            severity = ReviewSeverity.SAFE
            message = f"切削力 {cutting_force:.2f}N 在安全范围内（使用率 {force_ratio*100:.1f}%）"
            recommendation = "参数合理，可正常使用"
        
        items.append(ReviewItem(
            item_name="刀具强度",
            current_value=cutting_force,
            limit_value=max_tool_force,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        # 刀具变形审查
        deflection = self._calculate_tool_deflection(params)
        max_deflection = 0.1  # 最大允许变形 0.1mm
        
        if deflection > max_deflection:
            severity = ReviewSeverity.ERROR
            message = f"刀具变形 {deflection*1000:.3f}μm 超过允许值 {max_deflection*1000:.3f}μm"
            recommendation = "建议降低切深或增加刀具刚度（减少悬伸）"
        elif deflection > max_deflection * 0.8:
            severity = ReviewSeverity.WARNING
            message = f"刀具变形 {deflection*1000:.3f}μm 较大"
            recommendation = "可能影响加工精度，建议降低切深"
        else:
            severity = ReviewSeverity.SAFE
            message = f"刀具变形 {deflection*1000:.3f}μm 在允许范围内"
            recommendation = "刀具刚度充足"
        
        items.append(ReviewItem(
            item_name="刀具变形",
            current_value=deflection,
            limit_value=max_deflection,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        return items
    
    def _review_machine_capacity(self, params: Dict[str, float]) -> List[ReviewItem]:
        """审查机床能力"""
        items = []
        
        # 功率审查
        power_usage = params.get("power", 0)
        power_ratio = power_usage / self.machine.max_spindle_power
        threshold = self.safety_thresholds["power"]
        
        if power_ratio > 1.0:
            severity = ReviewSeverity.CRITICAL
            message = f"功率 {power_usage:.2f}kW 超过机床最大功率 {self.machine.max_spindle_power:.2f}kW"
            recommendation = "必须降低切削参数，避免机床过载"
        elif power_ratio > threshold:
            severity = ReviewSeverity.ERROR
            message = f"功率使用率 {power_ratio*100:.1f}% 超过安全阈值 {threshold*100:.0f}%"
            recommendation = f"建议降低切削参数，使功率使用率控制在 {threshold*100:.0f}% 以下"
        elif power_ratio > threshold * 0.9:
            severity = ReviewSeverity.WARNING
            message = f"功率使用率 {power_ratio*100:.1f}% 接近安全阈值"
            recommendation = "建议监控机床负载，避免长时间高负荷运行"
        else:
            severity = ReviewSeverity.SAFE
            message = f"功率使用率 {power_ratio*100:.1f}% 在安全范围内"
            recommendation = "功率使用合理"
        
        items.append(ReviewItem(
            item_name="机床功率",
            current_value=power_usage,
            limit_value=self.machine.max_spindle_power * threshold,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        # 扭矩审查
        torque_usage = params.get("torque", 0)
        torque_ratio = torque_usage / self.machine.max_spindle_torque
        threshold = self.safety_thresholds["torque"]
        
        if torque_ratio > 1.0:
            severity = ReviewSeverity.CRITICAL
            message = f"扭矩 {torque_usage:.2f}Nm 超过机床最大扭矩 {self.machine.max_spindle_torque:.2f}Nm"
            recommendation = "必须降低切削参数，避免机床过载"
        elif torque_ratio > threshold:
            severity = ReviewSeverity.ERROR
            message = f"扭矩使用率 {torque_ratio*100:.1f}% 超过安全阈值 {threshold*100:.0f}%"
            recommendation = f"建议降低切削参数，使扭矩使用率控制在 {threshold*100:.0f}% 以下"
        elif torque_ratio > threshold * 0.9:
            severity = ReviewSeverity.WARNING
            message = f"扭矩使用率 {torque_ratio*100:.1f}% 接近安全阈值"
            recommendation = "建议监控机床负载，避免长时间高负荷运行"
        else:
            severity = ReviewSeverity.SAFE
            message = f"扭矩使用率 {torque_ratio*100:.1f}% 在安全范围内"
            recommendation = "扭矩使用合理"
        
        items.append(ReviewItem(
            item_name="机床扭矩",
            current_value=torque_usage,
            limit_value=self.machine.max_spindle_torque * threshold,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        # 进给力审查
        feed_force = params.get("feed_force", 0)
        if feed_force > 0:  # 钻孔等有进给力的加工
            force_ratio = feed_force / self.machine.max_feed_force
            threshold = self.safety_thresholds["feed_force"]
            
            if force_ratio > 1.0:
                severity = ReviewSeverity.CRITICAL
                message = f"进给力 {feed_force:.2f}N 超过机床最大进给力 {self.machine.max_feed_force:.2f}N"
                recommendation = "必须降低进给速度，避免机床过载"
            elif force_ratio > threshold:
                severity = ReviewSeverity.ERROR
                message = f"进给力使用率 {force_ratio*100:.1f}% 超过安全阈值 {threshold*100:.0f}%"
                recommendation = f"建议降低进给速度，使进给力使用率控制在 {threshold*100:.0f}% 以下"
            else:
                severity = ReviewSeverity.SAFE
                message = f"进给力使用率 {force_ratio*100:.1f}% 在安全范围内"
                recommendation = "进给力使用合理"
            
            items.append(ReviewItem(
                item_name="机床进给力",
                current_value=feed_force,
                limit_value=self.machine.max_feed_force * threshold,
                severity=severity,
                message=message,
                recommendation=recommendation
            ))
        
        return items
    
    def _review_material_adaptability(self, params: Dict[str, float]) -> List[ReviewItem]:
        """审查材料适应性"""
        items = []
        
        # 切削速度审查
        cutting_speed = params.get("cutting_speed", 0)
        
        # 基于材料硬度推荐切削速度
        if self.material.hardness > 300:
            recommended_speed = 80  # 硬材料低速
        elif self.material.hardness > 200:
            recommended_speed = 120
        else:
            recommended_speed = 150  # 软材料高速
        
        speed_ratio = cutting_speed / recommended_speed
        
        if speed_ratio > 1.5:
            severity = ReviewSeverity.ERROR
            message = f"切削速度 {cutting_speed:.2f}m/min 远高于推荐值 {recommended_speed}m/min（材料硬度{self.material.hardness}HB）"
            recommendation = "建议降低转速，避免刀具过热和快速磨损"
        elif speed_ratio > 1.2:
            severity = ReviewSeverity.WARNING
            message = f"切削速度 {cutting_speed:.2f}m/min 高于推荐值 {recommended_speed}m/min"
            recommendation = "建议监控刀具温度，考虑使用冷却液"
        elif speed_ratio < 0.5:
            severity = ReviewSeverity.WARNING
            message = f"切削速度 {cutting_speed:.2f}m/min 低于推荐值 {recommended_speed}m/min"
            recommendation = "可适当提高转速以提高加工效率"
        else:
            severity = ReviewSeverity.SAFE
            message = f"切削速度 {cutting_speed:.2f}m/min 适合该材料"
            recommendation = "切削速度合理"
        
        items.append(ReviewItem(
            item_name="材料适应性",
            current_value=cutting_speed,
            limit_value=recommended_speed,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        return items
    
    def _review_vendor_params(self, params: Dict[str, float]) -> List[ReviewItem]:
        """审查刀具供应商参数"""
        items = []
        
        # 转速审查
        speed = params.get("speed", 0)
        if speed > self.tool.recommended_speed_max:
            severity = ReviewSeverity.ERROR
            message = f"转速 {speed:.2f}r/min 超过刀具供应商推荐最大值 {self.tool.recommended_speed_max:.2f}r/min"
            recommendation = "建议降低转速至供应商推荐范围内"
        elif speed < self.tool.recommended_speed_min:
            severity = ReviewSeverity.WARNING
            message = f"转速 {speed:.2f}r/min 低于刀具供应商推荐最小值 {self.tool.recommended_speed_min:.2f}r/min"
            recommendation = "可能影响加工效率，建议提高转速"
        else:
            severity = ReviewSeverity.SAFE
            message = f"转速 {speed:.2f}r/min 在刀具供应商推荐范围内"
            recommendation = "转速符合供应商推荐"
        
        items.append(ReviewItem(
            item_name="供应商转速",
            current_value=speed,
            limit_value=self.tool.recommended_speed_max,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        # 进给审查
        feed = params.get("feed", 0)
        if feed > self.tool.recommended_feed_max:
            severity = ReviewSeverity.ERROR
            message = f"进给 {feed:.2f}mm/min 超过刀具供应商推荐最大值 {self.tool.recommended_feed_max:.2f}mm/min"
            recommendation = "建议降低进给至供应商推荐范围内"
        elif feed < self.tool.recommended_feed_min:
            severity = ReviewSeverity.WARNING
            message = f"进给 {feed:.2f}mm/min 低于刀具供应商推荐最小值 {self.tool.recommended_feed_min:.2f}mm/min"
            recommendation = "可能影响加工效率，建议提高进给"
        else:
            severity = ReviewSeverity.SAFE
            message = f"进给 {feed:.2f}mm/min 在刀具供应商推荐范围内"
            recommendation = "进给符合供应商推荐"
        
        items.append(ReviewItem(
            item_name="供应商进给",
            current_value=feed,
            limit_value=self.tool.recommended_feed_max,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        # 切深审查
        cut_depth = params.get("cut_depth", 0)
        if cut_depth > self.tool.recommended_cut_depth_max:
            severity = ReviewSeverity.ERROR
            message = f"切深 {cut_depth:.2f}mm 超过刀具供应商推荐最大值 {self.tool.recommended_cut_depth_max:.2f}mm"
            recommendation = "建议降低切深至供应商推荐范围内"
        else:
            severity = ReviewSeverity.SAFE
            message = f"切深 {cut_depth:.2f}mm 在刀具供应商推荐范围内"
            recommendation = "切深符合供应商推荐"
        
        items.append(ReviewItem(
            item_name="供应商切深",
            current_value=cut_depth,
            limit_value=self.tool.recommended_cut_depth_max,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        return items
    
    def _review_safety(self, params: Dict[str, float]) -> List[ReviewItem]:
        """安全性审查"""
        items = []
        
        # 刀具寿命审查
        tool_life = params.get("tool_life", 0)
        min_life = 10  # 最小刀具寿命 10 分钟
        
        if tool_life < min_life:
            severity = ReviewSeverity.CRITICAL
            message = f"刀具寿命 {tool_life:.2f}min 过短，频繁换刀影响生产效率"
            recommendation = "必须降低切削参数以延长刀具寿命"
        elif tool_life < min_life * 2:
            severity = ReviewSeverity.ERROR
            message = f"刀具寿命 {tool_life:.2f}min 较短，换刀频繁"
            recommendation = "建议降低切削参数以提高刀具寿命"
        else:
            severity = ReviewSeverity.SAFE
            message = f"刀具寿命 {tool_life:.2f}min 合理"
            recommendation = "刀具寿命充足"
        
        items.append(ReviewItem(
            item_name="刀具寿命",
            current_value=tool_life,
            limit_value=min_life * 2,
            severity=severity,
            message=message,
            recommendation=recommendation
        ))
        
        return items
    
    def _calculate_cutting_force(self, params: Dict[str, float]) -> float:
        """计算切削力"""
        # 简化模型
        feed = params.get("feed", 0)
        cut_depth = params.get("cut_depth", 0)
        cut_width = params.get("cut_width", 0)
        
        # 基于材料切削力系数
        force = (
            self.material.cutting_force_coefficient * 
            cut_depth * cut_width * 
            (feed / 1000) ** 0.5
        )
        
        return force
    
    def _calculate_max_tool_force(self) -> float:
        """计算刀具最大承受力"""
        # 基于刀具刚度和变形限制
        max_force = self.tool.tool_stiffness * 0.1  # 变形不超过 0.1mm
        return max_force
    
    def _calculate_tool_deflection(self, params: Dict[str, float]) -> float:
        """计算刀具变形"""
        cutting_force = self._calculate_cutting_force(params)
        deflection = cutting_force / self.tool.tool_stiffness
        return deflection
    
    def _calculate_safety_score(self, items: List[ReviewItem]) -> float:
        """计算安全评分"""
        if not items:
            return 100.0
        
        total_score = 0.0
        for item in items:
            if item.severity == ReviewSeverity.SAFE:
                total_score += 100
            elif item.severity == ReviewSeverity.WARNING:
                total_score += 70
            elif item.severity == ReviewSeverity.ERROR:
                total_score += 30
            else:  # CRITICAL
                total_score += 0
        
        return total_score / len(items)
    
    def _generate_overall_assessment(
        self, 
        safe_count: int, 
        warning_count: int, 
        error_count: int, 
        critical_count: int
    ) -> str:
        """生成总体评估"""
        if critical_count > 0:
            return "严重错误：存在危及设备和人员安全的参数，必须立即修正"
        elif error_count > 0:
            return "存在错误：参数超出物理限制，需要调整后才能使用"
        elif warning_count > 3:
            return "多项警告：参数接近极限，建议优化以提高安全性"
        elif warning_count > 0:
            return "存在警告：参数基本合理，但有改进空间"
        else:
            return "参数安全：所有参数均在合理范围内，可以正常使用"