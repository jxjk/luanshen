"""
优化相关 API Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class OptimizationRequest(BaseModel):
    """优化请求"""
    material_id: str = Field(..., description="材料ID")
    tool_id: str = Field(..., description="刀具ID")
    machine_id: str = Field(..., description="设备ID")
    strategy_id: str = Field(..., description="策略ID")
    
    # 可选的算法参数覆盖
    population_size: Optional[int] = Field(None, ge=100, le=100000, description="种群大小")
    generations: Optional[int] = Field(None, ge=10, le=1000, description="迭代次数")
    crossover_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="交叉概率")
    mutation_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="变异概率")
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_id": "P1",
                "tool_id": "1",
                "machine_id": "1",
                "strategy_id": "1",
                "population_size": 10240,
                "generations": 200,
                "crossover_rate": 0.6,
                "mutation_rate": 0.3
            }
        }


class OptimizationResult(BaseModel):
    """优化结果"""
    # 优化参数
    speed: float = Field(..., description="转速 r/min")
    feed: float = Field(..., description="进给量 mm/min")
    cut_depth: float = Field(..., description="切深 mm")
    cut_width: float = Field(..., description="切宽 mm")
    
    # 计算参数
    cutting_speed: float = Field(..., description="线速度 m/min")
    feed_per_tooth: float = Field(..., description="每齿进给 mm")
    bottom_roughness: float = Field(..., description="底面粗糙度 um")
    side_roughness: float = Field(..., description="侧面粗糙度 um")
    power: float = Field(..., description="功率 Kw")
    torque: float = Field(..., description="扭矩 Nm")
    feed_force: float = Field(..., description="进给力 N")
    material_removal_rate: float = Field(..., description="材料去除率 cm³/min")
    tool_life: float = Field(..., description="刀具寿命 min")
    
    # 适应度
    fitness: float = Field(..., description="适应度值")


class OptimizationResponse(BaseModel):
    """优化响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    result: Optional[OptimizationResult] = Field(None, description="优化结果")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "优化成功",
                "result": {
                    "speed": 5000.0,
                    "feed": 3000.0,
                    "cut_depth": 0.5,
                    "cut_width": 8.5,
                    "cutting_speed": 157.0,
                    "feed_per_tooth": 0.15,
                    "bottom_roughness": 1.8,
                    "side_roughness": 2.1,
                    "power": 3.2,
                    "torque": 6.1,
                    "feed_force": 0.0,
                    "material_removal_rate": 63.75,
                    "tool_life": 45.2,
                    "fitness": 63.75
                }
            }
        }