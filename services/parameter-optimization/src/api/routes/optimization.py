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
        cut_width=strategy.ae,

        tool_life_coefficient=tool.ct,
        speed_coefficient=tool.s_xi_shu,
        feed_coefficient=tool.f_xi_shu,
        cut_depth_coefficient=tool.ap_xi_shu,

        material_coefficient=material.kc11,
        material_slope=material.mc,

        machine_efficiency=machine.xiao_lv,
        machining_method=machining_method,
        wear_coefficient=strategy.mo_sun_xi_shu,

        max_feed_per_tooth=tool.fz_max,
        max_cutting_speed=tool.vc_max,
        max_cut_depth=tool.ap_max
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


@router.get("/health", status_code=status.HTTP_200_OK)
@router.head("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "parameter-optimization"}