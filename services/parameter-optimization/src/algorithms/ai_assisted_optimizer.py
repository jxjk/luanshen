"""
AI 辅助优化器
集成 AI 规划器、优化算法和 AI 审查器的完整优化流程
"""
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from .ai_planner import AIPlanner, ToolVendorParams, MaterialProperties, MachineCapabilities, SearchRange
from .ai_reviewer import AIReviewer, ReviewResult
from .microbial_ga import MicrobialGeneticAlgorithm, GAConfig, OptimizationConstraints


class LLMIntegration:
    """LLM 集成器 - 用于生成智能建议"""
    
    def __init__(self):
        """初始化 LLM 集成器"""
        try:
            from ..services.llm_service import get_llm_service
            self.llm_service = get_llm_service()
            self.enabled = self.llm_service.enabled
        except ImportError:
            self.llm_service = None
            self.enabled = False
    
    async def generate_suggestions(self, context: Dict) -> Dict[str, str]:
        """生成优化建议"""
        if not self.enabled or self.llm_service is None:
            return {}
        return await self.llm_service.generate_optimization_suggestions(context)
    
    async def generate_review_analysis(self, params: Dict, review_result: Dict) -> str:
        """生成审查分析"""
        if not self.enabled or self.llm_service is None:
            return ""
        return await self.llm_service.generate_review_analysis(params, review_result)


@dataclass
class OptimizationRequest:
    """优化请求"""
    # 刀具参数
    tool_type: str
    tool_material: str
    coating: str
    tool_diameter: float
    tool_teeth: int
    
    # 刀具供应商推荐参数
    recommended_speed_min: float
    recommended_speed_max: float
    recommended_feed_min: float
    recommended_feed_max: float
    recommended_cut_depth_max: float
    recommended_cut_width_max: float
    
    # 刀具物理参数
    tool_stiffness: float
    tool_overhang: float
    max_cutting_speed: float
    max_feed_per_tooth: float
    
    # 材料参数
    material_id: str
    material_name: str
    material_group: str
    hardness: float
    tensile_strength: float
    machinability: float
    cutting_force_coefficient: float
    
    # 机床参数
    machine_type: str
    max_spindle_speed: float
    max_spindle_power: float
    max_spindle_torque: float
    max_feed_rate: float
    max_feed_force: float
    
    # 加工参数
    machining_method: str
    cut_width: float
    
    # 算法参数
    population_size: int = 10240
    generations: int = 200
    crossover_rate: float = 0.6
    mutation_rate: float = 0.3


@dataclass
class OptimizationResponse:
    """优化响应"""
    success: bool
    message: str
    
    # 优化结果
    result: Optional[Dict[str, float]] = None
    
    # AI 规划信息
    search_range: Optional[SearchRange] = None
    planner_suggestions: Optional[Dict[str, str]] = None
    
    # AI 审查结果
    review_result: Optional[ReviewResult] = None
    
    # 约束违规信息
    constraint_violations: Optional[list] = None


class AIAssistedOptimizer:
    """AI 辅助优化器 - 完整的智能优化流程"""
    
    def __init__(self):
        """初始化 AI 辅助优化器"""
        self.planner = None
        self.reviewer = None
        self.ga_optimizer = None
        self.llm_integration = LLMIntegration()
    
    def optimize(
        self, 
        request: OptimizationRequest,
        enable_ai_planning: bool = True,
        enable_ai_review: bool = True,
        enable_llm: bool = True
    ) -> OptimizationResponse:
        """
        执行 AI 辅助优化
        
        Args:
            request: 优化请求
            enable_ai_planning: 是否启用 AI 规划
            enable_ai_review: 是否启用 AI 审查
            
        Returns:
            优化响应
        """
        # 1. 构建参数对象
        tool_params = self._build_tool_params(request)
        material_props = self._build_material_props(request)
        machine_caps = self._build_machine_caps(request)
        
        # 2. AI 规划（设定搜索范围）
        search_range = None
        planner_suggestions = None
        
        if enable_ai_planning:
            self.planner = AIPlanner(tool_params, material_props, machine_caps)
            search_range = self.planner.plan_search_range(request.machining_method)
            planner_suggestions = self.planner.get_optimization_suggestions()
        
        # 3. 配置遗传算法
        ga_config = self._build_ga_config(request, search_range)
        constraints = self._build_constraints(request, tool_params, material_props)
        
        self.ga_optimizer = MicrobialGeneticAlgorithm(ga_config, constraints)
        
        # 4. 执行优化
        best_params, best_fitness = self.ga_optimizer.evolve()
        
        # 5. 计算完整加工参数
        result = self.ga_optimizer._calculate_machining_parameters(best_params)
        result["fitness"] = best_fitness
        
        # 6. AI 审查（验证结果）
        review_result = None
        
        if enable_ai_review:
            self.reviewer = AIReviewer(tool_params, material_props, machine_caps)
            review_result = self.reviewer.review_optimization_result(result)
        
        # 7. 检查约束违规
        constraint_checker = self._get_constraint_checker(constraints)
        passed, violations = constraint_checker.check_all(result)
        
        # 8. LLM 增强建议（如果启用）
        if enable_llm and self.llm_integration.enabled:
            logger.info(f"LLM 功能已启用，开始生成智能建议...")
            try:
                import asyncio
                # 生成 LLM 优化建议
                context = {
                    "material": {
                        "name": request.material_name,
                        "group": request.material_group,
                        "hardness": request.hardness,
                        "tensile_strength": request.tensile_strength,
                        "machinability": request.machinability
                    },
                    "tool": {
                        "type": request.tool_type,
                        "material": request.tool_material,
                        "coating": request.coating,
                        "diameter": request.tool_diameter,
                        "teeth": request.tool_teeth,
                        "overhang": request.tool_overhang
                    },
                    "machine": {
                        "type": request.machine_type,
                        "max_spindle_speed": request.max_spindle_speed,
                        "max_power": request.max_spindle_power,
                        "max_torque": request.max_spindle_torque
                    },
                    "result": result
                }
                
                llm_suggestions = asyncio.run(self.llm_integration.generate_suggestions(context))
                if llm_suggestions:
                    # 合并 LLM 建议到规划建议中
                    if planner_suggestions is None:
                        planner_suggestions = {}
                    planner_suggestions.update(llm_suggestions)
                
                # 生成 LLM 审查分析
                if review_result:
                    review_dict = {
                        "safety_score": review_result.safety_score,
                        "overall_assessment": review_result.overall_assessment,
                        "summary": {
                            "safe": review_result.safe_count,
                            "warning": review_result.warning_count,
                            "error": review_result.error_count,
                            "critical": review_result.critical_count
                        }
                    }
                    llm_review_analysis = asyncio.run(
                        self.llm_integration.generate_review_analysis(result, review_dict)
                    )
                    
                    logger.info(f"LLM 审查分析生成成功: {len(llm_review_analysis)} 字符")
                    
                    if llm_review_analysis:
                        # 将 LLM 分析添加到审查结果中
                        if not hasattr(review_result, 'llm_analysis'):
                            review_result.llm_analysis = llm_review_analysis
            except Exception as e:
                # LLM 调用失败不影响主流程
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"LLM 增强失败: {str(e)}")
        
        # 9. 构建响应
        response = OptimizationResponse(
            success=review_result.passed if review_result else passed,
            message=self._build_message(search_range, review_result, violations),
            result=result,
            search_range=search_range,
            planner_suggestions=planner_suggestions,
            review_result=review_result,
            constraint_violations=violations if not passed else None
        )
        
        return response
    
    def _build_tool_params(self, request: OptimizationRequest) -> ToolVendorParams:
        """构建刀具参数"""
        return ToolVendorParams(
            tool_type=request.tool_type,
            tool_material=request.tool_material,
            coating=request.coating,
            recommended_speed_min=request.recommended_speed_min,
            recommended_speed_max=request.recommended_speed_max,
            recommended_feed_min=request.recommended_feed_min,
            recommended_feed_max=request.recommended_feed_max,
            recommended_cut_depth_max=request.recommended_cut_depth_max,
            recommended_cut_width_max=request.recommended_cut_width_max,
            max_cutting_speed=request.max_cutting_speed,
            max_feed_per_tooth=request.max_feed_per_tooth,
            tool_stiffness=request.tool_stiffness,
            tool_overhang=request.tool_overhang,
            diameter=request.tool_diameter,
            teeth=request.tool_teeth,
            corner_radius=0.0,
            helix_angle=0.0,
            max_operating_temp=800.0,
            thermal_conductivity=50.0
        )
    
    def _build_material_props(self, request: OptimizationRequest) -> MaterialProperties:
        """构建材料特性"""
        return MaterialProperties(
            material_id=request.material_id,
            material_name=request.material_name,
            material_group=request.material_group,
            hardness=request.hardness,
            tensile_strength=request.tensile_strength,
            yield_strength=request.tensile_strength * 0.6,
            elongation=20.0,
            machinability=request.machinability,
            cutting_force_coefficient=request.cutting_force_coefficient,
            specific_cutting_energy=3.0,
            thermal_conductivity=50.0,
            specific_heat=500.0,
            melting_point=1500.0
        )
    
    def _build_machine_caps(self, request: OptimizationRequest) -> MachineCapabilities:
        """构建机床能力"""
        return MachineCapabilities(
            machine_type=request.machine_type,
            max_spindle_speed=request.max_spindle_speed,
            max_spindle_power=request.max_spindle_power,
            max_spindle_torque=request.max_spindle_torque,
            max_feed_rate=request.max_feed_rate,
            max_feed_force=request.max_feed_force,
            x_travel=500.0,
            y_travel=500.0,
            z_travel=500.0,
            positioning_accuracy=0.01,
            repeatability=0.005,
            spindle_stiffness=200.0,
            table_stiffness=300.0
        )
    
    def _build_ga_config(
        self, 
        request: OptimizationRequest, 
        search_range: Optional[SearchRange]
    ) -> GAConfig:
        """构建遗传算法配置"""
        # 如果有 AI 规划的搜索范围，使用规划范围
        if search_range:
            speed_bound = search_range.speed_range
            feed_bound = search_range.feed_range
            cut_depth_bound = search_range.cut_depth_range
        else:
            # 使用默认范围
            speed_bound = (0, request.recommended_speed_max)
            feed_bound = (0, request.recommended_feed_max)
            cut_depth_bound = (0, request.recommended_cut_depth_max)
        
        return GAConfig(
            population_size=request.population_size,
            generations=request.generations,
            crossover_rate=request.crossover_rate,
            mutation_rate=request.mutation_rate,
            speed_bound=speed_bound,
            feed_bound=feed_bound,
            cut_depth_bound=cut_depth_bound,
            enable_parallel=True
        )
    
    def _build_constraints(
        self, 
        request: OptimizationRequest,
        tool_params: ToolVendorParams,
        material_props: MaterialProperties
    ) -> OptimizationConstraints:
        """构建优化约束"""
        # 计算合理的切宽：最大为刀具直径
        max_cut_width = min(request.tool_diameter, request.cut_width)
        
        return OptimizationConstraints(
            # 约束值
            min_tool_life=10.0,
            max_power=request.max_spindle_power * 0.85,  # 85% 安全系数
            max_torque=request.max_spindle_torque * 0.85,
            max_feed_force=request.max_feed_force * 0.85,
            min_surface_roughness=3.2,
            
            # 工艺参数
            tool_diameter=request.tool_diameter,
            tool_teeth=request.tool_teeth,
            tool_radius=request.tool_diameter / 2,
            main_cutting_angle=31.0,
            rake_angle=0.0,
            cut_width=max_cut_width,  # 使用合理的切宽
            bottom_hole_diameter=22.5,
            turning_diameter=0.0,
            
            # 刀具耐用度系数
            tool_life_coefficient=100000.0,
            speed_coefficient=-1.5,
            feed_coefficient=0.75,
            cut_depth_coefficient=0.1,
            
            # 材料参数
            material_coefficient=request.cutting_force_coefficient,
            material_slope=0.21,
            
            # 机床参数
            machine_efficiency=0.85,
            
            # 加工方法
            machining_method=request.machining_method,
            
            # 刀具磨损系数
            wear_coefficient=1.0,
            
            # 最大参数限制
            max_feed_per_tooth=request.max_feed_per_tooth,
            max_cutting_speed=request.max_cutting_speed,
            max_cut_depth=min(request.recommended_cut_depth_max, request.tool_diameter)  # 最大切深不超过刀具直径
        )
    
    def _get_constraint_checker(self, constraints: OptimizationConstraints):
        """获取约束检查器"""
        from .constraints import ConstraintChecker
        constraints_dict = {
            'min_tool_life': constraints.min_tool_life,
            'max_power': constraints.max_power,
            'max_torque': constraints.max_torque,
            'max_feed_force': constraints.max_feed_force,
            'min_surface_roughness': constraints.min_surface_roughness,
            'max_feed_per_tooth': constraints.max_feed_per_tooth,
            'max_cutting_speed': constraints.max_cutting_speed,
        }
        return ConstraintChecker(constraints_dict)
    
    def _build_message(
        self, 
        search_range: Optional[SearchRange],
        review_result: Optional[ReviewResult],
        violations: Optional[list]
    ) -> str:
        """构建响应消息"""
        messages = []
        
        if search_range:
            messages.append(f"AI 规划已完成，搜索范围：{search_range.reason}")
        
        if review_result:
            messages.append(f"AI 审查评分：{review_result.safety_score:.1f}/100")
            messages.append(f"总体评估：{review_result.overall_assessment}")
            
            if review_result.warning_count > 0:
                messages.append(f"警告项：{review_result.warning_count} 个")
            
            if review_result.error_count > 0:
                messages.append(f"错误项：{review_result.error_count} 个")
        
        if violations:
            messages.append(f"约束违规：{len(violations)} 项")
        
        return "；".join(messages) if messages else "优化完成"