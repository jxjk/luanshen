"""
策略 API Schema
"""
from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    """创建策略请求"""
    name: str = Field(..., description="策略名称")
    type: str = Field(..., max_length=32, description="加工类型")
    rx_min: float = Field(..., description="最小侧面粗糙度 um")
    rz_min: float = Field(..., description="最小底面粗糙度 um")
    lft_min: float = Field(..., description="最小刀具寿命 min")
    ae: float = Field(..., description="切削宽度 mm")
    moSunXiShu: float = Field(None, description="刀具磨损系数")


class StrategyUpdate(BaseModel):
    """更新策略请求"""
    name: str = Field(None, description="策略名称")
    type: str = Field(None, max_length=32, description="加工类型")
    rx_min: float = Field(None, description="最小侧面粗糙度 um")
    rz_min: float = Field(None, description="最小底面粗糙度 um")
    lft_min: float = Field(None, description="最小刀具寿命 min")
    ae: float = Field(None, description="切削宽度 mm")
    moSunXiShu: float = Field(None, description="刀具磨损系数")


class StrategyResponse(BaseModel):
    """策略响应"""
    id: str = Field(..., description="策略ID")
    name: str = Field(..., description="策略名称")
    type: str = Field(..., description="加工类型")
    rx_min: float = Field(..., description="最小侧面粗糙度 um")
    rz_min: float = Field(..., description="最小底面粗糙度 um")
    lft_min: float = Field(..., description="最小刀具寿命 min")
    ae: float = Field(..., description="切削宽度 mm")
    moSunXiShu: float = Field(None, description="刀具磨损系数")