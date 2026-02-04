"""
设备管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config.database import get_db
from ...repositories.device_status_repository import DeviceStatusRepository
from ...collectors.opcua_collector import get_or_create_collector, remove_collector
from ...api.schemas.device import (
    DeviceStatusResponse,
    DeviceStartRequest,
    DeviceStopRequest,
)
from ...config.constants import APIMessage

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.get("", response_model=list[DeviceStatusResponse])
async def get_all_devices_status(db: Session = Depends(get_db)):
    """
    获取所有设备的最新状态
    """
    try:
        repo = DeviceStatusRepository(db)
        statuses = repo.get_all_latest()
        return [DeviceStatusResponse.model_validate(status.to_dict()) for status in statuses]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备状态失败: {str(e)}"
        )


@router.get("/{device_id}/status", response_model=DeviceStatusResponse)
async def get_device_status(device_id: int, db: Session = Depends(get_db)):
    """
    获取指定设备的当前状态
    """
    try:
        repo = DeviceStatusRepository(db)
        status = repo.get_latest(device_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.DEVICE_NOT_FOUND
            )
        
        return DeviceStatusResponse.model_validate(status.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备状态失败: {str(e)}"
        )


@router.post("/{device_id}/start")
async def start_device_monitoring(
    device_id: int,
    request: DeviceStartRequest,
    db: Session = Depends(get_db)
):
    """
    启动设备监控
    """
    try:
        # 获取或创建采集器
        opcua_url = request.opcua_url
        collector = await get_or_create_collector(device_id, opcua_url)
        
        # 连接 OPC UA 服务器
        connected = await collector.connect()
        if not connected:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="连接 OPC UA 服务器失败"
            )
        
        # 开始采集
        await collector.start_collection()
        
        return {
            "success": True,
            "message": f"设备 {device_id} 监控已启动",
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动设备监控失败: {str(e)}"
        )


@router.post("/{device_id}/stop")
async def stop_device_monitoring(
    device_id: int,
    request: DeviceStopRequest,
    db: Session = Depends(get_db)
):
    """
    停止设备监控
    """
    try:
        # 移除采集器
        await remove_collector(device_id)
        
        return {
            "success": True,
            "message": f"设备 {device_id} 监控已停止",
            "device_id": device_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止设备监控失败: {str(e)}"
        )