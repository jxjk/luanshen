"""
监控数据 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ...config.database import get_db
from ...repositories.device_status_repository import DeviceStatusRepository
from ...stores.influxdb_store import InfluxDBStore
from ...api.schemas.device import (
    RealtimeDataResponse,
    HistoryDataRequest,
    HistoryDataResponse,
)
from ...api.schemas.monitoring import MonitoringStatsResponse, TimeSeriesQuery
from ...config.constants import APIMessage

router = APIRouter(prefix="/monitoring", tags=["监控数据"])


@router.get("/stats", response_model=MonitoringStatsResponse)
async def get_monitoring_stats(db: Session = Depends(get_db)):
    """
    获取监控统计信息
    """
    try:
        repo = DeviceStatusRepository(db)
        
        return MonitoringStatsResponse(
            total_devices=len(repo.get_all_latest()),
            running_devices=repo.count_by_status("RUNNING"),
            idle_devices=repo.count_by_status("IDLE"),
            alarm_devices=repo.count_by_status("ALARM"),
            maintenance_devices=repo.count_by_status("MAINTENANCE"),
            offline_devices=repo.count_by_status("OFFLINE"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/{device_id}/realtime", response_model=RealtimeDataResponse)
async def get_realtime_data(device_id: int, db: Session = Depends(get_db)):
    """
    获取设备实时监控数据
    """
    try:
        repo = DeviceStatusRepository(db)
        status = repo.get_latest(device_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessage.DEVICE_NOT_FOUND
            )
        
        status_dict = status.to_dict()
        
        return RealtimeDataResponse(
            device_id=device_id,
            status=status_dict["status"],
            coordinates={
                "x": status_dict["current_x"],
                "y": status_dict["current_y"],
                "z": status_dict["current_z"],
            },
            parameters={
                "spindle_speed": status_dict["spindle_speed"],
                "feed_rate": status_dict["feed_rate"],
                "load": status_dict["load_percent"],
            },
            sensors={},
            timestamp=status_dict["recorded_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取实时数据失败: {str(e)}"
        )


@router.post("/{device_id}/history", response_model=HistoryDataResponse)
async def get_history_data(
    device_id: int,
    request: HistoryDataRequest,
    db: Session = Depends(get_db)
):
    """
    获取设备历史监控数据
    """
    try:
        store = InfluxDBStore()
        
        # 查询 InfluxDB
        data = store.query_data(
            measurement=request.measurement,
            time_range=(request.start_time, request.end_time),
            filters={"device_id": str(device_id)},
            limit=request.limit
        )
        
        return HistoryDataResponse(
            device_id=device_id,
            measurement=request.measurement,
            data_points=data,
            count=len(data),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史数据失败: {str(e)}"
        )


@router.get("/{device_id}/timeseries")
async def get_timeseries_data(
    device_id: int,
    field: str = Query(..., description="字段名称"),
    start_time: datetime = Query(..., description="开始时间"),
    end_time: datetime = Query(..., description="结束时间"),
    aggregation: Optional[str] = Query(None, description="聚合函数: mean, max, min, sum"),
    window: Optional[str] = Query(None, description="时间窗口: 1m, 5m, 1h"),
):
    """
    获取时序数据（支持聚合）
    """
    try:
        store = InfluxDBStore()
        
        if aggregation and window:
            # 查询聚合数据
            data = store.query_aggregated(
                measurement="device_sensor_data",
                time_range=(start_time, end_time),
                window=window,
                filters={"device_id": str(device_id)},
                agg_func=aggregation
            )
        else:
            # 查询原始数据
            data = store.query_data(
                measurement="device_sensor_data",
                time_range=(start_time, end_time),
                filters={"device_id": str(device_id)},
                fields=[field]
            )
        
        return {
            "device_id": device_id,
            "field": field,
            "data": data,
            "count": len(data),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取时序数据失败: {str(e)}"
        )