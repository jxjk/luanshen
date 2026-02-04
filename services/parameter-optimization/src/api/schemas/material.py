"""
材料 API Schema
"""
from pydantic import BaseModel, Field


class MaterialCreate(BaseModel):
    """创建材料请求"""
    id: str = Field(..., min_length=1, max_length=3, description="材料ID")
    caiLiaoZu: str = Field(..., min_length=1, max_length=3, description="材料组")
    name: str = Field(..., description="材料名称")
    rm_min: int = Field(None, description="最小强度")
    rm_max: int = Field(None, description="最大强度")
    kc11: int = Field(None, description="单位切削力")
    mc: float = Field(None, description="坡度值")


class MaterialUpdate(BaseModel):
    """更新材料请求"""
    name: str = Field(None, description="材料名称")
    rm_min: int = Field(None, description="最小强度")
    rm_max: int = Field(None, description="最大强度")
    kc11: int = Field(None, description="单位切削力")
    mc: float = Field(None, description="坡度值")


class MaterialResponse(BaseModel):
    """材料响应"""
    id: str = Field(..., description="材料ID")
    caiLiaoZu: str = Field(..., description="材料组")
    name: str = Field(..., description="材料名称")
    rm_min: int = Field(None, description="最小强度")
    rm_max: int = Field(None, description="最大强度")
    kc11: int = Field(None, description="单位切削力")
    mc: float = Field(None, description="坡度值")