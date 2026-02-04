"""
设备 API Schema
"""
from pydantic import BaseModel, Field


class MachineCreate(BaseModel):
    """创建设备请求"""
    id: str = Field(..., min_length=1, max_length=20, description="设备ID")
    name: str = Field(..., description="设备名称")
    type: str = Field(..., max_length=20, description="设备类型")
    pw_max: float = Field(..., description="最大功率 Kw")
    rp_max: float = Field(..., description="最大转速 r/min")
    tnm_max: float = Field(..., description="最大扭矩 Nm")
    xiaoLv: float = Field(..., description="机床效率")
    f_max: float = Field(..., description="最大进给量 mm/min")


class MachineUpdate(BaseModel):
    """更新设备请求"""
    name: str = Field(None, description="设备名称")
    type: str = Field(None, max_length=20, description="设备类型")
    model: str = Field(None, description="型号")
    pw_max: float = Field(None, description="最大功率 Kw")
    rp_max: float = Field(None, description="最大转速 r/min")
    tnm_max: float = Field(None, description="最大扭矩 Nm")
    xiaoLv: float = Field(None, description="机床效率")
    f_max: float = Field(None, description="最大进给量 mm/min")


class MachineResponse(BaseModel):
    """设备响应"""
    id: str = Field(..., description="设备ID")
    name: str = Field(..., description="设备名称")
    type: str = Field(..., description="设备类型")
    pw_max: float = Field(..., description="最大功率 Kw")
    rp_max: float = Field(..., description="最大转速 r/min")
    tnm_max: float = Field(..., description="最大扭矩 Nm")
    xiaoLv: float = Field(..., description="机床效率")
    f_max: float = Field(..., description="最大进给量 mm/min")