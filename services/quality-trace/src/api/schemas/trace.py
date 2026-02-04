"""
质量追溯相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QualityGradeEnum(str, Enum):
    """质量等级枚举"""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    REJECTED = "REJECTED"


class TraceRecordResponse(BaseModel):
    """追溯记录响应"""
    id: int
    workpiece_id: str
    workpiece_name: Optional[str] = None
    production_order_id: Optional[str] = None
    material_id: Optional[str] = None
    tool_id: Optional[int] = None
    machine_id: Optional[int] = None
    strategy_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration: Optional[int] = None
    nc_program_path: Optional[str] = None
    operator: Optional[str] = None
    quality_grade: Optional[QualityGradeEnum] = None
    inspection_result: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TraceRecordCreateRequest(BaseModel):
    """创建追溯记录请求"""
    workpiece_id: str = Field(..., description="工件ID", max_length=100)
    workpiece_name: Optional[str] = Field(None, description="工件名称", max_length=255)
    production_order_id: Optional[str] = Field(None, description="生产订单ID", max_length=50)
    material_id: Optional[str] = Field(None, description="材料ID", max_length=50)
    tool_id: Optional[int] = Field(None, description="刀具ID")
    machine_id: Optional[int] = Field(None, description="设备ID")
    strategy_id: Optional[int] = Field(None, description="策略ID")
    nc_program_path: Optional[str] = Field(None, description="NC程序路径", max_length=500)
    operator: Optional[str] = Field(None, description="操作员", max_length=50)


class TraceRecordUpdateRequest(BaseModel):
    """更新追溯记录请求"""
    workpiece_name: Optional[str] = Field(None, max_length=255)
    end_time: Optional[datetime] = None
    operator: Optional[str] = Field(None, max_length=50)
    quality_grade: Optional[QualityGradeEnum] = None
    inspection_result: Optional[str] = None


class ParameterDataPoint(BaseModel):
    """参数数据点"""
    parameter_name: str = Field(..., description="参数名称")
    parameter_value: float = Field(..., description="参数值")
    timestamp: Optional[datetime] = None


class AppendParameterRequest(BaseModel):
    """追加参数数据请求"""
    trace_record_id: int = Field(..., description="追溯记录ID")
    parameters: List[ParameterDataPoint] = Field(..., description="参数数据列表")


class TimelineResponse(BaseModel):
    """时间轴响应"""
    trace_record: TraceRecordResponse
    parameters: List[Dict[str, Any]]
    summary: Dict[str, Any]
    statistics: Dict[str, Any]


class CorrelationAnalysisRequest(BaseModel):
    """关联分析请求"""
    workpiece_id: str = Field(..., description="工件ID")
    parameter_name: str = Field(..., description="参数名称")
    threshold: Optional[float] = Field(None, description="阈值")


class CorrelationAnalysisResponse(BaseModel):
    """关联分析响应"""
    workpiece_id: str
    parameter_name: str
    anomalies: List[Dict[str, Any]]
    correlation_coefficients: Dict[str, float]
    insights: List[str]