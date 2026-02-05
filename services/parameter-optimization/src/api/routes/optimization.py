"""
参数优化 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from ...config.database import get_db
from ...config.constants import MachiningMethod
from ...repositories import (
    MaterialRepository,
    ToolRepository,
    MachineRepository,
    StrategyRepository
)
from ...algorithms import MicrobialGeneticAlgorithm, GAConfig, OptimizationConstraints
from ..schemas.optimization import OptimizationRequest, OptimizationResponse, OptimizationResult
from ..schemas.material import MaterialResponse
from ..schemas.tool import ToolResponse
from ..schemas.machine import MachineResponse
from ..schemas.strategy import StrategyResponse

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(tags=["参数优化"])

# 中文到英文的加工类型映射
MACHINING_TYPE_MAP = {
    "铣削": MachiningMethod.MILLING,
    "钻孔": MachiningMethod.DRILLING,
    "镗孔": MachiningMethod.BORING,
    "车削": MachiningMethod.TURNING,
    "milling": MachiningMethod.MILLING,
    "drilling": MachiningMethod.DRILLING,
    "boring": MachiningMethod.BORING,
    "turning": MachiningMethod.TURNING,
}


@router.post("/optimize", response_model=OptimizationResponse, status_code=status.HTTP_200_OK)
async def optimize_parameters(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    优化切削参数
    
    基于微生物遗传算法，在满足所有约束条件的前提下，最大化材料去除率。
    
    - **material_id**: 材料ID（如 P1, M1, K1 等）
    - **tool_id**: 刀具ID
    - **machine_id**: 设备ID
    - **strategy_id**: 策略ID
    """
    # 获取材料
    material_repo = MaterialRepository(db)
    material = material_repo.get_by_group(request.material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"材料 {request.material_id} 不存在"
        )
    
    # 获取刀具
    tool_repo = ToolRepository(db)
    tool = tool_repo.get(request.tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"刀具 {request.tool_id} 不存在"
        )
    
    # 获取设备
    machine_repo = MachineRepository(db)
    machine = machine_repo.get(request.machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {request.machine_id} 不存在"
        )
    
    # 获取策略
    strategy_repo = StrategyRepository(db)
    strategy = strategy_repo.get(request.strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略 {request.strategy_id} 不存在"
        )
    
    # 构建约束条件 - 使用正确的字段名（数据库模型字段名）
    # 映射加工类型（中文 → 英文）
    machining_method = MACHINING_TYPE_MAP.get(strategy.type, MachiningMethod.MILLING)

    # 计算合理的切宽：最大为刀具直径，但不超过策略中的ae
    max_cut_width = min(tool.zhi_jing, strategy.ae)
    
    constraints = OptimizationConstraints(
        min_tool_life=strategy.lft_min,
        max_power=machine.pw_max,
        max_torque=machine.tnm_max,
        max_feed_force=tool.ff_max or 0,
        min_surface_roughness=min(strategy.rx_min, strategy.rz_min),

        tool_diameter=tool.zhi_jing,
        tool_teeth=tool.chi_shu,
        tool_radius=tool.dao_jian_r,
        main_cutting_angle=tool.zhu_pian_jiao,
        rake_angle=tool.qian_jiao,
        cut_width=max_cut_width,  # 使用合理的切宽

        tool_life_coefficient=tool.ct,
        speed_coefficient=tool.s_xi_shu,
        feed_coefficient=tool.f_xi_shu,
        cut_depth_coefficient=tool.ap_xi_shu,

        material_coefficient=material.kc11,
        material_slope=material.mc,

        machine_efficiency=machine.xiao_lv,
        machining_method=machining_method,
        wear_coefficient=strategy.mo_sun_xi_shu,

        # 刀具挠度参数
        tool_elastic_modulus=tool.elastic_modulus if tool.elastic_modulus else 630000.0,
        tool_overhang_length=tool.overhang_length if tool.overhang_length else 40.0,
        max_tool_deflection=1.0,  # 最大允许挠度 1.0mm（粗加工）

        max_feed_per_tooth=tool.fz_max,
        max_cutting_speed=tool.vc_max,
        max_cut_depth=min(tool.ap_max, tool.zhi_jing)  # 最大切深不超过刀具直径
    )
    
    # 构建算法配置
    config = GAConfig(
        population_size=request.population_size or 10240,
        generations=request.generations or 200,
        crossover_rate=request.crossover_rate or 0.6,
        mutation_rate=request.mutation_rate or 0.3,
        speed_bound=(0, machine.rp_max),
        feed_bound=(0, machine.f_max),
        cut_depth_bound=(0.0, tool.ap_max)
    )
    
    # 执行优化
    try:
        logger.info(f"开始优化: material_id={request.material_id}, tool_id={request.tool_id}, "
                   f"machine_id={request.machine_id}, strategy_id={request.strategy_id}")
        
        ga = MicrobialGeneticAlgorithm(config=config, constraints=constraints)
        result_params, fitness = ga.evolve()
        
        logger.info(f"优化完成: fitness={fitness:.6f}, "
                   f"speed={result_params['speed']:.2f}, feed={result_params['feed']:.2f}")

        # 构建响应
        result = OptimizationResult(
            speed=round(result_params["speed"], 2),
            feed=round(result_params["feed"], 2),
            cut_depth=round(result_params["cut_depth"], 2),
            cut_width=round(result_params["cut_width"], 2),
            cutting_speed=round(result_params["cutting_speed"], 2),
            feed_per_tooth=round(result_params["feed_per_tooth"], 4),
            bottom_roughness=round(result_params["bottom_roughness"], 2),
            side_roughness=round(result_params["side_roughness"], 2),
            power=round(result_params["power"], 2),
            torque=round(result_params["torque"], 2),
            feed_force=round(result_params["feed_force"], 2),
            material_removal_rate=round(result_params["material_removal_rate"], 2),
            tool_life=round(result_params["tool_life"], 2),
            fitness=round(fitness, 6)
        )

        return OptimizationResponse(
            success=True,
            message="优化成功",
            result=result
        )

    except Exception as e:
        import traceback
        error_detail = f"优化失败: {str(e)}\n\n详细错误:\n{traceback.format_exc()}"
        logger.error(f"优化失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/ai-optimize", status_code=status.HTTP_200_OK)
async def ai_assisted_optimize(
    request: OptimizationRequest,
    enable_ai_planning: bool = True,
    enable_ai_review: bool = True,
    enable_llm: bool = True,
    db: Session = Depends(get_db)
):
    """
    AI 辅助参数优化（新增）
    
    集成 AI 规划器、AI 审查器和 LLM 的智能优化流程：
    1. AI 规划：基于刀具供应商参数、材料特性和机床能力，智能设定参数搜索范围
    2. 遗传算法优化：在规划的搜索范围内执行优化
    3. AI 审查：验证优化结果的物理合理性和安全性
    4. LLM 增强：使用 DeepSeek 大模型生成智能优化建议和审查分析（可选）
    
    - **material_id**: 材料ID（如 P1, M1, K1 等）
    - **tool_id**: 刀具ID
    - **machine_id**: 设备ID
    - **strategy_id**: 策略ID
    - **enable_ai_planning**: 是否启用 AI 规划（默认 True）
    - **enable_ai_review**: 是否启用 AI 审查（默认 True）
    - **enable_llm**: 是否启用 LLM 增强（默认 True，需要配置 DEEPSEEK_API_KEY）
    """
    from ...algorithms.ai_assisted_optimizer import (
        AIAssistedOptimizer, 
        OptimizationRequest as AIOptimizationRequest
    )
    
    # 获取材料
    material_repo = MaterialRepository(db)
    material = material_repo.get_by_group(request.material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"材料 {request.material_id} 不存在"
        )
    
    # 获取刀具
    tool_repo = ToolRepository(db)
    tool = tool_repo.get(request.tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"刀具 {request.tool_id} 不存在"
        )
    
    # 获取设备
    machine_repo = MachineRepository(db)
    machine = machine_repo.get(request.machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {request.machine_id} 不存在"
        )
    
    # 获取策略
    strategy_repo = StrategyRepository(db)
    strategy = strategy_repo.get(request.strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略 {request.strategy_id} 不存在"
        )
    
    # 映射加工类型
    machining_method = MACHINING_TYPE_MAP.get(strategy.type, MachiningMethod.MILLING)
    
    try:
        logger.info(f"开始 AI 辅助优化: material_id={request.material_id}, tool_id={request.tool_id}, "
                   f"machine_id={request.machine_id}, strategy_id={request.strategy_id}")
        
        # 构建 AI 优化请求
        ai_request = AIOptimizationRequest(
            # 刀具参数
            tool_type=tool.type,
            tool_material=tool.material,
            coating=tool.coating or "无",
            tool_diameter=tool.zhi_jing,
            tool_teeth=tool.chi_shu,
            
            # 刀具供应商推荐参数
            recommended_speed_min=tool.vc_min * 318.0 / tool.zhi_jing if tool.vc_min > 0 else 100,
            recommended_speed_max=tool.vc_max * 318.0 / tool.zhi_jing if tool.vc_max > 0 else machine.rp_max,
            recommended_feed_min=tool.fz_min * tool.chi_shu * (tool.vc_min * 318.0 / tool.zhi_jing) if tool.fz_min > 0 else 10,
            recommended_feed_max=tool.fz_max * tool.chi_shu * (tool.vc_max * 318.0 / tool.zhi_jing) if tool.fz_max > 0 else machine.f_max,
            recommended_cut_depth_max=tool.ap_max,
            recommended_cut_width_max=strategy.ae,
            
            # 刀具物理参数
            tool_stiffness=tool.du_gang_du or 500.0,
            tool_overhang=tool.xuan_shen or 50.0,
            max_cutting_speed=tool.vc_max,
            max_feed_per_tooth=tool.fz_max,
            
            # 材料参数
            material_id=material.group,
            material_name=material.name,
            material_group=material.group,
            hardness=material.hardness,
            tensile_strength=material.tensile_strength,
            machinability=material.machinability or 0.8,
            cutting_force_coefficient=material.kc11,
            
            # 机床参数
            machine_type=machine.type,
            max_spindle_speed=machine.rp_max,
            max_spindle_power=machine.pw_max,
            max_spindle_torque=machine.tnm_max,
            max_feed_rate=machine.f_max,
            max_feed_force=tool.ff_max or 800.0,
            
            # 加工参数
            machining_method=machining_method,
            cut_width=strategy.ae,
            
            # 算法参数
            population_size=request.population_size or 10240,
            generations=request.generations or 200,
            crossover_rate=request.crossover_rate or 0.6,
            mutation_rate=request.mutation_rate or 0.3
        )
        
        # 执行 AI 辅助优化
        optimizer = AIAssistedOptimizer()
        response = optimizer.optimize(
            ai_request,
            enable_ai_planning=enable_ai_planning,
            enable_ai_review=enable_ai_review,
            enable_llm=enable_llm
        )
        
        logger.info(f"AI 辅助优化完成: success={response.success}, "
                   f"safety_score={response.review_result.safety_score if response.review_result else 0:.1f}")
        
        # 构建响应
        result = OptimizationResult(
            speed=round(response.result["speed"], 2),
            feed=round(response.result["feed"], 2),
            cut_depth=round(response.result["cut_depth"], 2),
            cut_width=round(response.result["cut_width"], 2),
            cutting_speed=round(response.result["cutting_speed"], 2),
            feed_per_tooth=round(response.result["feed_per_tooth"], 4),
            bottom_roughness=round(response.result["bottom_roughness"], 2),
            side_roughness=round(response.result["side_roughness"], 2),
            power=round(response.result["power"], 2),
            torque=round(response.result["torque"], 2),
            feed_force=round(response.result["feed_force"], 2),
            material_removal_rate=round(response.result["material_removal_rate"], 2),
            tool_life=round(response.result["tool_life"], 2),
            fitness=round(response.result["fitness"], 6)
        )
        
        # 构建完整响应（包含 AI 信息）
        response_data = {
            "success": response.success,
            "message": response.message,
            "result": result,
        }
        
        # 添加 AI 规划信息
        if response.search_range:
            response_data["ai_planning"] = {
                "search_range": {
                    "speed": response.search_range.speed_range,
                    "feed": response.search_range.feed_range,
                    "cut_depth": response.search_range.cut_depth_range,
                    "cut_width": response.search_range.cut_width_range,
                },
                "reason": response.search_range.reason,
                "safety_factor": response.search_range.safety_factor,
                "suggestions": response.planner_suggestions
            }
        
        # 添加 AI 审查信息
        if response.review_result:
            response_data["ai_review"] = {
                "passed": response.review_result.passed,
                "safety_score": response.review_result.safety_score,
                "overall_assessment": response.review_result.overall_assessment,
                "summary": {
                    "total": response.review_result.total_items,
                    "safe": response.review_result.safe_count,
                    "warning": response.review_result.warning_count,
                    "error": response.review_result.error_count,
                    "critical": response.review_result.critical_count
                },
                "items": [
                    {
                        "name": item.item_name,
                        "current": item.current_value,
                        "limit": item.limit_value,
                        "severity": item.severity.value,
                        "message": item.message,
                        "recommendation": item.recommendation
                    }
                    for item in response.review_result.items
                ]
            }
        
        # 添加 LLM 分析信息（如果存在）
        if response.review_result and hasattr(response.review_result, 'llm_analysis'):
            response_data["ai_review"]["llm_analysis"] = response.review_result.llm_analysis
        
        return response_data

    except Exception as e:
        import traceback
        error_detail = f"AI 辅助优化失败: {str(e)}\n\n详细错误:\n{traceback.format_exc()}"
        logger.error(f"AI 辅助优化失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/health", status_code=status.HTTP_200_OK)
@router.head("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "parameter-optimization"}