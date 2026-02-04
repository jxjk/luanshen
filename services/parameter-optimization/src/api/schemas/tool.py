"""
刀具 API Schema
"""
from pydantic import BaseModel, Field


class ToolCreate(BaseModel):
    """创建刀具请求"""
    name: str = Field(..., description="刀具名称")
    type: str = Field(..., max_length=8, description="刀具类型")
    zhiJing: float = Field(..., description="刀具直径 mm")
    chiShu: int = Field(..., description="刀具齿数")
    vc_max: float = Field(..., description="最大线速度 m/min")
    fz_max: float = Field(..., description="最大每齿进给量 mm")
    ct: float = Field(..., description="刀具耐用度系数")
    s_xiShu: float = Field(..., description="转速系数")
    f_xiShu: float = Field(..., description="进给系数")
    ap_xiShu: float = Field(..., description="切深系数")
    ap_max: float = Field(None, description="最大切深 mm")
    ff_max: int = Field(None, description="最大进给力 N")
    daoJianR: float = Field(..., description="刀尖半径 mm")
    zhuPianJiao: float = Field(..., description="主偏角")
    qianJiao: float = Field(..., description="前角")


class ToolUpdate(BaseModel):
    """更新刀具请求"""
    name: str = Field(None, description="刀具名称")
    type: str = Field(None, max_length=8, description="刀具类型")
    zhiJing: float = Field(None, description="刀具直径 mm")
    chiShu: int = Field(None, description="刀具齿数")
    vc_max: float = Field(None, description="最大线速度 m/min")
    fz_max: float = Field(None, description="最大每齿进给量 mm")
    ct: float = Field(None, description="刀具耐用度系数")
    s_xiShu: float = Field(None, description="转速系数")
    f_xiShu: float = Field(None, description="进给系数")
    ap_xiShu: float = Field(None, description="切深系数")
    ap_max: float = Field(None, description="最大切深 mm")
    ff_max: int = Field(None, description="最大进给力 N")
    daoJianR: float = Field(None, description="刀尖半径 mm")
    zhuPianJiao: float = Field(None, description="主偏角")
    qianJiao: float = Field(None, description="前角")


class ToolResponse(BaseModel):
    """刀具响应"""
    id: str = Field(..., description="刀具ID")
    name: str = Field(..., description="刀具名称")
    type: str = Field(..., description="刀具类型")
    zhiJing: float = Field(..., description="刀具直径 mm")
    chiShu: int = Field(..., description="刀具齿数")
    vc_max: float = Field(..., description="最大线速度 m/min")
    fz_max: float = Field(..., description="最大每齿进给量 mm")
    ct: float = Field(..., description="刀具耐用度系数")
    s_xiShu: float = Field(..., description="转速系数")
    f_xiShu: float = Field(..., description="进给系数")
    ap_xiShu: float = Field(..., description="切深系数")
    ap_max: float = Field(None, description="最大切深 mm")
    ff_max: int = Field(None, description="最大进给力 N")
    daoJianR: float = Field(..., description="刀尖半径 mm")
    zhuPianJiao: float = Field(..., description="主偏角")
    qianJiao: float = Field(..., description="前角")