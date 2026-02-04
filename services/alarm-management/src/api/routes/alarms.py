"""
报警管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ...config.database import get_db
from ...repositories.alarm_repository import AlarmRepository
from ...notifiers.notification_service import NotificationService
from ...api.schemas.alarm import (
    AlarmResponse,
    AlarmCreateRequest,
    AlarmAcknowledgeRequest,
    AlarmResolveRequest,
    AlarmCloseRequest,
    AlarmQueryParams,
    AlarmStatisticsResponse,
    WSAlarmMessage,
)
from ...config.constants import APIMessage, AlarmStatusEnum

router = APIRouter(prefix="/alarms", tags=["报警管理"])


@router.post("", response_model=AlarmResponse, status_code=status.HTTP_201_CREATED)
async def create_alarm(
    request: AlarmCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建报警记录
    """
    try:
        repo = AlarmRepository(db)
        
        # 检查是否已存在相同的未解决报警
        existing = repo.get_by_code(request.device_id, request.alarm_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该设备已存在相同的未解决报警"
            )
        
        # 创建报警记录
        alarm = repo.create({
            "device_id": request.device_id,
            "alarm_level": request.alarm_level,
            "alarm_code": request.alarm_code,
            "alarm_message": request.alarm_message,
        })
        
        # 发送通知
        notification_service = NotificationService()
        await notification_service.send_alarm_notification({
            "device_id": alarm.device_id,
            "alarm_level": alarm.alarm_level.value,
            "alarm_code": alarm.alarm_code,
            "alarm_message": alarm.alarm_message,
            "created_at": alarm.created_at.isoformat(),
        })
        
        return AlarmResponse.model_validate(alarm.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建报警失败: {str(e)}"
        )


@router.get("", response_model=List[AlarmResponse])
async def get_alarms(
    device_id: Optional[int] = Query(None, description="设备ID"),
    alarm_level: Optional[str] = Query(None, description="报警级别"),
    status: Optional[str] = Query(None, description="报警状态"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取报警记录列表
    """
    try:
        repo = AlarmRepository(db)
        
        # 转换枚举
        alarm_level_enum = None
        if alarm_level:
            from ...models.alarm_record import AlarmLevelEnum
            alarm_level_enum = AlarmLevelEnum(alarm_level.upper())
        
        status_enum = None
        if status:
            status_enum = AlarmStatusEnum(status.upper())
        
        alarms = repo.get_all(
            device_id=device_id,
            alarm_level=alarm_level_enum,
            status=status_enum,
            start_time=start_time,
            end_time=end_time,
            skip=(page - 1) * page_size,
            limit=page_size
        )
        
        return [AlarmResponse.model_validate(alarm.to_dict()) for alarm in alarms]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报警列表失败: {str(e)}"
        )


@router.get("/{alarm_id}", response_model=AlarmResponse)
async def get_alarm(
    alarm_id: int,
    db: Session = Depends(get_db)
):
    """
    获取报警详情
    """
    try:
        repo = AlarmRepository(db)
        alarm = repo.get(alarm_id)
        
        if not alarm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.ALARM_NOT_FOUND
            )
        
        return AlarmResponse.model_validate(alarm.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报警详情失败: {str(e)}"
        )


@router.post("/{alarm_id}/acknowledge")
async def acknowledge_alarm(
    alarm_id: int,
    request: AlarmAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    """
    确认报警
    """
    try:
        repo = AlarmRepository(db)
        alarm = repo.acknowledge(alarm_id, request.acknowledged_by)
        
        if not alarm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.ALARM_NOT_FOUND
            )
        
        return {
            "success": True,
            "message": APIMessage.ACKNOWLEDGED,
            "alarm": AlarmResponse.model_validate(alarm.to_dict())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"确认报警失败: {str(e)}"
        )


@router.post("/{alarm_id}/resolve")
async def resolve_alarm(
    alarm_id: int,
    request: AlarmResolveRequest,
    db: Session = Depends(get_db)
):
    """
    解决报警
    """
    try:
        repo = AlarmRepository(db)
        alarm = repo.resolve(
            alarm_id,
            request.resolved_by,
            request.resolution_note
        )
        
        if not alarm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.ALARM_NOT_FOUND
            )
        
        return {
            "success": True,
            "message": APIMessage.RESOLVED,
            "alarm": AlarmResponse.model_validate(alarm.to_dict())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解决报警失败: {str(e)}"
        )


@router.post("/{alarm_id}/close")
async def close_alarm(
    alarm_id: int,
    request: AlarmCloseRequest,
    db: Session = Depends(get_db)
):
    """
    关闭报警
    """
    try:
        repo = AlarmRepository(db)
        alarm = repo.close(alarm_id)
        
        if not alarm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.ALARM_NOT_FOUND
            )
        
        return {
            "success": True,
            "message": APIMessage.CLOSED,
            "alarm": AlarmResponse.model_validate(alarm.to_dict())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"关闭报警失败: {str(e)}"
        )


@router.get("/statistics/summary", response_model=AlarmStatisticsResponse)
async def get_alarm_statistics(db: Session = Depends(get_db)):
    """
    获取报警统计信息
    """
    try:
        repo = AlarmRepository(db)
        stats = repo.get_statistics()
        
        return AlarmStatisticsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/devices/{device_id}/active", response_model=List[AlarmResponse])
async def get_device_active_alarms(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    获取设备的活跃报警
    """
    try:
        repo = AlarmRepository(db)
        alarms = repo.get_active_alarms(device_id)
        
        return [AlarmResponse.model_validate(alarm.to_dict()) for alarm in alarms]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取活跃报警失败: {str(e)}"
        )