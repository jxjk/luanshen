"""
质量追溯 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ...config.database import get_db
from ...repositories.trace_repository import TraceRecordRepository
from ...services.analysis_service import AnalysisService
from ...api.schemas.trace import (
    TraceRecordResponse,
    TraceRecordCreateRequest,
    TraceRecordUpdateRequest,
    AppendParameterRequest,
    TimelineResponse,
    CorrelationAnalysisRequest,
    CorrelationAnalysisResponse,
)
from ...config.constants import APIMessage

router = APIRouter(prefix="/traces", tags=["质量追溯"])


@router.post("", response_model=TraceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_trace_record(
    request: TraceRecordCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建质量追溯记录
    """
    try:
        repo = TraceRecordRepository(db)
        
        # 检查工件ID是否已存在
        existing = repo.get_by_workpiece_id(request.workpiece_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=APIMessage.WORKPIECE_ALREADY_EXISTS
            )
        
        # 创建追溯记录
        record = repo.create(request.model_dump())
        
        return TraceRecordResponse.model_validate(record.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建追溯记录失败: {str(e)}"
        )


@router.get("", response_model=List[TraceRecordResponse])
async def get_trace_records(
    production_order_id: Optional[str] = Query(None, description="生产订单ID"),
    machine_id: Optional[int] = Query(None, description="设备ID"),
    quality_grade: Optional[str] = Query(None, description="质量等级"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取追溯记录列表
    """
    try:
        repo = TraceRecordRepository(db)
        
        # 转换枚举
        grade_enum = None
        if quality_grade:
            from ...models.trace_record import QualityGradeEnum
            grade_enum = QualityGradeEnum(quality_grade.upper())
        
        records = repo.get_all(
            production_order_id=production_order_id,
            machine_id=machine_id,
            quality_grade=grade_enum,
            start_time=start_time,
            end_time=end_time,
            skip=(page - 1) * page_size,
            limit=page_size
        )
        
        return [TraceRecordResponse.model_validate(record.to_dict()) for record in records]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取追溯记录列表失败: {str(e)}"
        )


@router.get("/{trace_id}", response_model=TraceRecordResponse)
async def get_trace_record(
    trace_id: int,
    db: Session = Depends(get_db)
):
    """
    获取追溯记录详情
    """
    try:
        repo = TraceRecordRepository(db)
        record = repo.get(trace_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.TRACE_NOT_FOUND
            )
        
        return TraceRecordResponse.model_validate(record.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取追溯记录详情失败: {str(e)}"
        )


@router.get("/workpiece/{workpiece_id}", response_model=TraceRecordResponse)
async def get_trace_by_workpiece(
    workpiece_id: str,
    db: Session = Depends(get_db)
):
    """
    根据工件ID获取追溯记录
    """
    try:
        repo = TraceRecordRepository(db)
        record = repo.get_by_workpiece_id(workpiece_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.TRACE_NOT_FOUND
            )
        
        return TraceRecordResponse.model_validate(record.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取追溯记录失败: {str(e)}"
        )


@router.put("/{trace_id}", response_model=TraceRecordResponse)
async def update_trace_record(
    trace_id: int,
    request: TraceRecordUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新追溯记录
    """
    try:
        repo = TraceRecordRepository(db)
        
        # 过滤None值
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        record = repo.update(trace_id, update_data)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.TRACE_NOT_FOUND
            )
        
        return TraceRecordResponse.model_validate(record.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新追溯记录失败: {str(e)}"
        )


@router.post("/{trace_id}/parameters")
async def append_parameters(
    trace_id: int,
    request: AppendParameterRequest,
    db: Session = Depends(get_db)
):
    """
    追加参数数据
    """
    try:
        repo = TraceRecordRepository(db)
        
        # 验证追溯记录存在
        record = repo.get(trace_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.TRACE_NOT_FOUND
            )
        
        # 追加参数
        count = repo.append_parameters(
            trace_id,
            [p.model_dump() for p in request.parameters]
        )
        
        return {
            "success": True,
            "message": f"成功追加 {count} 条参数数据",
            "count": count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"追加参数数据失败: {str(e)}"
        )


@router.get("/{trace_id}/timeline", response_model=TimelineResponse)
async def get_timeline(
    trace_id: int,
    db: Session = Depends(get_db)
):
    """
    获取时间轴数据
    """
    try:
        repo = TraceRecordRepository(db)
        
        # 获取时间轴数据
        timeline_data = repo.get_timeline(trace_id)
        
        if not timeline_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.TRACE_NOT_FOUND
            )
        
        # 获取统计信息
        statistics = repo.get_statistics(trace_id)
        
        return TimelineResponse(
            trace_record=TraceRecordResponse.model_validate(timeline_data["record"]),
            parameters=timeline_data["parameters"],
            summary={
                "total_parameters": statistics["total_parameters"],
                "parameter_count": statistics["parameter_count"],
            },
            statistics=statistics["parameter_statistics"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取时间轴数据失败: {str(e)}"
        )


@router.post("/analysis/correlation", response_model=CorrelationAnalysisResponse)
async def analyze_correlation(
    request: CorrelationAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    关联分析
    """
    try:
        repo = TraceRecordRepository(db)
        
        # 获取追溯记录
        record = repo.get_by_workpiece_id(request.workpiece_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.TRACE_NOT_FOUND
            )
        
        # 获取参数数据
        parameters = repo.get_parameters(record.id)
        
        # 按参数名分组
        parameter_data = {}
        for param in parameters:
            name = param.parameter_name
            value = float(param.parameter_value) if param.parameter_value else None
            if name not in parameter_data:
                parameter_data[name] = []
            if value is not None:
                parameter_data[name].append(value)
        
        # 检测异常
        target_data = parameter_data.get(request.parameter_name, [])
        anomalies = AnalysisService.detect_anomalies(
            target_data,
            threshold=request.threshold
        )
        
        # 计算相关性
        correlations = AnalysisService.analyze_parameter_correlation(parameter_data)
        
        # 生成洞察
        anomalies_dict = {request.parameter_name: anomalies}
        insights = AnalysisService.generate_insights(parameter_data, anomalies_dict)
        
        return CorrelationAnalysisResponse(
            workpiece_id=request.workpiece_id,
            parameter_name=request.parameter_name,
            anomalies=anomalies,
            correlation_coefficients=correlations.get(request.parameter_name, {}),
            insights=insights
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"关联分析失败: {str(e)}"
        )